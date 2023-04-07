import datetime
import json

PL_PATH = 'performances.json'


class Performance:
    date = None

    def __init__(self, *args, **kwargs):
        try:
            t_dict = args[0]
            self.song_id = t_dict['song_id']
            self.date = datetime.date.fromisoformat(t_dict['date'])
        except Exception:
            raise Exception('Wrong arguments passed')

    def __str__(self):
        out_str = 'Song with id "' + self.song_id + '" was performed at ' + str(self.date)
        out_str += ', ' + CalendarOps.wd_name_from_int(self.date.weekday())
        return out_str

    def json_ready(self):
        t_dict = {}
        t_dict.update({'song_id': self.song_id})
        t_dict.update({'date': str(self.date)})
        return t_dict


class PerformanceList(list):
    def __init__(self, *args, **kwargs):
        super(PerformanceList, self).__init__(*args, **kwargs)

    def add_performance(self, perf=Performance):
        pos = 0
        for elem in self:
            if perf.date > elem.date:
                self.insert(pos, perf)
                break
            pos += 1
            if pos == len(self):
                self.append(perf)
                break

    def json_ready(self):
        t_dict = []
        for value in self:
            try:
                value_out = value.json_ready()
                t_dict.append(value_out)
            except:
                t_dict.append(value)
        return t_dict

    def save_to_file(self, pl_path):
        try:
            with open(pl_path, 'w') as f:
                json.dump(self.json_ready(), f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def from_json_list(self, t_dict):
        self.clear()
        for value in t_dict:
            try:
                perf = Performance(value)
            except:
                raise TypeError
            self.append(perf)

    def read_from_file(self, pl_path):
        with open(pl_path, 'r') as f:
            # self.clear()
            self.from_json_list(json.load(f))

    def find_song_performances(self, song_id):
        pf_list = []
        for perf in self:
            if song_id == perf.song_id:
                pf_list.append(perf.date)
        pf_list.sort(reverse=True)
        return pf_list

    def sort(self, *args, **kwargs):
        kwargs.update(
            {
                'reverse': True,
                'key': lambda k: k.date
            }
        )
        super(PerformanceList, self).sort(*args, **kwargs)


class CalendarOps:
    @staticmethod
    def wd_name_from_int(wd):
        if wd == 0:
            return "Понедельник"
        elif wd == 1:
            return "Вторник"
        elif wd == 2:
            return "Среда"
        elif wd == 3:
            return "Четверг"
        elif wd == 4:
            return "Пятница"
        elif wd == 5:
            return "Суббота"
        elif wd == 6:
            return "Воскресенье"
        else:
            raise TypeError('Wrong weekday format')

    @staticmethod
    def iso_date_input():
        date_str = ''
        date_str += input('Please, input the year (YYYY): ')
        date_str += '-' + input('Please, input the month (MM): ')
        date_str += '-' + input('Please, input the month (DD): ')
        try:
            datetime.date.fromisoformat(date_str)
            return date_str
        except:
            print('ERROR: wrong data entered')
            return False

# print(CalendarOps.iso_date_input())
# x = PerformanceList()
# x.read_from_file(PL_PATH)
# print(x.find_song_performances('9'))
# for p in x:
#     print(p)
# x.save_to_file(F_PATH)
# print(x.find_song_performances('9'))
