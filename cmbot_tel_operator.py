# System-related imports
import calendar
import datetime
import json
import os
import traceback

from dotenv import load_dotenv
# Telegram-related imports
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update
)
from telegram.ext import (
    CallbackContext,
    ConversationHandler,
    Application
)

from cmbot_performances import CalendarOps
# Imports from local modules
from cmbot_performances import Performance, PerformanceList
from cmbot_songs import SongList

# A constant for storing a filepath to the main JSON file
F_PATH = 'songlist.json'
PL_PATH = 'performances.json'
MBLIST_PATH = 'memberlist.json'
PL_PATH_BCK = 'data backup/' + PL_PATH.split('.')[0] + '_backup.json'
F_PATH_BCK = 'data backup/' + F_PATH.split('.')[0] + '_backup.json'

CLEAR_KEYBOARD = ReplyKeyboardRemove()
KEYBOARD_HOME = ReplyKeyboardMarkup(
    [
        [KeyboardButton("Искать по названию"), KeyboardButton("Искать по теме"), KeyboardButton("Искать везде")],
        [KeyboardButton("Выбрать по номеру"), KeyboardButton("Показать")],
        [KeyboardButton("Закончить")]
    ]
)
FATAL_ERROR_STR = 'Во мне что-то сломалось... Пойду чаю попью'


# Class for storing the authentication information
class Authenticator:
    # Loads data from .env file during initialization
    def __init__(self):
        load_dotenv()
        self.token = str(os.environ.get('CMB_TOKEN'))
        self.owner_id = int(os.environ.get('OWNER_ID'))
        self.choir_id = int(os.environ.get('CHOIR_GROUP_ID'))
        self.admins = []
        admins = os.environ.get('ADMINS_IDS').strip('][').split(', ')
        for item in admins:
            self.admins.append(int(item))
        self.admins.append(self.owner_id)


