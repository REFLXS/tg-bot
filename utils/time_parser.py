from datetime import datetime


class TimeParser:
    def parse(self, date_str):
        try:
            return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d 00:00:00")
        except Exception:
            return None
