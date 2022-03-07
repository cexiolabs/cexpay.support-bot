from typing import Optional

from cexpay.api.v2 import ApiV2, NotFoundException, Order
from cexpay_support_bot.auth_talker import AuthTalker
from cexpay_support_bot.config_provider import ConfigProvider
from cexpay_support_bot.dbfacade.dbfacade import DbFacade

from cexpay_support_bot.model.bot_order import BotOrder
from cexpay_support_bot.provider_locator import ProviderLocator

class Commander:
	# def __init__(self,
	# 	cexpay_api_key: str,
	# 	cexpay_api_passphrase: str,
	# 	cexpay_api_secret: str,
	# 	cexpay_api_url: Optional[str],
	# 	cexpay_api_ca_cert_file: Optional[str]

	def __init__(
		self,
		provider_locator: ProviderLocator,
		chat_id: int
	) -> None:
		self._db_facade = provider_locator.get(DbFacade)
		config_provider: ConfigProvider = provider_locator.get(ConfigProvider)
		auth_state = self._db_facade.chat_auth_state(chat_id)
		cexpay_api_key: str = ""
		cexpay_api_passphrase: str = ""
		cexpay_api_secret: str = ""
		if auth_state != None:
			cexpay_api_key = auth_state["api_key"]
			cexpay_api_passphrase = auth_state["api_passphrase"]
			cexpay_api_secret = auth_state["api_secret"]

		self._cexpay_api_client = ApiV2(
			key = cexpay_api_key,
			passphrase = cexpay_api_passphrase,
			secret = cexpay_api_secret,
			url = config_provider.cexapi_url,
			ssl_ca_cert=config_provider.cexpay_api_ca_cert_file
		)

		pass

	def __enter__(self):
		# TODO
		return self

	def __exit__(self, type, value, traceback):
		# TODO
		pass

	def order(self, variant_order_identifier: str) -> BotOrder:
		try:
			order: Order = self._cexpay_api_client.order_fetch(
				order_id = variant_order_identifier,
				use_merchant_family = True
			)
			return BotOrder(order)
		except NotFoundException as e:
			# Look like 'variant_order_identifier' is a client order identifier
			order: Order = self._cexpay_api_client.order_fetch_by_client_id(
				client_order_id = variant_order_identifier,
				use_merchant_family = True
			)
			return BotOrder(order)

	def address(self, variant_address: str) -> list[str]:
		order_ids: list[str] = self._cexpay_api_client.order_fetch_by_address(
			address = variant_address,
			use_merchant_family = True
		)
		return order_ids

	def transaction(self, variant_tx: str) -> list[str]:
		order_ids: list[str] = self._cexpay_api_client.order_fetch_by_tx(
			order_tx = variant_tx,
			use_merchant_family = True
		)
		return order_ids

	def auth_save(self, user_id: int, chat_id: int) -> None:
		self._db_facade.add_auth_request(user_id, chat_id)

	def auth_cancel(self, user_id: int) -> None:
		self._db_facade.auth_cancel(user_id)
	
	def auth_mykey(self, user_id:int) -> str:
		auth_state = self._db_facade.user_auth_state(user_id)
		key = auth_state["api_key"]
		if key == None:
			return "api ket dose not set"
		return key

	def auth_talker(self, user_id: int) -> AuthTalker:
		auth_talker: AuthTalker = AuthTalker(self._db_facade, user_id)
		return auth_talker

