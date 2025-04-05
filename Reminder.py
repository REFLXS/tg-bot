import threading
import time
import datetime
import db
from telebot import TeleBot

class Reminder(threading.Thread):
    def __init__(self, bot: TeleBot, interval: int = 60):
        super().__init__()
        self.bot = bot
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            now = datetime.datetime.now()
            notes = db.get_all_pending_notes()

            for note in notes:
                note_id, user_id, text, _, _, note_end_date = note
                if note_end_date and now >= datetime.datetime.strptime(note_end_date, '%Y-%m-%d %H:%M:%S'):
                    try:
                        self.bot.send_message(user_id, f"🔔 Напоминание: {text}")
                        db.mark_note_completed(note_id)
                    except Exception as e:
                        print(f"Ошибка при отправке напоминания: {e}")

            time.sleep(self.interval)

    def stop(self):
        self.running = False
