import datetime
from ipaddress import collapse_addresses
import logging
from urllib.parse import ParseResult
from pymongo import MongoClient

class DbFacade:
	AUTH_COLLECTION = "auth"

	def __init__(self, mongo_connection_uri: ParseResult, main_logger: logging.Logger) -> None:
		uri = "%s://%s:%s@%s" % (mongo_connection_uri.scheme, mongo_connection_uri.username,
								 mongo_connection_uri.password, mongo_connection_uri.hostname)
		self._main_logger = main_logger
		masked_password = "%s...%s" % (
			mongo_connection_uri.password[0], mongo_connection_uri.password[-1])
		main_logger.info("Connecting to mongo database: %s://%s:%s@%s" % (mongo_connection_uri.scheme, mongo_connection_uri.username,
																		  masked_password, mongo_connection_uri.hostname))
		client = MongoClient(uri)
		dbname = mongo_connection_uri.path
		if (dbname.startswith("/")):
			dbname = mongo_connection_uri.path[1:]
		self._db = client[dbname]
		pass

	def add_auth_request(self, user_id: int, chat_id: int) -> None:
		collection = self._db[self.AUTH_COLLECTION]
		user_state: dict = self.user_auth_state(user_id)
		if (user_state == None):
			collection.insert_one(
				{"user_id": user_id, "chat_id": chat_id, "created_at": datetime.datetime.utcnow()})

	def user_auth_state(self, user_id: int) -> dict:
		collection = self._db[self.AUTH_COLLECTION]
		auth_state: dict = collection.find_one({"user_id": user_id})
		return auth_state

	def chat_auth_state(self, chat_id: int) -> dict:
		collection = self._db[self.AUTH_COLLECTION]
		auth_state: dict = collection.find_one({"chat_id": chat_id})
		return auth_state

	def set_auth_state(self, user_id: int, key: str, value: str) -> None:
		collection = self._db[self.AUTH_COLLECTION]
		user_state: dict = self.user_auth_state(user_id)
		if (user_state != None):
			collection.find_one_and_update({"user_id": user_id}, {"$set": {key: value}})

	def auth_cancel(self, user_id: int) -> None:
		collection = self._db[self.AUTH_COLLECTION]
		collection.delete_one({"user_id": user_id})
