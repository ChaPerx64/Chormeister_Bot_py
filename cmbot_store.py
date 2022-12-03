from cmbot_songs import SongList

STORES_PATH = 'stores.json'
STORES = ['Лесколово', 'Захарова']


class StoreList(dict):
    def __init__(self, *args, **kwargs):
        super(StoreList, self).__init__()
        try:
            t_dict = args[0]
            if type(t_dict) == dict:
                for key in STORES:
                    if key in t_dict:
                        self.update({key: t_dict[key]})
                    else:
                        self.update({key: ""})
            print(t_dict)
        except Exception:
            pass


m = StoreList({'yo': 445689, 'Захарова': {'биба': 45689}})
t = StoreList()
print(m, t)