ARG BUILD_FROM
FROM $BUILD_FROM
RUN apk add --no-cache python3 py3-pip py3-virtualenv
WORKDIR /opt/xtream_orchard
COPY server/requirements.txt ./requirements.txt
RUN python3 -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt
COPY server/app ./app
COPY homeassistant/xtream_orchard/run.sh /run.sh
RUN chmod +x /run.sh
CMD ["/run.sh"]
