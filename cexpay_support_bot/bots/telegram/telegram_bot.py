from urllib.parse import quote, ParseResult
from telegram import Chat, Message, ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, Handler, MessageHandler, Updater
from telegram.utils.helpers import escape_markdown

from cexpay_support_bot.bots.utils import render_message
from cexpay_support_bot.commander import Commander
from cexpay_support_bot.config_provider import ConfigProvider
from cexpay_support_bot.model.bot_order import BotOrder
from cexpay_support_bot.provider_locator import ProviderLocator

class _TelegramMarkdownWrap:
	def __init__(self, wrap) -> None:
		assert not isinstance(wrap, dict)
		assert not isinstance(wrap, list)
		self._wrap = wrap

	def __getattr__(self, attr):
		thing = getattr(self._wrap, attr)
		if isinstance(thing, list): return [_TelegramMarkdownWrap(x) for x in thing]
		if isinstance(thing, dict): return map(lambda key: _TelegramMarkdownWrap(thing[key]), thing.keys())
		return _TelegramMarkdownWrap(thing)

	def __str__(self) -> str:
		return escape_markdown(str(self._wrap))

class _TelegramOrderReference:
	def __init__(self, cexpay_board_url: ParseResult, order_id: str) -> None:
		self.orderId = order_id
		encoded_order_id = quote(order_id, safe="")
		self.orderReferenceUrl = "%s://%s/yong/order/%s" % (cexpay_board_url.scheme, cexpay_board_url.hostname, encoded_order_id)

