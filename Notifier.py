import threading
import time
from datetime import datetime
from db import get_all_pending_notes
from telebot import TeleBot


class Notifier(threading.Thread):
    def __init__(self, bot: TeleBot, interval: int = 60):
        super().__init__()
        self.bot = bot
        self.interval = interval
        self.running = True

    def run(self):
        while self.running:
            now = datetime.now()
            notes = get_all_pending_notes()

            for note in notes:
                note_id, user_id, text, completed, created, end_date = note

                try:
                    note_time = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    continue
                if note_time <= now:
                    try:
                        self.bot.send_message(user_id, f'⏰ Напоминание:\n📌 {text}')
                        from db import mark_note_completed
                        mark_note_completed(note_id)
                    except Exception as e:
                        print(f"Ошибка отправки уведомления пользователю {user_id}: {e}")

            time.sleep(self.interval)

    def stop(self):
        self.running = False
