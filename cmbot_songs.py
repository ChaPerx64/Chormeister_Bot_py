import datetime
import json
import cmbot_performances
# Lists of names of the fields, if it's changed - corresponting changes
# MUST BE applied to the __init__() and clear() functions
import traceback
from cmbot_performances import Performance, PerformanceList
from urllib.request import urlopen
import validators


# SONG_KEYSLIST = ['status', 'name', 'lyricist', 'composer', 'translator', 'theme', 'performers', 'melodicality']
SONG_KEYSLIST = ['status']
SONG_KEYSLIST_RU = ['Название', 'Автор текста', 'Композитор', 'Переводчик', 'Тема', 'Состав', 'Мелодичность']
DB_STATE_KEYSLIST = ['SONGS', 'LASTUPDATED']

# F_PATH = 'songlist.json'
PL_PATH = 'http://127.0.0.1:8000/getchorperformances/?format=json&c=1'

class Song:
    def __init__(self, *args, **kwargs):
        try:
            t_dict = args[0]
            # SONG_KEYSLIST.clear()
            for key in t_dict.keys():
                SONG_KEYSLIST.append(key)
            for key in SONG_KEYSLIST:
                if key in t_dict:
                    self.__dict__.update({key: t_dict[key]})
                else:
                    self.__dict__.update({key: ""})
        except Exception:
            self.clear()
            pass

    def __str__(self):
        out_str = ''
        for attr, value in self.items():
            out_str += str(attr) + ' - ' + str(value) + '\n'
        return out_str

    def clear(self):
        self.__dict__.clear()
        for key in SONG_KEYSLIST:
            self.__dict__.update({key: ""})

    def json_ready(self):
        t_dict = {}
        for attr, value in self.__dict__.items():
            t_dict.update({attr: value})
        return t_dict

    def items(self):
        t_list = []
        for attr, value in self.__dict__.items():
            if attr != 'status':
                t_list.append((attr, value))
        return t_list

    def keys(self):
        t_list = []
        for attr, value in self.items():
            t_list.append(attr)
        return t_list

    def values(self):
        t_list = []
        for attr, value in self.items():
            t_list.append(value)
        return t_list

    def found_in(self, sought_str=str):
        sought_str = sought_str.lower()
        t_str = ''
        for v in self.values():
            t_str += v
        t_str = t_str.lower()
        if sought_str in t_str:
            return True
        else:
            return False

    def update_field(self, field, value):
        if field == 'status':
            print("ERROR: Field 'STATUS' is not accessible.")
            return False
        for key in SONG_KEYSLIST:
            if field == key:
                self.__dict__.update({key: value})
                return True
        print("Wrong key's been entered")
        return False
        # except Exception:
        #     traceback.print_exc()

    def change_to_deleted(self):
        for attr, value in self.__dict__.items():
            if attr == 'status':
                self.__dict__.update({attr: "deleted"})
            else:
                value = str("### " + value + " ###")
                self.__dict__.update({attr: value})

    @staticmethod
    def keys_stat():
        pass
        return SONG_KEYSLIST


