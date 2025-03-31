from TimeParser import TimeParser
import config
import telebot
import db
import datetime
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
parser = TimeParser()

# Тестовые вызовы парсера
# print(parser.parse_raw_date("2023/12/31 23:59"))
# print(parser.input_word_and_time("завтра", "15:30"))
# print(parser.input_word("послезавтра"))
# print(parser.parse_string("сегодня в 14:00"))
# print(parser.parse("2023/12/31 23:59 Новый год"))
# print(parser.parse(""))

print(parser.parse("2023/12/31 23:59 Новый год"))


@bot.message_handler(commands=['start'])
def start(message):
    db.create_table()

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_add_note = types.KeyboardButton('Добавить заметку')
    button_delete_note = types.KeyboardButton('Удалить заметку')
    button_show_notes = types.KeyboardButton('Список заметок')
    button_clear_all = types.KeyboardButton('Очистить всё')
    keyboard.add(button_add_note, button_delete_note, button_show_notes, button_clear_all)

    bot.send_message(message.chat.id,
                     'Привет! Я бот для управления заметками. Выберите действие:',
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Добавить заметку')
def add_note_request(message):
    msg = bot.send_message(message.chat.id,
                           'Введите текст заметки:')
    bot.register_next_step_handler(msg, save_note)


def save_note(message):
    try:
        db.add_note(message, datetime.datetime.now())
        bot.send_message(message.chat.id, '✅ Заметка успешно сохранена!')
    except Exception as e:
        bot.send_message(message.chat.id, f'❌ Ошибка при сохранении: {str(e)}')


@bot.message_handler(func=lambda message: message.text == 'Удалить заметку')
def delete_note_request(message):
    notes = db.get_user_notes(str(message.chat.id))

    if not notes:
        bot.send_message(message.chat.id, 'У вас нет сохраненных заметок.')
        return

    keyboard = types.InlineKeyboardMarkup()
    for note in notes:
        button = types.InlineKeyboardButton(
            text=f"{note[1]} ({note[2]})",
            callback_data=f'delete_{note[0]}')
        keyboard.add(button)

    bot.send_message(message.chat.id,
                     'Выберите заметку для удаления:',
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def delete_note_callback(call):
    note_id = call.data.split('_')[1]
    db.delete_note(note_id)
    bot.answer_callback_query(call.id, '🗑️ Заметка удалена!')
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.message_handler(func=lambda message: message.text == 'Список заметок')
def list_notes(message):
    notes = db.get_user_notes(str(message.chat.id))

    if not notes:
        bot.send_message(message.chat.id, 'У вас нет сохраненных заметок.')
        return

    notes_list = '\n\n'.join([f"📌 {note[1]}\n⏰ {note[2]}" for note in notes])
    bot.send_message(message.chat.id, f'📋 Ваши заметки:\n\n{notes_list}')


@bot.message_handler(func=lambda message: message.text == 'Очистить всё')
def clear_all_notes_handler(message):
    keyboard = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton(
        text="✅ Да, удалить всё",
        callback_data='confirm_clear')
    cancel_button = types.InlineKeyboardButton(
        text="❌ Отмена",
        callback_data='cancel_clear')
    keyboard.add(confirm_button, cancel_button)

    bot.send_message(message.chat.id,
                     "⚠️ Вы уверены, что хотите удалить ВСЕ свои заметки?",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'confirm_clear')
def confirm_clear_callback(call):
    deleted_count = db.delete_all_user_notes(str(call.message.chat.id))
    bot.answer_callback_query(call.id, f"🗑️ Удалено {deleted_count} заметок!")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, f"Все заметки ({deleted_count}) успешно удалены.")


@bot.callback_query_handler(func=lambda call: call.data == 'cancel_clear')
def cancel_clear_callback(call):
    bot.answer_callback_query(call.id, "❌ Отменено")
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.send_message(message.chat.id,
                     "Я не понимаю эту команду. Пожалуйста, используйте кнопки меню.")


if __name__ == '__main__':
    bot.polling(none_stop=True)