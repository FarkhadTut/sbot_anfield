from telegram import (
    Update,
    ReplyKeyboardRemove,
    )
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from config import get_superusers
import os 


WAIT_FILE = 20

async def refresh_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}. Отправьте Excel файл сюда...')
    return WAIT_FILE

async def reject_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Отправьте Excel файл...')
    return WAIT_FILE

async def save_db(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ## bot geting the document and its file_name
    file_id = update.message['document']['file_id']
    file_name = update.message['document']['file_name']
    file_obj= await context.bot.get_file(file_id)
    file_name_new = 'db.xlsx'
    file_path = await file_obj.download_to_drive(os.path.join('out', file_name_new))

    await update.message.reply_text(f'Я файл получил, рахмат.')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    await update.message.reply_text(
        "Саламалекум тогда.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

