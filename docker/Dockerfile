ARG IMAGE=python:3.10-alpine3.15

FROM ${IMAGE} AS builder
# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
WORKDIR /stage/usr/local/cexiolabs/cexpay.support-bot
COPY requirements.txt .
COPY LICENSE .
COPY README.md .
COPY NOTICE .
COPY bin bin
COPY cexpay_support_bot cexpay_support_bot
COPY docker/docker-entrypoint.sh /stage/usr/local/bin/
# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug

FROM ${IMAGE}
COPY --from=builder /stage /
RUN \
  cd /usr/local/cexiolabs/cexpay.support-bot && \
  python3 -m venv .venv && \
  source .venv/bin/activate && \
  pip install --upgrade pip && \
  pip install --requirement requirements.txt
ENV ALLOWED_CHATS=
ENV CEXPAY_API_KEY=
ENV CEXPAY_API_PASSPHRASE=
ENV CEXPAY_API_SECRET=
ENV CEXPAY_API_URL="https://api.cexpay.io"
ENV CEXPAY_API_CA_CERTIFICATE_FILE=
ENV CEXPAY_BOARD_URL="https://board.cexpay.io"
ENV BOT_TELEGRAM_TOKEN=
ENV BOT_TELEGRAM_EXPLICIT_NAME=no
CMD [ "/usr/local/bin/docker-entrypoint.sh" ]
