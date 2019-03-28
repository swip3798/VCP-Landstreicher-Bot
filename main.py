from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import platform
from LunaDB import LunaDB
import sys
from dispatcher_plugin import AdvancedDispatcher
from event import EventLoop
from datetime import datetime
import uuid
import hashlib

# Enable logging
logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()

fileHandler = logging.FileHandler("{0}/{1}.log".format("logs/", "bot"))
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(logging.INFO)
# All constants
from sensitive import *
weekdays = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"]

class VCPBot():

	#Command methods

	def echo(self, bot, update):
		"""Echo the user message."""
		update.message.reply_text(update.message.text)

	def error(self, bot, update, error):
		"""Log Errors caused by Updates."""
		logger.warning('Update "%s" caused error "%s"', update, error)
	
	def add_event(self, bot, update, args):
		logger.info("New event set")
		now = datetime.now()
		date = args[0]
		time = args[1]
		message = " ".join(args[2:])
		if date in weekdays:
			pass
		elif date[-1] == ".":
			date += now.year
		timestamp = datetime.strptime(date + " " + time, "%d.%m.%y %H:%M").timestamp()
		self.events.insert({
			"id": str(uuid.uuid1()),
			"timestamp": int(timestamp),
			"chat_id": int(update.message.chat.id),
			"message": message,
			"preremember": False
		})
		update.message.reply_text("Termin ist vorgemerkt!")

	def register(self, bot, update, args):
		
		logger.info("Register attempt by " + update.message.from_user.first_name)
		if hashlib.sha512(args[0].encode("utf-8")).hexdigest().upper() == PASSWORD_HASH:
			self.chat.upsert({
				"chat_id": update.message.chat.id,
				"registered": True
			})
			update.message.reply_text("Du bist jetzt registriert!")
		else:
			self.chat.insert({
				"chat_id": update.message.chat.id,
				"registered": False
			}, strict=False)
		

		

		

		

	# Internal methods

	def _preprocessor(self, update):
		try:
			text = update.message.text
		except:
			text = ""
		logger.info("New message from " + str(update.message.from_user.first_name) + " in chat " + str(update.message.chat.id) + ": " + text)
		if update.message.chat.id in GROUP_CHATS.values() or update.message.chat.id == ADMIN:
			return True
		elif len(self.chat.search(lambda x: x["chat_id"] == update.message.chat.id and x["registered"])) > 0:
			return True
		return text.find("/register") != -1

	def send_message(self, chat_id, message):
		logger.info("Bot send message to chat " + chat_id + " with message: " + message)
		self.bot.send_message(chat_id, message, parse_mode = "HTML")

	def send_to_main_group(self, message):
		logger.info("Bot send message to main group with message: " + message)
		self.bot.send_message(GROUP_CHATS["main"], message, parse_mode = "HTML")

	def start_bot(self):
		# Start the Bot
		if platform.system() == "Linux":
			logger.info("Start bot with webhook...")
			self.updater.start_webhook(listen='194.55.14.167',
							port=8443,
							url_path=TOKEN,
							key='private.key',
							cert='cert.pem',
							webhook_url='https://194.55.14.167:8443/' + TOKEN)
		else:
			self.updater.start_polling()

		logger.info("Start event loop...")
		self.eventloop = EventLoop(self.events, self.bot, logger, wait_time=10)
		self.eventloop.run()
		self.updater.stop()

	def __init__(self):
		logger.info("Initializing system...")
		logger.info("Loading database...")
		self.db = LunaDB("vcp")
		self.chat = self.db.table("chat", id_field="id")
		self.events = self.db.table("events", id_field="id")
		logger.info("Initialize bot...")
		"""Start the bot."""
		# Create the EventHandler and pass it your bot's token.
		self.updater = Updater(TOKEN)
		self.bot = self.updater.bot

		# Load in plugin for advanced dispatcher
		self.updater.dispatcher = AdvancedDispatcher(self.updater.bot, self.updater.dispatcher.update_queue)
		self.updater.dispatcher.preprocessor = self._preprocessor

		# Get the dispatcher to register handlers
		self.dispatcher = self.updater.dispatcher

		# on different commands - answer in Telegram
		self.dispatcher.add_handler(CommandHandler("termin", self.add_event, pass_args=True))
		self.dispatcher.add_handler(CommandHandler("register", self.register, pass_args=True))
		# self.dispatcher.add_handler(CommandHandler("start", start))
		# self.dispatcher.add_handler(CommandHandler("help", help))

		# on noncommand i.e message - echo the message on Telegram
		self.dispatcher.add_handler(MessageHandler(Filters.text, self.echo))

		# log all errors
		self.dispatcher.add_error_handler(self.error)

if __name__ == "__main__":
	vcp = VCPBot()
	vcp.start_bot()