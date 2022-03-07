from re import M

from cexpay_support_bot.dbfacade.dbfacade import DbFacade


class AuthTalker:
	def __init__(self, db_facade: DbFacade, user_id: int) -> None:
		self._db_facade = db_facade
		self._user_id = user_id
		self._question: dict = {
			"api_key": "Auth start.\nWrite API key",
			"api_passphrase": "Write API passphrase",
			"api_secret": "Write API secret"
		}
		pass

	def next_question(self) -> str:
		auth_state: dict = self._db_facade.user_auth_state(self._user_id)
		for question_key in self._question.keys():
			if (question_key not in auth_state.keys()):
				return self._question[question_key]
		return None

	def write_answer(self, answer: str) -> None:
		auth_state: dict = self._db_facade.user_auth_state(self._user_id)
		for question_key in self._question.keys():
			if (question_key not in auth_state.keys()):
				self._db_facade.set_auth_state(self._user_id, question_key, answer)
				break
