from telebot import types


def register_handlers(bot):
    @bot.message_handler(commands=['start'])
    def start(message):
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        buttons = ['Добавить заметку', 'Удалить заметку', 'Список заметок', 'Очистить всё', 'Выполненные']
        keyboard.add(*(types.KeyboardButton(b) for b in buttons))
        bot.send_message(
            message.chat.id,
            'Привет! Я бот для управления заметками. Выберите действие:',
            reply_markup=keyboard
        )
