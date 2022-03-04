
### Build
docker build --tag "py_test" \
    --file docker/Dockerfile .

### Run


docker run --rm --interactive --tty \
    -e CEXPAY_API_KEY= \
    -e CEXPAY_API_PASSPHRASE= \
    -e CEXPAY_API_SECRET= \
    -e BOT_TELEGRAM_TOKEN= \
    py_test

docker run --rm --interactive --tty \
    --entrypoint /bin/bash \
    py_test
