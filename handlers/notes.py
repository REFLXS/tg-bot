from telebot import types
import db.database as db
from utils.time_parser import TimeParser

temp_notes = {}
parser = TimeParser()

def register_handlers(bot):
    @bot.message_handler(func=lambda message: message.text == 'Добавить заметку')
    def add_note_request(message):
        msg = bot.send_message(message.chat.id, 'Введите текст заметки:')
        bot.register_next_step_handler(msg, get_note_date)

    def get_note_date(message):
        temp_notes[message.chat.id] = {
            'user_id': str(message.chat.id),
            'text': message.text
        }
        msg = bot.send_message(message.chat.id, 'Теперь введите дату (ДД-ММ-ГГГГ):')
        bot.register_next_step_handler(msg, save_note_with_date)

    def save_note_with_date(message):
        try:
            chat_id = message.chat.id
            user_id = temp_notes[chat_id]['user_id']
            note_text = temp_notes[chat_id]['text']
            date_str = message.text

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

            db.add_note(user_id, note_text, parsed_date)
            del temp_notes[chat_id]
            bot.send_message(chat_id, f'✅ Заметка сохранена на {parsed_date}!')

        except Exception as e:
            bot.send_message(message.chat.id, f'❌ Ошибка: {e}')

    @bot.message_handler(func=lambda message: message.text == 'Список заметок')
    def list_notes(message):
        notes = db.get_user_notes(str(message.chat.id))
        if not notes:
            bot.send_message(message.chat.id, 'Нет активных заметок.')
            return
        for note in notes:
            note_id, text, date = note
            keyboard = types.InlineKeyboardMarkup()
            btn_done = types.InlineKeyboardButton(text="✅ Выполнить", callback_data=f'done_{note_id}')
            btn_delete = types.InlineKeyboardButton(text="🗑️ Удалить", callback_data=f'delete_{note_id}')
            keyboard.add(btn_done, btn_delete)
            bot.send_message(message.chat.id, f"📌 {text}\n⏰ {date}", reply_markup=keyboard)

    @bot.message_handler(func=lambda message: message.text == 'Выполненные')
    def list_completed_notes(message):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT note_text, note_end_date FROM notes WHERE user_id = ? AND completed = 1', (str(message.chat.id),))
        notes = cursor.fetchall()
        conn.close()

        if not notes:
            bot.send_message(message.chat.id, 'Нет выполненных заметок.')
            return

        notes_list = '\n\n'.join([f"✅ {text}\n⏰ {date}" for text, date in notes])
        bot.send_message(message.chat.id, f'📋 Выполненные заметки:\n\n{notes_list}')
