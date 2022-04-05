from contextvars import copy_context
from urllib.parse import quote, ParseResult
from chevron import render
from telegram import Chat, KeyboardButton, Message, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, Handler, MessageHandler, Updater, ConversationHandler
from telegram.utils.helpers import escape_markdown

from cexpay_support_bot.bots.utils import render_message
from cexpay_support_bot.commander import Commander
from cexpay_support_bot.model.bot_order import BotOrder
from cexpay_support_bot.utils import read_resource_json


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

	def __init__(self, commander: Commander, telegram_token: str, telegram_explicit_bot_name: bool, allowed_chats: list[str], cexpay_board_url: ParseResult) -> None:
		assert isinstance(commander, Commander)
		assert isinstance(telegram_token, str)
		assert isinstance(telegram_explicit_bot_name, bool)
		assert isinstance(allowed_chats, list)
		assert isinstance(cexpay_board_url, ParseResult)

		self._updater = None
		self._commander = commander
		self._telegram_token = telegram_token
		self._allowed_chats = allowed_chats
		self._telegram_explicit_bot_name = telegram_explicit_bot_name
		self._cexpay_board_url = cexpay_board_url
		pass

	def _return_start(self, update: Update, context: CallbackContext) -> int:
		try:
			message = update.message
			bot_name = message.bot.name
			text = message.text
			user_id = message.from_user.id

			args = text.split(" ")
			command = args[0]
			variant_order_identifier = args[1]

			if (self._telegram_explicit_bot_name == True):
				if not command.endswith(bot_name):
					return
			
			bot_order: BotOrder = self._commander.order(variant_order_identifier = variant_order_identifier)

			deposits_str = "Согласно ордера %s есть следующие депозиты:" % variant_order_identifier
			deposits = list()
			for depositTransaction in bot_order.depositTransactions:
				deposits_str = "%s\n%s - %s %s" % (deposits_str, depositTransaction.tx_hash, depositTransaction.amount, bot_order.fromCurrency)
				deposits.append(depositTransaction.tx_hash)

			context.user_data["deposit_return"] = dict()
			context.user_data["deposit_return"]["bot_order"] = bot_order
			keyboard = ReplyKeyboardMarkup([deposits], resize_keyboard=True)
			self._updater.bot.send_message(chat_id=user_id, text=deposits_str, reply_markup=keyboard)
		except Exception as ex:
			context.bot.send_message(
				chat_id = update.effective_chat.id,
				reply_to_message_id = message.message_id,
				text = str(ex)
			)
		pass
		return 1

	def _return_request_address(self, update: Update, context: CallbackContext) -> int:
		message = update.message
		user_id = message.from_user.id
		tx_hash = message.text
		keyboard = ReplyKeyboardRemove()
		
		context.user_data["deposit_return"]["tx_hash"] = tx_hash
		self._updater.bot.send_message(chat_id=user_id, text="Enter return address", reply_markup=keyboard)
		return 2

	def _return_save_address(self, update: Update, context: CallbackContext) -> None:
		message = update.message
		user_id = message.from_user.id
		return_address = message.text
		context.user_data["deposit_return"]["return_address"] = return_address
		bot_order = context.user_data["deposit_return"]["bot_order"]
		deposit_address = bot_order.depositAddress
		tx_hash = context.user_data["deposit_return"]["tx_hash"]
		deposit = list(filter(lambda el: el.tx_hash == tx_hash, bot_order.depositTransactions))[0]
		deposit_amount = deposit.amount
		deposit_currency = bot_order.fromCurrency

		order_id = bot_order.orderId
		client_order_id = bot_order.clientOrderId
		return_str = """Ордер: %s / %s\nАдрес депозита: %s\nХеш депозита: %s\nСумма депозита: %s %s\nАдрес возврата: %s\n\nПринят к возврату.""" % (order_id, client_order_id, deposit_address, tx_hash, deposit_amount, deposit_currency, return_address)
		self._updater.bot.send_message(chat_id=user_id, text=return_str)
		return ConversationHandler.END

	def _return_cancel(self, update: Update, context: CallbackContext) -> None:
		update.message.reply_text("Returning end")
		return ConversationHandler.END

	def __enter__(self):
		self._updater = Updater(token=self._telegram_token)

		return_conv_handler = ConversationHandler(
			entry_points= [CommandHandler('return', self._return_start)],
			states={
				1: [MessageHandler(Filters.text, self._return_request_address, pass_user_data=True)],
				2: [MessageHandler(Filters.text, self._return_save_address, pass_user_data=True)]
			},
			fallbacks=[CommandHandler("return_cancel", self._return_cancel)]
		)
		
		start_handler = CommandHandler('start', self._start)
		self._updater.dispatcher.add_handler(start_handler)

		status_handler = CommandHandler('order', self._authorize(self._order, self._allowed_chats))
		self._updater.dispatcher.add_handler(status_handler)

		orders_handler_by_tx = CommandHandler('transaction', self._authorize(self._transaction, self._allowed_chats))
		self._updater.dispatcher.add_handler(orders_handler_by_tx)

		orders_handler_by_address = CommandHandler('address', self._authorize(self._address, self._allowed_chats))
		self._updater.dispatcher.add_handler(orders_handler_by_address)

		self._updater.dispatcher.add_handler(return_conv_handler)
		# echo_handler = MessageHandler(Filters.text & (~Filters.command), self._message)
		# self._updater.dispatcher.add_handler(echo_handler)

		return self

	def __exit__(self, type, value, traceback):
		# TODO
		pass

	def idle(self) -> None:
		self._updater.start_polling()
		self._updater.idle()

	def _start(self, update: Update, context: CallbackContext) -> None:
		context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a CEX Pay Support Bot, please talk to me!")

	# def _message(self, update: Update, context: CallbackContext) -> None:
	# 	context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

	def _order(self, update: Update, context: CallbackContext) -> None:
		try:
			message = update.message
			bot_name = message.bot.name
			text = message.text

			args = text.split(" ")
			command = args[0]
			variant_order_identifier = args[1]

			if (self._telegram_explicit_bot_name == True):
				if not command.endswith(bot_name):
					return
			
			bot_order: BotOrder = self._commander.order(variant_order_identifier = variant_order_identifier)

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
			message = update.message
			bot_name = message.bot.name
			text = message.text

			args = text.split(" ")
			command = args[0]
			variant_address = args[1]

			if (self._telegram_explicit_bot_name == True):
				if not command.endswith(bot_name):
					return
			
			order_ids: list = self._commander.address(variant_address = variant_address)

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
			message = update.message
			bot_name = message.bot.name
			text = message.text

			args = text.split(" ")
			command = args[0]
			variant_tx = args[1]

			if (self._telegram_explicit_bot_name == True):
				if not command.endswith(bot_name):
					return
			
			order_ids: list = self._commander.transaction(variant_tx = variant_tx)

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

