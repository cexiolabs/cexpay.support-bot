from email.policy import default
from typing import Any
from cexpay_support_bot.dbfacade.dbfacade import DbFacade

class ProviderLocator:
	__instance = None
	@classmethod
	def getDefault(cls):
		if cls.__instance == None:
			cls.__instance = DefaultProviderLocator()
		return cls.__instance
	
	def get(self, cls) -> Any:
		raise Exception("Abstract method")

class DefaultProviderLocator(ProviderLocator):
	def __init__(self) -> None:
		super().__init__()
		self._instances = {}

	def register(self, cls, instance):
		if cls in self._instances:
			raise Exception("Class %s already registred" % str(cls))
		self._instances[cls] = instance

	def get(self, cls):
		if cls in self._instances:
			return self._instances[cls]
		raise Exception("Required type error: %d" % str(cls))