class SongList:
    def __init__(self, path=None, *args, **kwargs):
        if len(args) and type(args[0]) == dict:
            try:
                self.from_json_dict()
            except Exception:
                raise TypeError
        else:
            self.sl = {}
        if path:
            if validators.url(path):
                response = urlopen(path)
                songlist_json = json.loads(response.read())
                self.from_json_dict(songlist_json)
            else:
                self.read_from_file(path)
                try:
                    self.read_from_file(path)
                except:
                    raise TypeError

    def __str__(self):
        out_str = ''
        for attr, value in self.song_id_pairs():
            out_str += 'Song id: ' + attr + ", Song:\n" + str(value) + "\n"
        return out_str

    def names_ru(self):
        out_str = ''
        for attr, value in self.song_id_pairs():
            out_str += '#' + attr + ". " + str(value.name) + "\n"
        return out_str\

    # @staticmethod
    # def sort_key(sdict: dict):
    #     sdict

    def names_abc(self):
        out_list = []
        for attr, value in self.song_id_pairs():
            out_list.append([attr, value.name])
        out_list.sort(key=lambda k: k[1])
        out_str = ''
        for item in out_list:
            if int(item[0]) < 10:
                out_str += '#' + str(item[0]) + '     - ' + str(item[1]) + '\n'
            elif int(item[0]) < 100:
                out_str += '#' + str(item[0]) + '   - ' + str(item[1]) + '\n'
            else:
                out_str += '#' + str(item[0]) + ' - ' + str(item[1]) + '\n'
        return out_str

    def names_perf(self):
        plist = PerformanceList()
        plist.read_from_file(PL_PATH)
        out_list = []
        out_list_wdates = []
        for id, song in self.song_id_pairs():
            datelist = plist.find_song_performances(id)
            if datelist:
                out_list_wdates.append([id, datelist[0], song.name])
            else:
                out_list.append([id, song.name])
        if out_list:
            out_str = '\nПесни, которые мы НЕ ПЕЛИ:\n'
            out_list.sort(key=lambda k: k[1])
            for item in out_list:
                if int(item[0]) < 10:
                    out_str += '#' + str(item[0]) + '     - ' + str(item[1]) + '\n'
                elif int(item[0]) < 100:
                    out_str += '#' + str(item[0]) + '   - ' + str(item[1]) + '\n'
                else:
                    out_str += '#' + str(item[0]) + ' - ' + str(item[1]) + '\n'
        else:
            out_str = ''
        if out_list_wdates:
            out_list_wdates.sort(key=SongList.datelist_sort, reverse=True)
            out_str_wdates = '\nПесни, которые мы УЖЕ ПЕЛИ:\n'
            for item in out_list_wdates:
                if int(item[0]) < 10:
                    out_str_wdates += '#' + str(item[0]) + '     - ' + str(item[1]) + ' - ' + str(item[2]) + '\n'
                elif int(item[0]) < 100:
                    out_str_wdates += '#' + str(item[0]) + '   - ' + str(item[1]) + ' - ' + str(item[2]) + '\n'
                else:
                    out_str_wdates += '#' + str(item[0]) + ' - ' + str(item[1]) + ' - ' + str(item[2]) + '\n'
        else:
            out_str_wdates = ''
        return out_str + out_str_wdates

    @staticmethod
    def datelist_sort(perf_date):
        if type(perf_date[1]) is datetime.date:
            return perf_date[1]
        else:
            return datetime.date.today()

    def clear(self):
        self.sl.clear()

    def add_song(self, song=Song):
        self.sl.update({self.new_song_id(): song})

    def update_song(self, key, song=Song):
        self.sl.update({key: song})
        return True

    def recent_song_id(self):
        recent_song_id = 0
        if len(self.sl) != 0:
            for song_id in self.sl.keys():
                if int(song_id) > recent_song_id:
                    recent_song_id = int(song_id)
            return str(recent_song_id)
        else:
            return '0'

    def new_song_id(self):
        recent_song_id = 0
        if len(self.sl) != 0:
            for song_id in self.sl.keys():
                if int(song_id) >= recent_song_id:
                    recent_song_id = int(song_id) + 1
            return str(recent_song_id)
        else:
            return '0'

    def json_ready(self):
        t_dict = {}
        for attr, value in self.sl.items():
            try:
                value_out = value.json_ready()
                t_dict.update({attr: value_out})
            except:
                t_dict.update({attr: value})
        return t_dict

    def from_json_dict(self, t_dict=dict):
        for key, value in t_dict.items():
            try:
                song_id = int(key)
                song = Song(value)
            except:
                raise TypeError
            self.sl.update({str(song_id): song})

    def save_to_file(self, sl_path):
        try:
            with open(sl_path, 'w') as f:
                json.dump(self.json_ready(), f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def read_from_file(self, sl_path):
        with open(sl_path, 'r') as f:
            self.clear()
            self.from_json_dict(json.load(f))

    def get_song(self, song_id):
        if song_id in self.song_ids():
            for song_id_key, song in self.song_id_pairs():
                if song_id_key == song_id:
                    if isinstance(song, Song):
                        return song
        else:
            traceback.print_exc()
            raise Exception("Wrong song_id passed to the method SongList.get_song")

    def song_id_pairs(self):
        t_list = []
        for song_id, song in self.sl.items():
            if song.status != 'deleted':
                t_list.append((song_id, song))
        return t_list

    def song_ids(self):
        t_list = []
        for song_id, song in self.song_id_pairs():
            t_list.append(song_id)
        return t_list

    def songs(self):
        t_list = []
        for song_id, song in self.song_id_pairs():
            t_list.append(song)
        return t_list

    # def update(self, id_song_pair=dict):
    #     #print(id_song_pair)
    #     for key, value in id_song_pair.items():
    #         self.sl.update({key: value})

    def search(self, sought_str=str, key=str):
        sl_matching_songs = SongList()
        if key == '':
            for song_id, song in self.sl.items():
                if song.found_in(sought_str):
                    sl_matching_songs.sl.update({song_id: song})
        elif key == 'name':
            for song_id, song in self.sl.items():
                if sought_str in str(song.name).lower():
                    sl_matching_songs.sl.update({song_id: song})
        elif key == 'theme':
            for song_id, song in self.sl.items():
                if sought_str in song.theme.lower():
                    sl_matching_songs.sl.update({song_id: song})
        return sl_matching_songs
