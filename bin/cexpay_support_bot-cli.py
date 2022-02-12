#!/usr/bin/env python
#

from argparse import ArgumentParser
from os import getpid, environ
from sys import stderr
from time import sleep
import logging
from typing import Optional, Union
from typing_extensions import NoReturn

from cexpay_support_bot.commander import Commander
from cexpay_support_bot.bots.telegram.telegram_bot import TelegramBot

def main(cexpay_api_key: str, cexpay_api_passphrase: str, cexpay_api_secret: str, bot_telegram_token: str, cexpay_api_url: Optional[str] = None):
	logging.basicConfig(stream=stderr)

	main_logger: logging.Logger = logging.getLogger("main")
	main_logger.setLevel(logging.DEBUG)

	main_logger.info("Application starting ...")

	try:
		main_logger.info("Creating Commander ...")
		with Commander(
			cexpay_api_key = cexpay_api_key,
			cexpay_api_passphrase = cexpay_api_passphrase,
			cexpay_api_secret = cexpay_api_secret,
			cexpay_api_url = cexpay_api_url
		) as commander:

			with TelegramBot(commander, bot_telegram_token) as telegram_bot:
				main_logger.info("Entering main loop ...")
				telegram_bot.idle()

	except Exception as ex:
		# TODO
		main_logger.exception("UNEXPECTED ERROR: " + str(ex))
		raise

	main_logger.info("Main loop was interrupt. Exiting...")
	pass


def _get_environ_variable(name: str, exit_code: int) -> Union[str, NoReturn]:
	value = environ.get(name, None)
	if value is None:
		print("A required environment variable '%s' is not set." % name, file=sys.stderr)
		sys.exit(exit_code)
	return value

if __name__ == "__main__":
	import sys

	cexpay_api_key = _get_environ_variable('CEXPAY_API_KEY', 1)
	cexpay_api_passphrase = _get_environ_variable('CEXPAY_API_PASSPHRASE', 2)
	cexpay_api_secret = _get_environ_variable('CEXPAY_API_SECRET', 3)
	cexpay_api_url = environ.get('CEXPAY_API_URL', None)

	bot_telegram_token = _get_environ_variable('BOT_TELEGRAM_TOKEN', 4)

	# launch application loop
	main(cexpay_api_key, cexpay_api_passphrase, cexpay_api_secret, bot_telegram_token, cexpay_api_url)
