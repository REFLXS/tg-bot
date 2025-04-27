import threading
import time
from db.database import get_all_pending_notes
from datetime import datetime


class Notifier(threading.Thread):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.daemon = True

    def run(self):
        while True:
            notes = get_all_pending_notes()
            for note in notes:
                note_id, user_id, text, completed, note_date, note_end_date = note
                if datetime.now() >= datetime.strptime(note_end_date, "%Y-%m-%d %H:%M:%S"):
                    try:
                        self.bot.send_message(user_id, f'🔔 Напоминание: {text}')
                        from db.database import mark_note_completed
                        mark_note_completed(note_id)
                    except Exception as e:
                        print(f"Ошибка при отправке уведомления: {e}")
            time.sleep(60)