class TelegramBot:

	def __init__(self, provider_locator: ProviderLocator) -> None:
		self._updater = None
		self._provider_locator = provider_locator
		config_provider: ConfigProvider = provider_locator.get(ConfigProvider)
		self._updater = None
		self._telegram_token = config_provider.bot_telegram_token
		self._telegram_explicit_bot_name = config_provider.telegram_explicit_bot_name
		self._allowed_chats = config_provider.allowed_chats
		self._cexpay_board_url = config_provider.cexpay_board_url
		# assert isinstance(commander, Commander)
		assert isinstance(self._telegram_token, str)
		assert isinstance(self._telegram_explicit_bot_name, bool)
		assert isinstance(self._allowed_chats, list)
		assert isinstance(self._cexpay_board_url, ParseResult)

		pass

	def __enter__(self):
		self._updater = Updater(token=self._telegram_token)
		
		auth_handler = CommandHandler('auth', self._auth)
		self._updater.dispatcher.add_handler(auth_handler)

		auth_cancel_handler = CommandHandler('authcancel', self._auth_cancel)
		self._updater.dispatcher.add_handler(auth_cancel_handler)

		auth_mykey_handler = CommandHandler('mykey', self._auth_mykey)
		self._updater.dispatcher.add_handler(auth_mykey_handler)

		start_handler = CommandHandler('start', self._start)
		self._updater.dispatcher.add_handler(start_handler)

		status_handler = CommandHandler('order', self._authorize(self._order, self._allowed_chats))
		self._updater.dispatcher.add_handler(status_handler)

		orders_handler_by_tx = CommandHandler('transaction', self._authorize(self._transaction, self._allowed_chats))
		self._updater.dispatcher.add_handler(orders_handler_by_tx)

		orders_handler_by_address = CommandHandler('address', self._authorize(self._address, self._allowed_chats))
		self._updater.dispatcher.add_handler(orders_handler_by_address)

		# echo_handler = MessageHandler(Filters.text & (~Filters.command), self._message)
		# self._updater.dispatcher.add_handler(echo_handler)

		return self

	def __exit__(self, type, value, traceback):
		# TODO
		pass

	def idle(self) -> None:
		self._updater.start_polling()
		self._updater.idle()

	def _auth(self, update: Update, context: CallbackContext) -> None:
		user_id = update.effective_user.id
		chat_id = update.effective_chat.id
		commander = Commander(self._provider_locator, chat_id)
		commander.auth_save(user_id, chat_id)
		if (user_id == chat_id):
			# User write direct message to bot
			next_question = commander.auth_talker(user_id).next_question()
			context.bot.send_message(chat_id = update.effective_chat.id, text = next_question)
		else:
			# User write message to bot in public chat
			context.bot.send_message(
				reply_to_message_id = update.message.message_id,
				chat_id = update.effective_chat.id,
				text = "To start auth, please talk direct to me!")

	def _auth_cancel(self, update: Update, context: CallbackContext) -> None:
		user_id = update.effective_user.id
		chat_id = update.effective_chat.id
		commander = Commander(self._provider_locator, chat_id)
		if (user_id == chat_id):
			# User write direct message to bot
			commander.auth_cancel(user_id)
			context.bot.send_message(chat_id = update.effective_chat.id, text = "Auth canceled")
	
	def _auth_mykey(self, update: Update, context: CallbackContext) -> None:
		user_id = update.effective_user.id
		chat_id = update.effective_chat.id
		commander = Commander(self._provider_locator, chat_id)
		if (user_id == chat_id):
			# User write direct message to bot
			my_key = commander.auth_mykey(user_id)
			context.bot.send_message(chat_id = update.effective_chat.id, text = "Used key:\n%s" % my_key)

	def _start(self, update: Update, context: CallbackContext) -> None:
		context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a CEX Pay Support Bot, please talk to me!")

	def _message(self, update: Update, context: CallbackContext) -> None:
		user_id = update.effective_user.id
		chat_id = update.effective_chat.id
		commander = Commander(self._provider_locator, chat_id)
		if (user_id == chat_id):
			# User write direct message to bot
			commander.auth_talker(user_id).write_answer(update.message.text)
			next_question = commander.auth_talker(user_id).next_question()
			if (next_question != None):
				context.bot.send_message(chat_id = update.effective_chat.id, text = next_question)
			else:
				context.bot.send_message(chat_id = update.effective_chat.id, text = "Done")
		else:
			context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

	def _order(self, update: Update, context: CallbackContext) -> None:
		chat_id = update.effective_chat.id
		commander = Commander(self._provider_locator, chat_id)
		try:
			commander = Commander(self._provider_locator, update.effective_chat.id)
			message = update.message
			bot_name = message.bot.name
			text = message.text

			args = text.split(" ")
			command = args[0]
			variant_order_identifier = args[1]

			if (self._telegram_explicit_bot_name == True):
				if not command.endswith(bot_name):
					return
			
			bot_order: BotOrder = commander.order_status(variant_order_identifier = variant_order_identifier)
			render_context: dict = {
				"input": _TelegramMarkdownWrap(variant_order_identifier),
				"order": _TelegramMarkdownWrap(bot_order),
				"orderReferenceUrl": _TelegramOrderReference(self._cexpay_board_url, bot_order.orderId).orderReferenceUrl
			}

			response_text: str = render_message(__name__, "order.mustache.txt", render_context)

			context.bot.send_message(
				chat_id = update.effective_chat.id,
				reply_to_message_id = message.message_id,
				text = response_text,
				parse_mode = ParseMode.MARKDOWN
			)
		except Exception as ex:
			context.bot.send_message(
				chat_id = update.effective_chat.id,
				reply_to_message_id = message.message_id,
				text = str(ex)
			)
		pass

	def _address(self, update: Update, context: CallbackContext) -> None:
		try:
			commander = Commander(self._provider_locator, update.effective_chat.id)
			message = update.message
			bot_name = message.bot.name
			text = message.text

			args = text.split(" ")
			command = args[0]
			variant_address = args[1]

			if (self._telegram_explicit_bot_name == True):
				if not command.endswith(bot_name):
					return
			
			order_ids: list = commander.address(variant_address = variant_address)

			render_context: dict = {
				"input": _TelegramMarkdownWrap(variant_address),
				"orders": [_TelegramMarkdownWrap(_TelegramOrderReference(self._cexpay_board_url, x)) for x in order_ids],
				"isUsed": len(order_ids) > 0
			}

			response_text: str = render_message(__name__, "address.mustache.txt", render_context)

			context.bot.send_message(
				chat_id = update.effective_chat.id,
				reply_to_message_id = message.message_id,
				text = response_text,
				parse_mode = ParseMode.MARKDOWN
			)
		except Exception as ex:
			context.bot.send_message(
				chat_id = update.effective_chat.id,
				reply_to_message_id = message.message_id,
				text = str(ex)
			)
		pass

	def _transaction(self, update: Update, context: CallbackContext) -> None:
		try:
			commander = Commander(self._provider_locator, update.effective_chat.id)
			message = update.message
			bot_name = message.bot.name
			text = message.text

			args = text.split(" ")
			command = args[0]
			variant_tx = args[1]

			if (self._telegram_explicit_bot_name == True):
				if not command.endswith(bot_name):
					return
			
			order_ids: list = commander.transaction(variant_tx = variant_tx)

			render_context: dict = {
				"input": _TelegramMarkdownWrap(variant_tx),
				"orders": [_TelegramMarkdownWrap(_TelegramOrderReference(self._cexpay_board_url, x)) for x in order_ids],
				"isUsed": len(order_ids) > 0
			}

			response_text: str = render_message(__name__, "transaction.mustache.txt", render_context)

			context.bot.send_message(
				chat_id = update.effective_chat.id,
				reply_to_message_id = message.message_id,
				text = response_text,
				parse_mode = ParseMode.MARKDOWN
			)
		except Exception as ex:
			context.bot.send_message(
				chat_id = update.effective_chat.id,
				reply_to_message_id = message.message_id,
				text = str(ex)
			)
		pass

	def _authorize(self, handler: Handler, allowed_chats: list[str]) -> Handler:

		def authorize_handler(update: Update, context: CallbackContext) -> None:
			effective_chat: Chat = update.effective_chat
			current_chat: str = effective_chat.title
			if (effective_chat.type == Chat.PRIVATE or (current_chat is not None and current_chat in allowed_chats)):
				handler(update, context)
			else:
				message: Message = update.message
				context.bot.send_message(
					chat_id = update.effective_chat.id,
					reply_to_message_id = message.message_id,
					text = "Forbidden. Did your authorize?",
					parse_mode = ParseMode.MARKDOWN
				)

		return authorize_handler

