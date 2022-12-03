import json, time
from cmbot_performances import Performance, PerformanceList
from cmbot_performances import CalendarOps
import traceback
from cmbot_songs import Song, SongList, SONG_KEYSLIST_RU

# A constant for storing a filepath to the main JSON file
F_PATH = 'songlist.json'
PL_PATH = 'performances.json'
PL_PATH_BCK = 'data backup/' + PL_PATH.split('.')[0] + '_backup.json'
F_PATH_BCK = 'data backup/' + F_PATH.split('.')[0] + '_backup.json'


# main script. all the editing should be done here

class CLI_Operator:
    @staticmethod
    def waiter():
        while True:
            input_1 = input("\nWhat do you want to do? ")
            input_1 = input_1.lower()
            if input_1 == 'add':
                CLI_Operator.add()
            elif input_1 == 'search':
                CLI_Operator.search()
            elif input_1 == 'show':
                CLI_Operator.show()
            elif input_1 == 'select':
                CLI_Operator.select_song_by_id()
            elif input_1 == 'make backup':
                CLI_Operator.make_backup()
            elif input_1 == 'load backup':
                CLI_Operator.load_backup()
            elif input_1 == 'exit':
                print("Closing now... See ya! Bye!")
                break
            elif input_1 == 'debug':
                # use this for testing pieces of code
                pass
            else:
                print('Unknown command. Please, try again.')
            time.sleep(1)

    @staticmethod
    def add():
        print('YAY! Adding commences now...')
        song_dict = {}  # Creating a dictionary for song instance creation
        for key in Song.keys_stat():
            if key != "status":
                song_dict.update({key: input('Enter ' + key + ' for a new song: ')})
        try:
            new_song = Song(song_dict)
        except Exception:
            print("Oops. Something went wrong")
            return
        print("Please, check entered inquiry.\n")  # Data confirmatioin
        print(new_song)
        if CLI_Operator.yn_question('Do you want to save it?'):  # Writing in the database file
            sl_adding = SongList(F_PATH)
            sl_adding.add_song(new_song)
            if sl_adding.save_to_file(F_PATH):
                print("Saved successfully!")
            else:
                print("Oops! An error occured. Sowwy :(")
        else:
            print('Saving aborted.')

    @staticmethod
    def search():
        while True:
            max_lines = 999
            input_search = input("Enter a string that you want to find: ")
            if input_search == "cancel":
                print("Search cancelled")
                break
            elif input_search != '':
                sl_search = SongList(F_PATH)
                matching_songs = sl_search.search(input_search)
                if matching_songs.sl == {}:
                    print('No matches found :(')
                else:
                    if len(matching_songs.sl) > max_lines:
                        print('Result is too long. First ' + str(max_lines) + ' shown:')
                        short_list = SongList()
                        i = 1
                        for song_id, song in matching_songs.song_id_pairs():
                            if not short_list.update_song(song_id, song):
                                traceback.print_exc()
                                raise Exception
                            if i == max_lines:
                                break
                            i = i + 1
                        matching_songs = short_list
                    print()
                    print(matching_songs)
                    input_select = input('Select a song (enter id): ')
                    if input_select in matching_songs.song_ids():
                        try:
                            CLI_Operator.song_select_action(
                                str(input_select))  # in raises exceptions where it shouldn't
                        except Exception:
                            print("Error occurred. Operation cancelled")
                            traceback.print_exc()
                    else:
                        print("Wrong song id entered. Operation cancelled.")
            else:
                print("Unknown command")

    @staticmethod
    def show():
        sl = SongList(F_PATH)
        print(sl)

    @staticmethod
    def song_select_action(song_id):
        try:
            sl1 = SongList(F_PATH)
            song_1 = sl1.get_song(song_id)
            print("\nSong selected. Showing selected song now.")
            print(song_1)
        except Exception("Error: wrong song_id passed to the function 'edit'"):
            traceback.print_exc()
        i = 0
        while True:
            input_action = input("What do you want to do? edit/delete/performances/cancel: ")
            input_action = input_action.lower()
            if input_action == "edit":
                if CLI_Operator.song_update(song_id):
                    return
            elif input_action == "delete":
                if CLI_Operator.song_delete(song_id):
                    return
                else:
                    print("Deletion aborted.")
            elif input_action == "performances":
                if CLI_Operator.find_performances(song_id):
                    return
            elif input_action == "add performances":
                if CLI_Operator.add_performance(song_id):
                    return
            elif input_action == "cancel":
                print("Operation cancelled.")
                break
            else:
                print("Unknown command. Try again")
            i += 1

    @staticmethod
    def song_update(song_id=str):
        sl_edit = SongList(F_PATH)
        song_in_edition = sl_edit.get_song(song_id)
        while True:
            try:
                input_edit_field = input("What do you want to edit? Enter key: ")
                input_edit_field = input_edit_field.lower()
                if input_edit_field in song_in_edition.keys():
                    f_value = input("Enter new value for " + input_edit_field + ": ")
                    song_in_edition.update_field(input_edit_field, f_value)
                else:
                    print("Wrong key has been entered.")
                if CLI_Operator.yn_question("Do you want to edit again?"):
                    pass
                else:
                    break
            except Exception:
                break
        print("\n" + str(song_in_edition) + "\n" + "Please, check entered inquiry.\n")  # Data confirmatioin
        if CLI_Operator.yn_question('Do you want to save it?'):  # Writing in the database file
            sl_adding = SongList(F_PATH)
            sl_adding.update_song(song_id, song_in_edition)
            if sl_adding.save_to_file(F_PATH):
                print("Saved successfully!")
                return True
            else:
                traceback.print_exc()
                print("Oops! An error occurred. Sowwy :(")
                return False
        else:
            print('Saving aborted.')
            return False

    @staticmethod
    def select_song_by_id():
        song_id = input("Enter song id: ")
        sl1 = SongList(F_PATH)
        if song_id in sl1.song_ids():
            print("Song with entered id found.")
            CLI_Operator.song_select_action(song_id)
        else:
            print("Sorry. Song id not found.")

    @staticmethod
    def song_delete(song_id):
        sl1 = SongList(F_PATH)
        song_for_deletion = sl1.get_song(song_id)
        if CLI_Operator.yn_question("Are you sure you want to delete this song?"):
            print("\nShowing song selected for deletion:")
            print("Song id: '" + song_id + "'")
            print(song_for_deletion)
            if CLI_Operator.yn_question("Do you want to delete this song?"):
                if CLI_Operator.yn_question("This action is irreversible, "
                                            "do you still want to proceed?"):
                    song_for_deletion.change_to_deleted()
                    sl1.update_song(song_id, song_for_deletion)
                    sl1.save_to_file(F_PATH)
                    print("Song deleted successfully.")
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    @staticmethod
    def find_performances(song_id):
        plist = PerformanceList()
        plist.read_from_file(PL_PATH)
        datelist = plist.find_song_performances(song_id)
        if datelist:
            print('This song was performed in:')
            for dt in datelist:
                print(str(dt) + ', ' + CalendarOps.wd_name_from_int(dt.weekday()))
        else:
            print("No performances found")

    @staticmethod
    def add_performance(song_id):
        while True:
            print("Enter the date of performance:")
            input_date = CalendarOps.iso_date_input()
            if not input_date:
                if not CLI_Operator.yn_question('Want to try again?'):
                    break
            else:
                break
        plist = PerformanceList()
        plist.read_from_file(PL_PATH)
        p = Performance({'song_id': song_id,
                         'date': input_date})
        plist.add_performance(p)
        plist.save_to_file(PL_PATH)
        print('Performance saved successfully!')

    @staticmethod
    def yn_question(qst):
        if isinstance(qst, str):
            inpt = input(qst + " Y/N: ")
            inpt = inpt.lower()
            if inpt == "y":
                return True
            else:
                return False
        else:
            raise Exception("Error occured in 'yn_question' method.")

    @staticmethod
    def make_backup():
        try:
            with open(PL_PATH, 'r') as f1:
                with open(PL_PATH_BCK, 'w') as f2:
                    f2.write(f1.read())
            with open(F_PATH, 'r') as f1:
                with open(F_PATH_BCK, 'w') as f2:
                    f2.write(f1.read())
            print('Data backed up successfully')
        except Exception:
            print('Backup failed')

    @staticmethod
    def load_backup():
        try:
            with open(PL_PATH_BCK, 'r') as f1:
                with open(PL_PATH, 'w') as f2:
                    f2.write(f1.read())
            with open(F_PATH_BCK, 'r') as f1:
                with open(F_PATH, 'w') as f2:
                    f2.write(f1.read())
            print('Data loaded from the backup successfully.')
        except Exception:
            print('Backup load failed.')


CLI_Operator.waiter()
