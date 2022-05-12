import functools
import os
from chevron import render

from cexpay_support_bot.utils import read_resource_json
from cexpay.api.v2 import Order

class BotOrder:
	def __init__(self, api_order_v2: Order) -> None:
		assert isinstance(api_order_v2, Order)
		self._api_order_v2 = api_order_v2

		# Hardcoded values
		self._language = "ru"

	@property
	def explain(self) -> str:
		order_explain_key: str = "STATUS_%s:STATE_%s:PAID_%s" % (self.status, self.state, self.paidStatus)
		json_data: dict = read_resource_json(os.path.join("order-explanations.json"))
		if (order_explain_key in json_data):
			explanation_template = json_data[order_explain_key][self._language]
		else:
			explanation_template = json_data["DEFAULT"][self._language]
		explained_text = render(explanation_template, self)
		return explained_text
	@explain.setter
	def explain(self, value): raise AttributeError("The property 'explain_order' is readonly and cannot be set.")
	@explain.deleter
	def explain(self): raise AttributeError("The property 'explain_order' is readonly and cannot be deleted.")

	@property
	def clientOrderId(self): return self._api_order_v2.client_order_id
	@clientOrderId.setter
	def clientOrderId(self, value): raise AttributeError("The property 'client_order_id' is readonly and cannot be set.")
	@clientOrderId.deleter
	def clientOrderId(self): raise AttributeError("The property 'client_order_id' is readonly and cannot be deleted.")

	@property
	def clientOrderTag(self): return self._api_order_v2.client_order_tag
	@clientOrderTag.setter
	def clientOrderTag(self, value): raise AttributeError("The property 'client_order_tag' is readonly and cannot be set.")
	@clientOrderTag.deleter
	def clientOrderTag(self): raise AttributeError("The property 'client_order_tag' is readonly and cannot be deleted.")

	@property
	def createdAt(self): return self._api_order_v2.created_at
	@createdAt.setter
	def createdAt(self, value): raise AttributeError("The property 'createdAt' is readonly and cannot be set.")
	@createdAt.deleter
	def createdAt(self): raise AttributeError("The property 'createdAt' is readonly and cannot be deleted.")

	@property
	def depositAddress(self): return self._api_order_v2.deposit.address
	@depositAddress.setter
	def depositAddress(self, value): raise AttributeError("The property 'depositAddress' is readonly and cannot be set.")
	@depositAddress.deleter
	def depositAddress(self): raise AttributeError("The property 'depositAddress' is readonly and cannot be deleted.")

	@property
	def depositAddressExplorerUrl(self): return self._api_order_v2.deposit.address_explorer_url
	@depositAddressExplorerUrl.setter
	def depositAddressExplorerUrl(self, value): raise AttributeError("The property 'depositAddressExplorerUrl' is readonly and cannot be set.")
	@depositAddressExplorerUrl.deleter
	def depositAddressExplorerUrl(self): raise AttributeError("The property 'depositAddressExplorerUrl' is readonly and cannot be deleted.")

	@property
	def depositRemainAmount(self): return self._api_order_v2.deposit.remain_amount
	@depositRemainAmount.setter
	def depositRemainAmount(self, value): raise AttributeError("The property 'depositRemainAmount' is readonly and cannot be set.")
	@depositRemainAmount.deleter
	def depositRemainAmount(self): raise AttributeError("The property 'depositRemainAmount' is readonly and cannot be deleted.")

	@property
	def depositTransactions(self): return self._api_order_v2.deposit.transactions
	@depositTransactions.setter
	def depositTransactions(self, value): raise AttributeError("The property 'depositTransactions' is readonly and cannot be set.")
	@depositTransactions.deleter
	def depositTransactions(self): raise AttributeError("The property 'depositTransactions' is readonly and cannot be deleted.")

	@property
	def expiredAt(self): return self._api_order_v2.expired_at
	@expiredAt.setter
	def expiredAt(self, value): raise AttributeError("The property 'expiredAt' is readonly and cannot be set.")
	@expiredAt.deleter
	def expiredAt(self): raise AttributeError("The property 'expiredAt' is readonly and cannot be deleted.")

	@property
	def fromAmount(self): return getattr(self._api_order_v2, "from").amount
	@fromAmount.setter
	def fromAmount(self, value): raise AttributeError("The property 'fromAmount' is readonly and cannot be set.")
	@fromAmount.deleter
	def fromAmount(self): raise AttributeError("The property 'fromAmount' is readonly and cannot be deleted.")

	@property
	def fromCurrency(self): return getattr(self._api_order_v2, "from").currency
	@fromCurrency.setter
	def fromCurrency(self, value): raise AttributeError("The property 'fromCurrency' is readonly and cannot be set.")
	@fromCurrency.deleter
	def fromCurrency(self): raise AttributeError("The property 'fromCurrency' is readonly and cannot be deleted.")

	@property
	def toAmount(self): return getattr(self._api_order_v2, "to").amount
	@toAmount.setter
	def toAmount(self, value): raise AttributeError("The property 'toAmount' is readonly and cannot be set.")
	@toAmount.deleter
	def toAmount(self): raise AttributeError("The property 'toAmount' is readonly and cannot be deleted.")

	@property
	def toCurrency(self): return getattr(self._api_order_v2, "to").currency
	@toCurrency.setter
	def toCurrency(self, value): raise AttributeError("The property 'toCurrency' is readonly and cannot be set.")
	@toCurrency.deleter
	def toCurrency(self): raise AttributeError("The property 'toCurrency' is readonly and cannot be deleted.")


	@property
	def orderId(self): return self._api_order_v2.order_id
	@orderId.setter
	def orderId(self, value): raise AttributeError("The property 'orderId' is readonly and cannot be set.")
	@orderId.deleter
	def orderId(self): raise AttributeError("The property 'orderId' is readonly and cannot be deleted.")

	@property
	def paidAmount(self): return self._api_order_v2.deposit.paid_amount
	@paidAmount.setter
	def paidAmount(self, value): raise AttributeError("The property 'paidAmount' is readonly and cannot be set.")
	@paidAmount.deleter
	def paidAmount(self): raise AttributeError("The property 'paidAmount' is readonly and cannot be deleted.")

	@property
	def paidAt(self):
		latest_transaction = functools.reduce(lambda a, b: a if a.created_at > b.created_at else b, self._api_order_v2.deposit.transactions)
		return latest_transaction.created_at
	@paidAt.setter
	def paidAt(self, value): raise AttributeError("The property 'paidAt' is readonly and cannot be set.")
	@paidAt.deleter
	def paidAt(self): raise AttributeError("The property 'paidAt' is readonly and cannot be deleted.")

	@property
	def paidStatus(self):
		if self._api_order_v2.paid_status == 'NONE':
			return 'NONE'
		elif self._api_order_v2.paid_status == 'PARTLY_PAID':
			return 'PARTLY'
		elif self._api_order_v2.paid_status == 'PAID':
			return 'EXACT'
		elif self._api_order_v2.paid_status == 'OVER_PAID':
			return 'OVER'
		else:
			raise Exception("Data corrupt. Not expected order paid status: '%s'" % self._paid_status)
	@paidStatus.setter
	def paidStatus(self, value): raise AttributeError("The property 'paidStatus' is readonly and cannot be set.")
	@paidStatus.deleter
	def paidStatus(self): raise AttributeError("The property 'paidStatus' is readonly and cannot be deleted.")

	@property
	def state(self): return self._api_order_v2.state
	@state.setter
	def state(self, value): raise AttributeError("The property 'state' is readonly and cannot be set.")
	@state.deleter
	def state(self): raise AttributeError("The property 'state' is readonly and cannot be deleted.")

	@property
	def status(self): return self._api_order_v2.status
	@status.setter
	def status(self, value): raise AttributeError("The property 'status' is readonly and cannot be set.")
	@status.deleter
	def status(self): raise AttributeError("The property 'status' is readonly and cannot be deleted.")

	@property
	def updatedAt(self): return self._api_order_v2.updated_at
	@updatedAt.setter
	def updatedAt(self, value): raise AttributeError("The property 'updatedAt' is readonly and cannot be set.")
	@updatedAt.deleter
	def updatedAt(self): raise AttributeError("The property 'updatedAt' is readonly and cannot be deleted.")
