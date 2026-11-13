import asyncio
import httpx
import pytest
from app.xtream import XtreamClient, XtreamCredentials, XtreamError, normalize_channels


def test_catalog_and_authentication():
    def respond(request):
        action = request.url.params.get("action")
        if action == "get_live_categories":
            return httpx.Response(200, json=[{"category_id": "4", "category_name": "News"}])
        if action == "get_live_streams":
            return httpx.Response(200, json=[{"stream_id": 12, "name": "Test News", "category_id": "4"}])
        return httpx.Response(200, json={"user_info": {"auth": 1}})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as http:
            client = XtreamClient(XtreamCredentials("https://example.test", "user", "secret"), http)
            assert await client.authenticate() == {"authenticated": True}
            channels = normalize_channels(await client.live_streams(), await client.categories())
            assert channels == [{"id": "12", "name": "Test News", "category": "News"}]
    asyncio.run(run())


def test_rejected_credentials_do_not_leak():
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda request: httpx.Response(401, text="invalid")
        )) as http:
            client = XtreamClient(XtreamCredentials("https://example.test", "user", "secret"), http)
            with pytest.raises(XtreamError) as err:
                await client.authenticate()
            assert "secret" not in str(err.value)
    asyncio.run(run())
