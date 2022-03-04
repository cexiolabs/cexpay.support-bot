#!/bin/sh

export PYTHONPATH=/usr/local/cexiolabs/cexpay.support-bot
source /usr/local/cexiolabs/cexpay.support-bot/.venv/bin/activate
python /usr/local/cexiolabs/cexpay.support-bot/bin/cexpay_support_bot-cli.py
