class OrderStatus:
	def __init__(self,
		order_id: str,
		client_order_id: str,
		client_order_tag: str,
		status: str,
		state: str,
		deposit_address: str,
		deposit_address_expolorer_url: str,
		paid_status: str
	) -> None:
		assert isinstance(order_id, str)
		assert isinstance(client_order_id, str)
		assert client_order_tag is not None and isinstance(client_order_tag, str)
		assert isinstance(status, str)

		self._client_order_id = client_order_id
		self._order_id = order_id
		self._client_order_tag = client_order_tag
		self._status = status
		self._state = state
		self._paid_status = paid_status
		self._deposit_address = deposit_address
		self._deposit_address_expolorer_url = deposit_address_expolorer_url

	@property
	def client_order_id(self): return self._client_order_id
	@client_order_id.setter
	def client_order_id(self, value): raise AttributeError("The property 'client_order_id' is readonly and cannot be set.")
	@client_order_id.deleter
	def client_order_id(self): raise AttributeError("The property 'client_order_id' is readonly and cannot be deleted.")

	@property
	def client_order_tag(self): return self._client_order_tag
	@client_order_tag.setter
	def client_order_tag(self, value): raise AttributeError("The property 'client_order_tag' is readonly and cannot be set.")
	@client_order_tag.deleter
	def client_order_tag(self): raise AttributeError("The property 'client_order_tag' is readonly and cannot be deleted.")

	@property
	def deposit_address(self): return self._deposit_address
	@deposit_address.setter
	def deposit_address(self, value): raise AttributeError("The property 'deposit_address' is readonly and cannot be set.")
	@deposit_address.deleter
	def deposit_address(self): raise AttributeError("The property 'deposit_address' is readonly and cannot be deleted.")

	@property
	def deposit_address_expolorer_url(self): return self._deposit_address_expolorer_url
	@deposit_address_expolorer_url.setter
	def deposit_address_expolorer_url(self, value): raise AttributeError("The property 'deposit_address_expolorer_url' is readonly and cannot be set.")
	@deposit_address_expolorer_url.deleter
	def deposit_address_expolorer_url(self): raise AttributeError("The property 'deposit_address_expolorer_url' is readonly and cannot be deleted.")

	@property
	def order_id(self): return self._order_id
	@order_id.setter
	def order_id(self, value): raise AttributeError("The property 'order_id' is readonly and cannot be set.")
	@order_id.deleter
	def order_id(self): raise AttributeError("The property 'order_id' is readonly and cannot be deleted.")

	@property
	def paid_status(self): return self._paid_status
	@paid_status.setter
	def paid_status(self, value): raise AttributeError("The property 'paid_status' is readonly and cannot be set.")
	@paid_status.deleter
	def paid_status(self): raise AttributeError("The property 'paid_status' is readonly and cannot be deleted.")

	@property
	def state(self): return self._state
	@state.setter
	def state(self, value): raise AttributeError("The property 'state' is readonly and cannot be set.")
	@state.deleter
	def state(self): raise AttributeError("The property 'state' is readonly and cannot be deleted.")

	@property
	def status(self): return self._status
	@status.setter
	def status(self, value): raise AttributeError("The property 'status' is readonly and cannot be set.")
	@status.deleter
	def status(self): raise AttributeError("The property 'status' is readonly and cannot be deleted.")

