import config
import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    connect = sqlite3.connect('schedulerbot.db')
    cursor = connect.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS notes('
                   'id int auto_increment PRIMARY KEY, '
                   'user_id varchar(50),'
                   'note_text varchar(50))'
                   )
    connect.commit()
    cursor.close()
    connect.close()

    keyboard = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Добавить заметку')
    button2 = types.KeyboardButton('Удалить заметку')
    keyboard.add(button1, button2)
    bot.reply_to(message, 'Привет! Выберите действие:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Добавить заметку')
def add_note_request(message):
    msg = bot.reply_to(message, 'Введите текст заметки:')
    bot.register_next_step_handler(msg, save_note)

def save_note(message):
    connect = sqlite3.connect('schedulerbot.db')
    cursor = connect.cursor()
    cursor.execute('INSERT INTO notes (user_id, note_text) VALUES (?, ?)', (str(message.chat.id), message.text))
    connect.commit()
    cursor.close()
    connect.close()
    bot.reply_to(message, 'Заметка сохранена!')

@bot.message_handler(func=lambda message: message.text == 'Удалить заметку')
def delete_note_request(message):
    connect = sqlite3.connect('schedulerbot.db')
    cursor = connect.cursor()
    cursor.execute('SELECT id, note_text FROM notes WHERE user_id = ?', (str(message.chat.id),))
    notes = cursor.fetchall()
    cursor.close()
    connect.close()

    if not notes:
        bot.reply_to(message, 'У вас нет сохраненных заметок.')
        return

    keyboard = types.InlineKeyboardMarkup()
    for note in notes:
        button = types.InlineKeyboardButton(text=note[1], callback_data=f'delete_{note[0]}')
        keyboard.add(button)
    bot.reply_to(message, 'Выберите заметку для удаления:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_note(call):
    note_id = call.data.split('_')[1]
    connect = sqlite3.connect('schedulerbot.db')
    cursor = connect.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    connect.commit()
    cursor.close()
    connect.close()
    bot.answer_callback_query(call.id, 'Заметка удалена!')
    bot.delete_message(call.message.chat.id, call.message.message_id)

bot.polling()
