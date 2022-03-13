#!/usr/bin/env python
#

from argparse import ArgumentParser
from os import getpid, environ
from sys import stderr
from time import sleep
import logging
from typing import Optional, Union
from typing_extensions import NoReturn
from urllib.parse import ParseResult, urlparse


from cexpay_support_bot.commander import Commander
from cexpay_support_bot.bots.telegram.telegram_bot import TelegramBot


def main(
	cexpay_api_key: str,
	cexpay_api_passphrase: str,
	cexpay_api_secret: str,
	bot_telegram_token: str,
	telegram_explicit_bot_name: bool,
	cexpay_api_url: Optional[str],
	cexpay_api_ca_cert_file: Optional[str],
	allowed_chats: list[str],
	cexpay_board_url: ParseResult
):
	logging.basicConfig(stream=stderr)

	main_logger: logging.Logger = logging.getLogger("main")
	main_logger.setLevel(logging.DEBUG)

	main_logger.info("Application starting ...")

	try:
		main_logger.info("Creating Commander ...")
		with Commander(
				cexpay_api_key=cexpay_api_key,
				cexpay_api_passphrase=cexpay_api_passphrase,
				cexpay_api_secret=cexpay_api_secret,
				cexpay_api_url=cexpay_api_url,
				cexpay_api_ca_cert_file = cexpay_api_ca_cert_file
		) as commander:

			with TelegramBot(commander, bot_telegram_token, telegram_explicit_bot_name, allowed_chats, cexpay_board_url) as telegram_bot:
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
	cexpay_api_url = environ.get('CEXPAY_API_URL', "https://api.cexpay.io/")
	cexpay_api_ca_cert_file = environ.get('CEXPAY_API_CA_CERTIFICATE_FILE', None)
	cexpay_board_url = urlparse(environ.get('CEXPAY_BOARD_URL', "https://board.cexpay.io/"))
	bot_telegram_token = _get_environ_variable('BOT_TELEGRAM_TOKEN', 4)
	allowed_chats_str = _get_environ_variable('BOT_TELEGRAM_ALLOWED_CHATS', 5)
	allowed_chats = allowed_chats_str.split(',')

	telegram_explicit_bot_name_raw = _get_environ_variable('BOT_TELEGRAM_EXPLICIT_NAME', 6)
	telegram_explicit_bot_name: bool
	if telegram_explicit_bot_name_raw.casefold() == "yes":
		telegram_explicit_bot_name = True
	elif telegram_explicit_bot_name_raw.casefold() == "no":
		telegram_explicit_bot_name = False
	else:
		print("A allowed value for environment variable 'BOT_TELEGRAM_EXPLICIT_NAME' is not 'yes'/'no'. '%s' wrong value" % telegram_explicit_bot_name_raw, file=sys.stderr)
		sys.exit(7)

	if (allowed_chats.count == 0):
		print("A required environment variable ALLOWED_CHATS is not set.", file=sys.stderr)
		sys.exit(8)

	# launch application loop
	main(cexpay_api_key, cexpay_api_passphrase, cexpay_api_secret, bot_telegram_token, telegram_explicit_bot_name, cexpay_api_url, cexpay_api_ca_cert_file, allowed_chats, cexpay_board_url)
