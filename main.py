import config
import telebot
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
  keyboard = types.ReplyKeyboardMarkup(row_width=2)
  button1 = types.KeyboardButton('Кнопка 1')
  button2 = types.KeyboardButton('Кнопка 2')
  keyboard.add(button1, button2)

  bot.reply_to(message, 'Привет! Я бот.', reply_markup=keyboard)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
  if message.text == 'Кнопка 1':
      bot.reply_to(message, 'Вы нажали на Кнопку 1')
  elif message.text == 'Кнопка 2':
      bot.reply_to(message, 'Вы нажали на Кнопку 2')
  else:
      bot.reply_to(message, 'Получено сообщение: ' + message.text)

bot.polling()