"""Xtream catalog client. Credentials are never included in exceptions or logs."""
from dataclasses import dataclass
from urllib.parse import urlsplit
import ipaddress
import httpx


class XtreamError(Exception):
    pass


@dataclass(frozen=True)
class XtreamCredentials:
    base_url: str
    username: str
    password: str

    def __post_init__(self):
        url = urlsplit(self.base_url)
        if url.scheme not in ("http", "https") or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError("Expected an http(s) Xtream server URL without credentials or query")
        # Provider hosts must be DNS names or globally routable IPs.
        # DNS resolution/rebinding protection is still required before deployment.
        try:
            address = ipaddress.ip_address(url.hostname)
        except ValueError:
            address = None
        if address is not None and not address.is_global:
            raise ValueError("Provider address must be public")
        if not self.username or not self.password:
            raise ValueError("Username and password are required")


class XtreamClient:
    def __init__(self, credentials: XtreamCredentials, client: httpx.AsyncClient):
        self.credentials = credentials
        self.client = client

    async def _request(self, action=None):
        params = {
            "username": self.credentials.username,
            "password": self.credentials.password,
        }
        if action:
            params["action"] = action
        try:
            response = await self.client.get(
                self.credentials.base_url.rstrip("/") + "/player_api.php",
                params=params,
                timeout=20,
                follow_redirects=False,
            )
            response.raise_for_status()
            result = response.json()
        except httpx.TimeoutException:
            raise XtreamError("Provider connection timed out") from None
        except httpx.ConnectError:
            raise XtreamError("Could not connect to provider (DNS, port, or network)") from None
        except httpx.HTTPStatusError as exc:
            raise XtreamError(f"Provider returned HTTP {exc.response.status_code}") from None
        except httpx.HTTPError:
            raise XtreamError("Provider HTTP transport failed") from None
        except ValueError:
            raise XtreamError("Provider returned invalid JSON") from None
        if not isinstance(result, (dict, list)):
            raise XtreamError("Unexpected Xtream response")
        return result

    async def authenticate(self):
        result = await self._request()
        if not isinstance(result, dict) or str(result.get("user_info", {}).get("auth", "0")) != "1":
            raise XtreamError("Xtream authentication rejected")
        return {"authenticated": True}

    async def categories(self):
        result = await self._request("get_live_categories")
        if not isinstance(result, list):
            raise XtreamError("Invalid categories response")
        return result

    async def live_streams(self):
        result = await self._request("get_live_streams")
        if not isinstance(result, list):
            raise XtreamError("Invalid live streams response")
        return result


def normalize_channels(streams, categories):
    names = {str(c.get("category_id")): str(c.get("category_name", "")) for c in categories}
    result = []
    for item in streams:
        stream_id = item.get("stream_id")
        if stream_id is None:
            continue
        result.append({
            "id": str(stream_id),
            "name": str(item.get("name") or f"Channel {stream_id}"),
            "category": names.get(str(item.get("category_id")), ""),
        })
    return result
