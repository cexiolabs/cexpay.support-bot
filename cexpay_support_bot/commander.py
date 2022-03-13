import json
import os
from typing import Optional

from cexpay.api.v2 import ApiV2, Order

from cexpay_support_bot.model.bot_order import BotOrder

class Commander:

	def __init__(self,
		cexpay_api_key: str,
		cexpay_api_passphrase: str,
		cexpay_api_secret: str,
		cexpay_api_url: Optional[str],
		cexpay_api_ca_cert_file: Optional[str]
	) -> None:
		assert isinstance(cexpay_api_key, str)
		assert isinstance(cexpay_api_passphrase, str)
		assert isinstance(cexpay_api_secret, str)

		self._cexpay_api_client = ApiV2(
			key = cexpay_api_key,
			passphrase = cexpay_api_passphrase,
			secret = cexpay_api_secret,
			url = cexpay_api_url,
			ssl_ca_cert=cexpay_api_ca_cert_file
		)
		pass

	def __enter__(self):
		# TODO
		return self

	def __exit__(self, type, value, traceback):
		# TODO
		pass

	def order(self, variant_order_identifier: str) -> BotOrder:
		order: Order = self._cexpay_api_client.order_fetch(
			order_id = variant_order_identifier
		)
		return BotOrder(order)

	def address(self, variant_address: str) -> list[str]:
		order_ids: list[str] = self._cexpay_api_client.order_fetch_by_address(
			address = variant_address
		)
		return order_ids

	def transaction(self, variant_tx: str) -> list[str]:
		order_ids: list[str] = self._cexpay_api_client.order_fetch_by_tx(
			order_tx = variant_tx
		)
		return order_ids
