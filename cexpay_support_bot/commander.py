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
		cexpay_api_url: Optional[str]
	) -> None:
		assert isinstance(cexpay_api_key, str)
		assert isinstance(cexpay_api_passphrase, str)
		assert isinstance(cexpay_api_secret, str)

		self._cexpay_api_client = ApiV2(
			key = cexpay_api_key,
			passphrase = cexpay_api_passphrase,
			secret = cexpay_api_secret,
			url = cexpay_api_url
		)
		pass

	def __enter__(self):
		# TODO
		return self

	def __exit__(self, type, value, traceback):
		# TODO
		pass


	def order_status(self, variant_order_identifier: str) -> BotOrder:

		# TODO: implement method

		order: Order = self._cexpay_api_client.order_fetch(
			order_id = variant_order_identifier
		)

		return BotOrder(
			order_id = order.order_id,
			client_order_id = order.client_order_id,
			client_order_tag = order.client_order_tag,
			status = order.status,
			state = order.state,
			paid_amount = order.deposit["paidAmount"],
			paid_status = order.paid_status,
			deposit_address = order.deposit["address"],
			deposit_address_expolorer_url = order.deposit["addressExplorerUrl"],
		)

	def order_status_by_address(self, variant_address: str) -> BotOrder:
		orders: list = self._cexpay_api_client.order_fetch_by_address(
			address = variant_address
		)
		return orders

	def order_status_by_tx(self, variant_order_tx: str) -> BotOrder:
		orders: list = self._cexpay_api_client.order_fetch_by_tx(
			order_tx = variant_order_tx
		)
		return orders
