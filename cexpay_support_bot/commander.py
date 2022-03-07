import json
import os
from typing import Optional

from cexpay.api.v2 import ApiV2, Order

from cexpay_support_bot.model.bot_order import BotOrder

class ExplanedOrder:

	def __init__(self, order: Order) -> None:
		self._order = order
		pass

	def explain_order_key(self) -> str:
		return "%s:%s:%s" % (self._order.status, self._order.state, self._order.paid_status)

	def explain_order_template(self) -> str:
		order_explain_key = self.explain_order_key()
		filepath = os.path.join("cexpay_support_bot", "order-explanations.json")
		json_file = open(filepath)
		json_data = json.load(json_file)
		if (order_explain_key in json_data):
			return json_data[order_explain_key]
		else:
			return json_data["DEFAULT"]
	
	def explain_order_context(self) -> dict:
		order_explain_key = self.explain_order_key()
		render_context: dict = {
			'order_data': {self._order.order_id}
			}
		return render_context

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

	def order_explanation(self, variant_order_identifier: str) -> ExplanedOrder:
		order: Order = self._cexpay_api_client.order_fetch(order_id = variant_order_identifier)
		return ExplanedOrder(order)




