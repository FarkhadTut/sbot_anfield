
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
from config import get_superusers

from .refresh_db import (
    refresh_db,
    save_db,
    reject_msg,
)
WAIT_FILE = 20

from .show_info import (
    start,
    respond_for_contact,
    send_info,
    reject_send_info,
)

CONTACT, DATE = 1, 2


date_pattern = r"^\d{2}\.\d{2}\.\d{4}$"

main_conversation = ConversationHandler(  
        entry_points=[CommandHandler("start", start),
                      CommandHandler("refresh_db", 
                                    refresh_db,
                                    filters=filters.Chat(username=get_superusers())),
                      ],
        states={
            WAIT_FILE: [MessageHandler(filters.Document.FileExtension(file_extension="xlsx"), save_db),
                        MessageHandler((~filters.Document.FileExtension(file_extension="xlsx"))&(~filters.COMMAND), reject_msg),],
            CONTACT: [MessageHandler(filters.CONTACT, respond_for_contact),
                      MessageHandler((~filters.CONTACT)&(~filters.COMMAND), start)],
            DATE: [MessageHandler(filters.Regex(date_pattern), send_info,),
                   MessageHandler((~filters.Regex(date_pattern)&(~filters.COMMAND)), reject_send_info,)],
        },  
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("refresh_db", 
                            refresh_db,
                            filters=filters.Chat(username=get_superusers()))],   
    )


