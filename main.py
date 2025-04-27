import telebot
import config
from db.database import create_table
from handlers import commands, notes, callbacks
from utils.notifier import Notifier
from utils.time_parser import TimeParser

bot = telebot.TeleBot(config.TOKEN)
parser = TimeParser()
notifier = Notifier(bot)
notifier.start()

create_table()

commands.register_handlers(bot)
notes.register_handlers(bot)
callbacks.register_callbacks(bot)

bot.remove_webhook()
bot.infinity_polling()
