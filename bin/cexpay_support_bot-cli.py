#!/usr/bin/env python
#

from distutils.command.config import config
from os import environ
from sys import stderr
import logging
from typing import Optional, Union
from typing_extensions import NoReturn
from urllib.parse import ParseResult, urlparse
from cexpay_support_bot.auth_talker import AuthTalker


from cexpay_support_bot.commander import Commander
from cexpay_support_bot.bots.telegram.telegram_bot import TelegramBot
from cexpay_support_bot.config_provider import ConfigProvider
from cexpay_support_bot.dbfacade.dbfacade import DbFacade
from cexpay_support_bot.provider_locator import ProviderLocator
from cexpay_support_bot.return_deposit_talker import ReturnDepositTalker


def main(
	bot_telegram_token: str,
	telegram_explicit_bot_name: bool,
	mongo_connection_uri: str,
	cexpay_api_v2_url: Optional[str],
	cexpay_api_v3_url: Optional[str],
	cexpay_api_ca_cert_file: Optional[str],
	allowed_chats: list[str],
	cexpay_board_url: ParseResult
):
	logging.basicConfig(stream=stderr)
	main_logger: logging.Logger = logging.getLogger("main")
	main_logger.setLevel(logging.DEBUG)

	provider_locator = ProviderLocator.getDefault()

	config_provider = ConfigProvider()
	config_provider.allowed_chats = allowed_chats
	config_provider.bot_telegram_token = bot_telegram_token
	config_provider.cexapi_v2_url = cexpay_api_v2_url
	config_provider.cexapi_v3_url = cexpay_api_v3_url
	config_provider.cexpay_api_ca_cert_file = cexpay_api_ca_cert_file
	config_provider.mongo_connection_string = mongo_connection_uri
	config_provider.telegram_explicit_bot_name = telegram_explicit_bot_name
	config_provider.cexpay_board_url = cexpay_board_url
	config_provider.talkers = [AuthTalker, ReturnDepositTalker]

	provider_locator.register(ConfigProvider, config_provider)
	provider_locator.register(logging.Logger, main_logger)
	provider_locator.register(DbFacade, DbFacade(mongo_connection_uri, main_logger))

	main_logger.info("Application starting ...")

	try:
		main_logger.info("Creating Commander ...")
		with TelegramBot(provider_locator) as telegram_bot:
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

	cexpay_api_v2_url = environ.get('CEXPAY_API_V2_URL', "https://api.cexpay.io/")
	cexpay_api_v3_url = environ.get('CEXPAY_API_V3_URL', "https://api.cexpay.io/")
	cexpay_api_ca_cert_file = environ.get('CEXPAY_API_CA_CERTIFICATE_FILE', None)
	cexpay_board_url = urlparse(environ.get('CEXPAY_BOARD_URL', "https://board.cexpay.io/"))
	bot_telegram_token = _get_environ_variable('BOT_TELEGRAM_TOKEN', 4)
	allowed_chats_str = _get_environ_variable('BOT_TELEGRAM_ALLOWED_CHATS', 5)
	allowed_chats = allowed_chats_str.split(',')
	if (allowed_chats.count == 0):
		print("A required environment variable BOT_TELEGRAM_ALLOWED_CHATS is not set.", file=sys.stderr)
		sys.exit(8)

	telegram_explicit_bot_name_raw = _get_environ_variable('BOT_TELEGRAM_EXPLICIT_NAME', 6)
	telegram_explicit_bot_name: bool
	if telegram_explicit_bot_name_raw.casefold() == "yes":
		telegram_explicit_bot_name = True
	elif telegram_explicit_bot_name_raw.casefold() == "no":
		telegram_explicit_bot_name = False
	else:
		print("A allowed value for environment variable 'BOT_TELEGRAM_EXPLICIT_NAME' is not 'yes'/'no'. '%s' wrong value" % telegram_explicit_bot_name_raw, file=sys.stderr)
		sys.exit(7)

	mongo_connection_str = _get_environ_variable("MONGO_CONNECTION_STRING", 9)
	mongo_connection_uri = urlparse(mongo_connection_str)

	# launch application loop
	main(bot_telegram_token, telegram_explicit_bot_name, mongo_connection_uri, cexpay_api_v2_url, cexpay_api_v3_url, cexpay_api_ca_cert_file, allowed_chats, cexpay_board_url)