class TelegramOperator:
    def __init__(self, curr_auth: Authenticator, application: Application):
        self._curr_auth = curr_auth
        self._app = application

    async def waiter_greeting(self, update: Update, context: CallbackContext) -> int | str:
        print(str(update.message.from_user) + ' contacted the bot.')
        # context.chat_data
        if update.message.chat.type != 'private':
            await update.message.reply_text('Привет.\nПрости, но я не разговариваю в чатах.\nПиши в личку.')
            if update.message.chat_id != self._curr_auth.choir_id:  # failsafe in case bot SOMEHOW gets added where it shouldn't be
                await update.message.reply_text('И, кажется, я вас не знаю... Извините.')
                await update.message.chat.leave()
            return ConversationHandler.END
        # if update.message.from_user.id == self._curr_auth.owner_id or True:
        if update.message.from_user.id in memberlist_loader():
            await update.message.reply_text(
                text='Здравствуй. Начнём сначала.\nЧто ты хочешь сделать?',
                reply_markup=KEYBOARD_HOME
            )
            beast = update.message.from_user
            await self._app.bot.send_message(
                chat_id=self._curr_auth.owner_id,
                text='#ALARM\nCurrently speaking with:\n' + str(beast)
            )
        else:
            await update.message.reply_text("Мне кажется, мы не знакомы :'(\nЯ не буду с тобой разговаривать")
            beast = update.message.from_user
            await self._app.bot.send_message(
                chat_id=self._curr_auth.owner_id,
                text='#ALARM\n' + str(beast) + '\ntried to contact me'
            )
            return ConversationHandler.END
        return 'WAITER'

    async def waiter(self, update: Update, context: CallbackContext, owner_id=int) -> str | int:
        try:
            context.user_data.pop('SONGLIST')
            context.user_data.pop('SONG_ID')
        except:
            pass
        input_1 = update.message.text
        input_1 = input_1.lower()
        if input_1 == 'добавить песню':
            await update.message.reply_text('Ура! Добавляем новую песню!', reply_markup=CLEAR_KEYBOARD)
            return 'ADD'
        elif input_1 == 'искать везде':
            keyboard_markup = ReplyKeyboardMarkup([['Отмена']])
            await update.message.reply_text('Хорошо!', reply_markup=keyboard_markup)
            await update.message.reply_text('Введи фразу (или кусок слова) по которому мне искать песню.')
            context.user_data.update({'SEARCH_KEY': ''})
            return 'SEARCH'
        elif input_1 == 'искать по названию':
            keyboard_markup = ReplyKeyboardMarkup([['Отмена']])
            await update.message.reply_text('Хорошо, ищем по названию!', reply_markup=keyboard_markup)
            await update.message.reply_text('Введи фразу (или кусок слова) по которому мне искать песню.')
            context.user_data.update({'SEARCH_KEY': 'name'})
            return 'SEARCH'
        elif input_1 == 'искать по теме':
            keyboard_markup = ReplyKeyboardMarkup([['Отмена']])
            await update.message.reply_text('Хорошо, ищем по теме!', reply_markup=keyboard_markup)
            await update.message.reply_text('Введи фразу (или кусок слова) по которому мне искать песню.')
            context.user_data.update({'SEARCH_KEY': 'theme'})
            return 'SEARCH'
        elif input_1 == 'показать':
            await update.message.reply_text('Показываю ВСЕ песни в алфавитном порядке:')
            await self.show(update, context)
            # keyboard_markup = ReplyKeyboardMarkup([['Да', 'Нет', 'Наверное']])
            await update.message.reply_text('Что-то ещё?')
            return 'WAITER'
        elif input_1 == 'выбрать по номеру':
            keyboard_markup = ReplyKeyboardMarkup([['Отмена']])
            await update.message.reply_text('Ты знаешь номер песни? Отлично! Скажи его:', reply_markup=keyboard_markup)
            sl = SongList(F_PATH)
            context.user_data.update({'SONGLIST': sl})
            return 'SELECT_BY_ID'
            # TelegramOperator.select_song_by_id(update, context)
        elif input_1 == 'make backup':
            if update.message.from_user.id == self._curr_auth.owner_id:
                self.make_backup()
                await update.message.reply_text("BACKUP WAS INITIALIZED!")
                await update.message.reply_text('Backup complete!')
            else:
                await context.bot.send_message(chat_id=self._curr_auth.owner_id, text="BACKUP INITIALIZATION WAS ATTEMPTED!")
            return 'WAITER'
        # elif input_1 == 'load backup':
        #     TelegramOperator.load_backup()
        elif input_1 == 'закончить':
            await update.message.reply_text("Ладно. Пока!", reply_markup=CLEAR_KEYBOARD)
            return ConversationHandler.END
        elif input_1 == 'debug':
            # use this for testing pieces of code
            pass
        else:
            await update.message.reply_text('Я не понял, чего от меня хотят. Попробуй снова.')

    # @staticmethod
    # def add(update: Update, context: CallbackContext) -> str:
    #     song_dict = {}  # Creating a dictionary for song instance creation
    #     for key in Song.keys_stat():
    #         if key != "status":
    #             song_dict.update({key: input('Enter ' + key + ' for a new song: ')})
    #     try:
    #         new_song = Song(song_dict)
    #     except Exception:
    #         print("Oops. Something went wrong")
    #     print("Please, check entered inquiry.\n")  # Data confirmatioin
    #     print(new_song)
    #     if TelegramOperator.yn_question('Do you want to save it?'):  # Writing in the database file
    #         sl_adding = SongList(F_PATH)
    #         sl_adding.add_song(new_song)
    #         if sl_adding.save_to_file(F_PATH):
    #             print("Saved successfully!")
    #         else:
    #             print("Oops! An error occured. Sowwy :(")
    #     else:
    #         print('Saving aborted.')

    @staticmethod
    async def search(update: Update, context: CallbackContext):
        search_key = context.user_data.get('SEARCH_KEY')
        if type(search_key) is not str:
            await update.message.reply_text(text=FATAL_ERROR_STR, reply_markup=CLEAR_KEYBOARD)
            return ConversationHandler.END
        input_search = update.message.text
        input_search = input_search.lower()
        if input_search == "отмена":
            await update.message.reply_text("Оке! Поиск отменён.")
            await update.message.reply_text('Что-то ещё?', reply_markup=KEYBOARD_HOME)
            return 'WAITER'
        elif input_search != '':
            sl_search = SongList(F_PATH)
            matching_songs = sl_search.search(input_search, search_key)
            if matching_songs.sl == {}:
                await update.message.reply_text("Я ничего не нашёл. :'(\nПопробуй что-то другое.")
                return None
            else:
                await update.message.reply_text('Вот песни, которые я нашёл:')
                out_str = matching_songs.names_perf()
                if len(out_str) < 4000:
                    await update.message.reply_text(out_str)
                    await update.message.reply_text('Скажи номер произведения, который тебя интересует')
                    context.user_data.update({'SONGLIST': matching_songs})
                    return 'SELECT_BY_ID'
                else:
                    await update.message.reply_text('Список результатов слишком длинный.\nПопробуй короче. :)')
                    return None
        else:
            await update.message.reply_text('Я тебя не понял. =/\nПопробуй ещё раз.')

    # @staticmethod
    # def select_after_search(update: Update, context: CallbackContext) -> str:
    #     pass

    @staticmethod
    async def show(update: Update, context: CallbackContext):
        sl = SongList(F_PATH)
        ls = sl.names_abc().split('\n')
        i = 0
        out_str = ''
        for one_song in ls:
            out_str += str(one_song) + '\n'
            if i % 100 == 0:
                await update.message.reply_text(out_str)
                out_str = ''
            i += 1
            if i == len(ls):
                await update.message.reply_text(out_str)

    async def song_select_action(self, update: Update, context: CallbackContext):
        try:
            song_id = context.user_data.get('SONG_ID')
            sl1 = SongList(F_PATH)
            song_1 = sl1.get_song(song_id)
        except Exception("Error: wrong song_id passed to the function 'edit'"):
            await update.message.reply_text('Что-то во мне сломалось... Пойду чаю попью.')
            return ConversationHandler.END
        input_action = update.message.text
        input_action = input_action.lower()
        # if input_action == "edit":
        #     if TelegramOperator.song_update(song_id):
        #         return
        # elif input_action == "delete":
        #     if TelegramOperator.song_delete(song_id):
        #         return
        #     else:
        #         print("Deletion aborted.")
        if input_action == "смотреть исполнения":
            plist = PerformanceList()
            plist.read_from_file(PL_PATH)
            datelist = plist.find_song_performances(song_id)
            if datelist:
                await update.message.reply_text('Эта песня исполнялась в следующие даты:')
                out_str = ''
                for dt in datelist:
                    out_str += str(dt) + ', ' + CalendarOps.wd_name_from_int(dt.weekday()) + '\n'
                await update.message.reply_text(out_str)
                return 'SONG_SELECTED'
            else:
                await update.message.reply_text("Исполнений не найдено")
                return 'SONG_SELECTED'
        elif input_action == "добавить исполнение":
            if update.message.from_user.id in self._curr_auth.admins:
                keyboard_markup = ReplyKeyboardMarkup([['Последнее воскресенье'], ['Прошлое воскресенье'], ['Отмена']])
                await update.message.reply_text('Ок. Добавляем исполнение.', reply_markup=keyboard_markup)
                await update.message.reply_text('Введи дату в формате ГГГГ-ММ-ДД, или выбери из списка ниже')
                return 'ADD_PERFORMANCE'
            else:
                await update.message.reply_text('Тебе сюда нельзя, прости =/')
                return None
        elif input_action == 'назад':
            keyboard_markup = ReplyKeyboardMarkup([['Отмена']])
            await update.message.reply_text(
                'Хорошо, выбери другую песню из последнего списка.',
                reply_markup=keyboard_markup
            )
            return 'SELECT_BY_ID'
        elif input_action == "домой":
            await update.message.reply_text('Оке. Давай сначала.', reply_markup=KEYBOARD_HOME)
            return 'WAITER'
        else:
            await update.message.reply_text("Я тебя не понял. Попробуй снова.")
            return 'SONG_SELECTED'

    # @staticmethod
    # def song_update(song_id=str):
    #     sl_edit = SongList(F_PATH)
    #     song_in_edition = sl_edit.get_song(song_id)
    #     while True:
    #         try:
    #             input_edit_field = input("What do you want to edit? Enter key: ")
    #             input_edit_field = input_edit_field.lower()
    #             if input_edit_field in song_in_edition.keys():
    #                 f_value = input("Enter new value for " + input_edit_field + ": ")
    #                 song_in_edition.update_field(input_edit_field, f_value)
    #             else:
    #                 print("Wrong key has been entered.")
    #             if TelegramOperator.yn_question("Do you want to edit again?"):
    #                 pass
    #             else:
    #                 break
    #         except Exception:
    #             break
    #     print("\n" + str(song_in_edition) + "\n" + "Please, check entered inquiry.\n")  # Data confirmatioin
    #     if TelegramOperator.yn_question('Do you want to save it?'):  # Writing in the database file
    #         sl_adding = SongList(F_PATH)
    #         sl_adding.update_song(song_id, song_in_edition)
    #         if sl_adding.save_to_file(F_PATH):
    #             print("Saved successfully!")
    #             return True
    #         else:
    #             traceback.print_exc()
    #             print("Oops! An error occurred. Sowwy :(")
    #             return False
    #     else:
    #         print('Saving aborted.')
    #         return False

    @staticmethod
    async def select_song_by_id(update: Update, context: CallbackContext):
        try:
            sl1 = context.user_data.get('SONGLIST')
        except:
            await update.message.reply_text('Что-то во мне сломалось... Пойду чаю попью.')
            return ConversationHandler.END
        song_id = update.message.text
        # sl1 = SongList(F_PATH)
        if song_id in sl1.song_ids():
            await update.message.reply_text('Есть такая песня, да.')
            # context.user_data.pop('SONGLIST')
            context.user_data.update({'SONG_ID': song_id})
            sl2 = SongList(F_PATH)
            song_1 = sl2.get_song(song_id)
            await update.message.reply_text("Показываю песню:")
            await update.message.reply_text('#' + song_id + '\n' + str(song_1))
            keyboard_markup = ReplyKeyboardMarkup([['Смотреть исполнения', 'Добавить исполнение'],
                                                   ['Назад', 'Домой']])
            await update.message.reply_text('Что будем делать с песней?', reply_markup=keyboard_markup)
            return 'SONG_SELECTED'
            # TelegramOperator.song_select_action(song_id)
        elif song_id.lower() == 'отмена':
            await update.message.reply_text('Ок. Начнём снова', reply_markup=KEYBOARD_HOME)
            return 'WAITER'
        else:
            await update.message.reply_text(
                'Песни с таким номером последнем списке нет *dunno.jpg*\nP.S. Нужно ввести только цифру\nПопробуй снова'
            )

    # @staticmethod
    # def song_delete(song_id):
    #     sl1 = SongList(F_PATH)
    #     song_for_deletion = sl1.get_song(song_id)
    #     if TelegramOperator.yn_question("Are you sure you want to delete this song?"):
    #         print("\nShowing song selected for deletion:")
    #         print("Song id: '" + song_id + "'")
    #         print(song_for_deletion)
    #         if TelegramOperator.yn_question("Do you want to delete this song?"):
    #             if TelegramOperator.yn_question("This action is irreversible, "
    #                                             "do you still want to proceed?"):
    #                 song_for_deletion.change_to_deleted()
    #                 sl1.update_song(song_id, song_for_deletion)
    #                 sl1.save_to_file(F_PATH)
    #                 print("Song deleted successfully.")
    #                 return True
    #             else:
    #                 return False
    #         else:
    #             return False
    #     else:
    #         return False

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
    async def add_performance(update, context):
        keyboard_markup = ReplyKeyboardMarkup(
            [
                ['Смотреть исполнения', 'Добавить исполнение'],
                ['Назад', 'Домой']
            ]
        )
        song_id = context.user_data.get('SONG_ID')
        input_date = update.message.text
        # input_date = input_date.lower
        if input_date.lower() == 'отмена':
            await update.message.reply_text('Хорошо. Что делать с песней?', reply_markup=keyboard_markup)
            return 'SONG_SELECTED'
        if input_date.lower() == 'последнее воскресенье':
            input_date = str(recent_sundays(0))
        if input_date.lower() == 'прошлое воскресенье':
            input_date = str(recent_sundays(1))
        try:
            datetime.date.fromisoformat(str(input_date))
        except Exception:
            traceback.print_exc()
            await update.message.reply_text('ОШИБКА! :(\nВведи дату в формате ГГГГ-ММ-ДД')
            return None
        # while True:
        #     print("Enter the date of performance:")
        #     input_date = CalendarOps.iso_date_input()
        #     if not input_date:
        #         if not TelegramOperator.yn_question('Want to try again?'):
        #             break
        #     else:
        #         break
        plist = PerformanceList()
        plist.read_from_file(PL_PATH)
        p = Performance({'song_id': song_id,
                         'date': input_date})
        plist.add_performance(p)
        plist.save_to_file(PL_PATH)
        message = 'Сохранено исполнение ' + str(input_date)
        await update.message.reply_text(message, reply_markup=keyboard_markup)
        return 'SONG_SELECTED'

    # @staticmethod
    # def yn_question(qst):
    #     if isinstance(qst, str):
    #         inpt = input(qst + " Y/N: ")
    #         inpt = inpt.lower()
    #         if inpt == "y":
    #             return True
    #         else:
    #             return False
    #     else:
    #         raise Exception("Error occured in 'yn_question' method.")

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

    # @staticmethod
    # def load_backup():
    #     try:
    #         with open(PL_PATH_BCK, 'r') as f1:
    #             with open(PL_PATH, 'w') as f2:
    #                 f2.write(f1.read())
    #         with open(F_PATH_BCK, 'r') as f1:
    #             with open(F_PATH, 'w') as f2:
    #                 f2.write(f1.read())
    #         print('Data loaded from the backup successfully.')
    #     except Exception:
    #         print('Backup load failed.')

    @staticmethod
    async def stop(update: Update, context: CallbackContext):
        await update.message.reply_text(
            'Я показал что мог. Пиши /start, чтобы начать сначала',
            reply_markup=CLEAR_KEYBOARD
        )
        return ConversationHandler.END

    async def access_denied(self, update: Update, context: CallbackContext):
        if update.message.chat_id != self._curr_auth.choir_id:
            await update.message.reply_text('Привет.')
            await update.message.reply_text('Кажется, я вас не знаю... Извините.')
            await update.message.chat.leave()
        else:
            new_mb_list = update.message.new_chat_members
            with open(MBLIST_PATH, 'r') as f:
                mblist = json.load(f)
            for item in new_mb_list:
                if item.id not in mblist:
                    mblist.append(item.id)
            with open(MBLIST_PATH, 'w') as f:
                json.dump(mblist, f, ensure_ascii=False, indent=2)
            await self._app.bot.send_message(chat_id=self._curr_auth.owner_id, text='#ALARM\nNew members added!')

    async def remove_choir_member(self, update: Update, context: CallbackContext):
        if update.message.chat_id == self._curr_auth.choir_id:
            left_user_id = update.message.left_chat_member.id
            with open(MBLIST_PATH, 'r') as f:
                mblist = json.load(f)
                mblist.remove(left_user_id)
            with open(MBLIST_PATH, 'w') as f:
                json.dump(mblist, f, ensure_ascii=False, indent=2)
            await self._app.bot.send_message(chat_id=self._curr_auth.owner_id, text='#ALARM\nMember deleted')


def memberlist_loader():
    with open(MBLIST_PATH, 'r') as f:
        mblist = json.load(f)
    return mblist


def recent_sundays(skip=0):
    date_today = datetime.date.today()
    oneday = datetime.timedelta(days=1)
    date_sunday = date_today
    while skip >= 0:
        while date_sunday.weekday() != calendar.SUNDAY:
            date_sunday -= oneday
            # print(date_sunday)
        if skip:
            date_sunday -= oneday
        skip -= 1
    return date_sunday
