import db.database as db
from telebot import types


def register_callbacks(bot):
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
        bot.answer_callback_query(call.id, '✅ Заметка выполнена!')
        bot.delete_message(call.message.chat.id, call.message.message_id)

    @bot.message_handler(func=lambda message: message.text == 'Очистить всё')
    def clear_all_notes(message):
        keyboard = types.InlineKeyboardMarkup()
        confirm_button = types.InlineKeyboardButton(text="✅ Да, удалить всё", callback_data='confirm_clear')
        cancel_button = types.InlineKeyboardButton(text="❌ Отмена", callback_data='cancel_clear')
        keyboard.add(confirm_button, cancel_button)
        bot.send_message(message.chat.id, "⚠️ Удалить все заметки?", reply_markup=keyboard)

    @bot.callback_query_handler(func=lambda call: call.data == 'confirm_clear')
    def confirm_clear(call):
        deleted = db.delete_all_user_notes(str(call.message.chat.id))
        bot.answer_callback_query(call.id, f"Удалено {deleted} заметок.")
        bot.delete_message(call.message.chat.id, call.message.message_id)

    @bot.callback_query_handler(func=lambda call: call.data == 'cancel_clear')
    def cancel_clear(call):
        bot.answer_callback_query(call.id, "❌ Отмена.")
        bot.delete_message(call.message.chat.id, call.message.message_id)

