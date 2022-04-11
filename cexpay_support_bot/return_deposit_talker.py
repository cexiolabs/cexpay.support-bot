from re import M

from cexpay_support_bot.dbfacade.dbfacade import DbFacade


class ReturnDepositTalker:
	def __init__(self, db_facade: DbFacade, user_id: int) -> None:
		self._db_facade = db_facade
		self._user_id = user_id
		self._question: dict = {
			"message_id": "return_message_id",
			"order_id": "return_order_id",
			"deposit_hash": "return_deposit_hash",
			"return_address": "return_address"
		}
		pass

	def next_question(self) -> str:
		auth_state: dict = self._db_facade.return_deposit_state(self._user_id)
		for question_key in self._question.keys():
			if (question_key not in auth_state.keys()):
				return self._question[question_key]
		return None

	def write_answer(self, answer: str) -> None:
		auth_state: dict = self._db_facade.return_deposit_state(self._user_id)
		for question_key in self._question.keys():
			if (question_key not in auth_state.keys()):
				self._db_facade.set_return_deposit_state(self._user_id, question_key, answer)
				break

	def start(self, chat_id: int) -> None:
		self._db_facade.add_return_deposit_request(self._user_id, chat_id)

	def cancel(self) -> None:
		self._db_facade.return_deposit_cancel(self._user_id)

	def status(self) -> dict:
		return self._db_facade.return_deposit_state(self._user_id)
