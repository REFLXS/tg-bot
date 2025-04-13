from TimeParser import TimeParser
import config
import telebot
import db
from telebot import types

bot = telebot.TeleBot(config.TOKEN)
parser = TimeParser()

print(parser.parse("2023/12/31 23:59 Новый год"))
temp_notes = {}


@bot.message_handler(commands=['start'])
def start(message):
    db.create_table()
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_add_note = types.KeyboardButton('Добавить заметку')
    button_delete_note = types.KeyboardButton('Удалить заметку')
    button_show_notes = types.KeyboardButton('Список заметок')
    button_clear_all = types.KeyboardButton('Очистить всё')
    button_done_notes = types.KeyboardButton('Выполненные')
    keyboard.add(button_add_note, button_delete_note, button_show_notes, button_clear_all, button_done_notes)
    bot.send_message(message.chat.id,
                     'Привет! Я бот для управления заметками. Выберите действие:',
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Добавить заметку')
def add_note_request(message):
    msg = bot.send_message(message.chat.id, 'Введите текст заметки:')
    bot.register_next_step_handler(msg, get_note_date)


def get_note_date(message):
    temp_notes[message.chat.id] = {
        'user_id': str(message.chat.id),
        'text': message.text
    }
    msg = bot.send_message(message.chat.id, 'Теперь введите дату для заметки:')
    bot.register_next_step_handler(msg, save_note_with_date)


def save_note_with_date(message):
    try:
        chat_id = message.chat.id
        if chat_id not in temp_notes:
            raise ValueError("Не найден текст заметки. Пожалуйста, начните процесс заново.")

        user_id = temp_notes[chat_id]['user_id']
        note_text = temp_notes[chat_id]['text']
        date_str = message.text
        try:
            if "-" in date_str:
                day, month, year = date_str.split("-")
                parsed_date = f"{year}-{month}-{day} 00:00:00"
            elif "/" in date_str:
                day, month, year = date_str.split("/")
                parsed_date = f"{year}-{month}-{day} 00:00:00"
            else:
                parsed_date = parser.parse(date_str)
                if not parsed_date:
                    raise ValueError("Не удалось распознать дату")
        except Exception as e:
            raise ValueError(f"Неверный формат даты. Используйте ДД-ММ-ГГГГ (например, 03-02-2004). Ошибка: {str(e)}")

        db.add_note(user_id, note_text, parsed_date)
        del temp_notes[chat_id]

        bot.send_message(chat_id, f'✅ Заметка успешно сохранена на {parsed_date}!')
    except Exception as e:
        error_msg = f'❌ Ошибка при сохранении: {str(e)}\n\nПопробуйте снова: нажмите "Добавить заметку"'
        bot.send_message(message.chat.id, error_msg)
        if message.chat.id in temp_notes:
            del temp_notes[message.chat.id]


@bot.message_handler(func=lambda message: message.text == 'Удалить заметку')
def delete_note_request(message):
    notes = db.get_user_notes(str(message.chat.id))

    if not notes:
        bot.send_message(message.chat.id, 'У вас нет невыполненных заметок.')
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


@bot.callback_query_handler(func=lambda call: call.data.startswith('done_'))
def done_note_callback(call):
    note_id = call.data.split('_')[1]
    db.mark_note_completed(note_id)
    bot.answer_callback_query(call.id, '✅ Заметка отмечена как выполненная!')
    bot.delete_message(call.message.chat.id, call.message.message_id)


@bot.message_handler(func=lambda message: message.text == 'Список заметок')
def list_notes(message):
    notes = db.get_user_notes(str(message.chat.id))

    if not notes:
        bot.send_message(message.chat.id, 'У вас нет сохраненных заметок.')
        return

    for note in notes:
        note_id, text, date = note
        keyboard = types.InlineKeyboardMarkup()
        btn_done = types.InlineKeyboardButton(text="✅ Выполнить", callback_data=f'done_{note_id}')
        btn_delete = types.InlineKeyboardButton(text="🗑️ Удалить", callback_data=f'delete_{note_id}')
        keyboard.add(btn_done, btn_delete)

        bot.send_message(
            message.chat.id,
            f"📌 {text}\n⏰ {date}",
            reply_markup=keyboard
        )


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


@bot.message_handler(func=lambda message: message.text == 'Выполненные')
def list_completed_notes(message):
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT note_text, note_end_date FROM notes WHERE user_id = ? AND completed = 1 ORDER BY '
                   'note_end_date', (str(message.chat.id),))
    notes = cursor.fetchall()
    cursor.close()
    conn.close()

    if not notes:
        bot.send_message(message.chat.id, 'У вас нет выполненных заметок.')
        return

    notes_list = '\n\n'.join([f"✅ {text}\n⏰ {date}" for text, date in notes])
    bot.send_message(message.chat.id, f'📋 Выполненные заметки:\n\n{notes_list}')


@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.send_message(message.chat.id,
                     "Я не понимаю эту команду. Пожалуйста, используйте кнопки меню.")


bot.remove_webhook()
bot.polling()
