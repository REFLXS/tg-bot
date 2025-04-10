import re
from datetime import datetime, timedelta, date, time
class TimeParser():
    def __init__(self):
        self.reg_date = re.compile(r'(\d{4}/\d{1,2}/\d{1,2} \d{2}:\d{2}) (.*)')
        self.reg_word = re.compile(r'([а-я ]* в \d{2}:\d{2}) (.*)')
        self.days_and_shift = {
            'сегодня': timedelta(days=0),
            'завтра': timedelta(days=1),
            'послезавтра': timedelta(days=2),
            'через неделю': timedelta(days=7)
        }

    def parse_raw_date(self, input_string):
        try:
            result = datetime.strptime(input_string, "%Y/%m/%d %H:%M")
        except ValueError:
            return None
        return result

    def input_word_and_time(self, word, time_str):
        if word not in self.days_and_shift:
            return None
        date_part = date.today() + self.days_and_shift[word]
        time_part = datetime.strptime(time_str, "%H:%M").time()
        return datetime.combine(date_part, time_part)

    def input_word(self, word):
        today_date = date.today()
        if word not in self.days_and_shift:
            return None
        return datetime.combine(today_date + self.days_and_shift[word], time(0, 0))

    def parse(self, input_string):
        if not input_string:
            return None

        match_reg_date = self.reg_date.match(input_string)
        if match_reg_date:
            return self.parse_raw_date(match_reg_date.group(1))

        words = input_string.split()
        if words[0] in self.days_and_shift:
            if 'в' in words:
                idx = words.index('в')
                time_str = words[idx + 1] if idx + 1 < len(words) else "00:00"
                return self.input_word_and_time(words[0], time_str)
            return self.input_word(words[0])

        return None
