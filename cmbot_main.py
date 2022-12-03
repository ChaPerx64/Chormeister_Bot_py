from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    CallbackContext,
    CallbackQueryHandler,
    Filters
)
from telegram import (
    Update
)
from cmbot_tel_operator import TelegramOperator, Authenticator
import logging, json
MBLIST_PATH = 'memberlist.json'

# Creating authenticator instance
curr_auth = Authenticator()

SELECTING_ACTION, ADDING_MEMBER, ADDING_SELF, DESCRIBING_SELF = map(chr, range(4))


def access_denied(update: Update, context: CallbackContext):
    if update.message.chat_id != curr_auth.choir_id:
        update.message.reply_text('Привет.')
        update.message.reply_text('Кажется, я вас не знаю... Извините.')
        update.message.chat.leave()
    else:
        new_mb_list = update.message.new_chat_members
        with open(MBLIST_PATH, 'r') as f:
            mblist = json.load(f)
        for item in new_mb_list:
            if item.id not in mblist:
                mblist.append(item.id)
        with open(MBLIST_PATH, 'w') as f:
            json.dump(mblist, f, ensure_ascii=False, indent=2)
        update.message.bot.send_message(chat_id=curr_auth.owner_id, text='#ALARM\nNew members added!')

def remove_choir_member(update: Update, context: CallbackContext):
    if update.message.chat_id == curr_auth.choir_id:
        left_user_id = update.message.left_chat_member.id
        with open(MBLIST_PATH, 'r') as f:
            mblist = json.load(f)
            mblist.remove(left_user_id)
        with open(MBLIST_PATH, 'w') as f:
            json.dump(mblist, f, ensure_ascii=False, indent=2)
        update.message.bot.send_message(chat_id=curr_auth.owner_id, text='#ALARM\nMember deleted')

def main():
    # Launching logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    curr_auth = Authenticator()
    updater = Updater(token=curr_auth.token)
    dispatcher = updater.dispatcher
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', TelegramOperator.waiter_greeting)],
        states={'WAITER': [MessageHandler(Filters.text, TelegramOperator.waiter)],
                'SEARCH': [MessageHandler(Filters.text, TelegramOperator.search)],
                # 'SEARCH_BY_NAME': [MessageHandler(Filters.text, TelegramOperator.search)],
                'SELECT_BY_ID': [MessageHandler(Filters.text, TelegramOperator.select_song_by_id)],
                'SONG_SELECTED': [MessageHandler(Filters.text, TelegramOperator.song_select_action)],
                # 'ALARM OWNER': [M]
                'ADD_PERFORMANCE': [MessageHandler(Filters.text, TelegramOperator.add_performance)],
                'FIND_PERFORMANCES': [MessageHandler(Filters.text, TelegramOperator.find_performances)]
                },
        fallbacks=[CommandHandler('stop', TelegramOperator.stop)],
        allow_reentry=True,
        conversation_timeout=500
    )
    msg_hand = MessageHandler(Filters.status_update.new_chat_members, access_denied)
    member_left = MessageHandler(Filters.status_update.left_chat_member, remove_choir_member)
    dispatcher.add_handler(msg_hand)
    dispatcher.add_handler(conversation_handler)
    dispatcher.add_handler(member_left)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    print("ChormeisterBot welcomes you!")
    print()
    main()
