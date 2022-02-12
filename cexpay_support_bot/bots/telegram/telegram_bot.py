from telegram import ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

from cexpay_support_bot.bots.utils import render_message
from cexpay_support_bot.commander import Commander
from cexpay_support_bot.model.order_status import OrderStatus

class TelegramBot:

	def __init__(self, commander: Commander, telegram_token: str) -> None:
		assert isinstance(commander, Commander)
		assert isinstance(telegram_token, str)

		self._updater = None
		self._commander = commander
		self._telegram_token = telegram_token
		pass

	def __enter__(self):
		self._updater = Updater(token=self._telegram_token)
		
		start_handler = CommandHandler('start', self._start)
		self._updater.dispatcher.add_handler(start_handler)

		caps_handler = CommandHandler('caps', self._caps)
		self._updater.dispatcher.add_handler(caps_handler)

		status_handler = CommandHandler('order', self._order)
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

	def _start(self, update: Update, context: CallbackContext):
		context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a CEX Pay Support Bot, please talk to me!")

	def _caps(self, update: Update, context: CallbackContext):
		text_caps = ' '.join(context.args).upper()
		context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)

	def _message(self, update: Update, context: CallbackContext):
		context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

	def _order(self, update: Update, context: CallbackContext):
		try:
			text = update.message.text
			args = text.split(" ")
			variant_order_identifier = args[1]

			order_status: OrderStatus = self._commander.order_status(variant_order_identifier = variant_order_identifier)

			render_context: dict = {
				"input": variant_order_identifier,
				"order_data": order_status
			}

			response_text: str = render_message(__name__, "order-accepted.mustache.txt", render_context)

			context.bot.send_message(chat_id=update.effective_chat.id, text=response_text, parse_mode = ParseMode.MARKDOWN)
		except Exception as ex:
			context.bot.send_message(chat_id=update.effective_chat.id, text=str(ex))
		pass
