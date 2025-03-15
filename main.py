import config
import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    conection = sqlite3.connect('schedulerbot.sql')
    cursor = conection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (id int auto_increment PRIMARY KEY, name varchar(50))')
    conection.commit()
    cursor.close()
    conection.close()

    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Кнопка 1')
    button2 = types.KeyboardButton('Кнопка 2')
    keyboard.add(button1, button2)

    bot.reply_to(message, 'Привет! Я бот.', reply_markup=keyboard)

def get_username(message):
    name = message.text.strip()
    conection = sqlite3.connect('schedulerbot.sql')
    cursor = conection.cursor()
    cursor.execute(f'INSERT INTO users (name) VALUES ({name})')
    conection.commit()
    cursor.close()
    conection.close()

@bot.message_handler(func=lambda message: True)
def handle_message(message):
  if message.text == 'Кнопка 1':
      bot.reply_to(message, 'Вы нажали на Кнопку 1')
  elif message.text == 'Кнопка 2':
      bot.reply_to(message, 'Вы нажали на Кнопку 2')
  else:
      bot.reply_to(message, 'Получено сообщение: ' + message.text)

bot.polling()