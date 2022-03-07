import os
from chevron import render
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, Handler, MessageHandler, Updater

from cexpay_support_bot.bots.utils import render_message
from cexpay_support_bot.commander import Commander, ExplanedOrder
from cexpay_support_bot.model.bot_order import BotOrder
from cexpay_support_bot.utils import read_json_templates

class TelegramBot:

	def __init__(self, commander: Commander, telegram_token: str, telegram_explicit_bot_name: bool, allowed_chats: list[str]) -> None:
		assert isinstance(commander, Commander)
		assert isinstance(telegram_token, str)

		self._updater = None
		self._commander = commander
		self._telegram_token = telegram_token
		self._allowed_chats = allowed_chats
		self._telegram_explicit_bot_name = telegram_explicit_bot_name
		pass

	def __enter__(self):
		self._updater = Updater(token=self._telegram_token)
		
		start_handler = CommandHandler('start', self._start)
		self._updater.dispatcher.add_handler(start_handler)

		caps_handler = CommandHandler('caps', self._caps)
		self._updater.dispatcher.add_handler(caps_handler)

		status_handler = CommandHandler('order', self._verify_permission(self._order, self._allowed_chats))
		self._updater.dispatcher.add_handler(status_handler)

		echo_handler = MessageHandler(Filters.text & (~Filters.command), self._message)
		self._updater.dispatcher.add_handler(echo_handler)

		return self

	def __exit__(self, type, value, traceback):
		# TODO
		pass

	def idle(self) -> None:
		self._updater.start_polling()
		self._updater.idle()

	def _start(self, update: Update, context: CallbackContext) -> None:
		context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a CEX Pay Support Bot, please talk to me!")

	def _caps(self, update: Update, context: CallbackContext) -> None:
		text_caps = ' '.join(context.args).upper()
		context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

	def _message(self, update: Update, context: CallbackContext) -> None:
		context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

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
			
			bot_order: BotOrder = self._commander.order_status(variant_order_identifier = variant_order_identifier)
			render_context: dict = {
				"text_data": bot_order.explain_order
			}
			response_text: str = render_message(__name__, "order-accepted.mustache.txt", render_context)

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

	def _permission_denied(self, update: Update, context: CallbackContext) -> None:
		text = "Permission denied"
		context.bot.send_message(chat_id=update.effective_chat.id, text=text)

	def _verify_permission(self, handler: Handler, allowed_chats: list[str]) -> Handler:

		def permission_handler(update: Update, context: CallbackContext) -> None:
			current_chat: str = update.effective_chat.title
			if (current_chat in allowed_chats):
				handler(update, context)
			else:
				self._permission_denied(update, context)

		# (self, update: Update, allowed_chats: List[str]):
		# current_chat: str = update.effective_chat.title
		# if (not allowed_chats in allowed_chats)

		return permission_handler

