import logging, os

from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ApplicationBuilder,
    ContextTypes
)

from cmbot_tel_operator import TelegramOperator, Authenticator

MBLIST_PATH = 'memberlist.json'

SELECTING_ACTION, ADDING_MEMBER, ADDING_SELF, DESCRIBING_SELF = map(chr, range(4))


async def startup_msg(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(str(os.getenv('OWNER_ID')), 'ChormeisterBot is up and running!')


def main():
    # Launching logger
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    curr_auth = Authenticator()
    application = ApplicationBuilder().token(curr_auth.token).build()
    # async with application:
    tel_op = TelegramOperator(curr_auth, application)
    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', tel_op.waiter_greeting)],
        states={
            'WAITER': [MessageHandler(filters.TEXT, tel_op.waiter)],
            'SEARCH': [MessageHandler(filters.TEXT, tel_op.search)],
            'SELECT_BY_ID': [MessageHandler(filters.TEXT, tel_op.select_song_by_id)],
            'SONG_SELECTED': [MessageHandler(filters.TEXT, tel_op.song_select_action)],
            'ADD_PERFORMANCE': [MessageHandler(filters.TEXT, tel_op.add_performance)],
            'FIND_PERFORMANCES': [MessageHandler(filters.TEXT, tel_op.find_performances)]
        },
        fallbacks=[CommandHandler('stop', TelegramOperator.stop)],
        allow_reentry=True,
        conversation_timeout=500
    )
    msg_hand = MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, tel_op.access_denied)
    member_left = MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, tel_op.remove_choir_member)
    application.add_handler(msg_hand)
    application.add_handler(conversation_handler)
    application.add_handler(member_left)
    application.job_queue.run_once(startup_msg, 0)
    application.run_polling()


if __name__ == "__main__":
    print("ChormeisterBot welcomes you!")
    print()
    main()
