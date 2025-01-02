from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    KeyboardButton,
    )
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode
from config import get_superusers
import os 
import logging
import pandas as pd
import dataframe_image as dfi
import uuid
from tabulate import tabulate
from cachetools import TTLCache
cache = TTLCache(maxsize=100, ttl=3600*24*7)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CONTACT, DATE, MONTH, DAY = 1, 2, 3, 4

db_filepath = os.path.join('out', 'db.xlsx')
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not os.path.exists(os.path.join("out", 'db.xlsx')):
        await update.message.reply_text(f'Не найдена база данных...')
        return ConversationHandler.END

    text = f'Привет, {update.effective_user.first_name}. Отправьте свой Телеграм контакт, чтобы проверить информацию о себе.'
    reply_keyboard = [[KeyboardButton(text="Отправить контакт",
                                     request_contact=True,)]]
    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, 
            one_time_keyboard=True,
        ),
    )
    return CONTACT

async def reject_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Нажмите на кнопку внизу "Отправить контакт"...')
    return CONTACT

async def reject_send_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Отправьте дату в формате: <strong>ДД.ММ.ГГГГ</strong>', parse_mode=ParseMode.HTML)
    return DATE

async def check_exist(phone_number):
    df = pd.read_excel(db_filepath)
    mask = df["Телефон номер"] == int(phone_number)
    return mask.any()

async def check_by_date(date, chat_id):
    df = pd.read_excel(db_filepath)

    phone_number = cache[chat_id]
    mask = ((df["Период, день"] == date) & (df["Телефон номер"] == int(phone_number)))
    df = df[mask].tail(1)
    df.fillna(0, inplace=True)
    return df

async def last_record(phone_number):
    df = pd.read_excel(db_filepath)
    mask = ((df["Телефон номер"] == int(phone_number)))
    df = df[mask].tail(1)
    df.fillna(0, inplace=True)
    return df

async def add_delimeters(number):
    number = (int(number))

    formatted_number = '{0:,}'.format(number).replace(',', ' ')


    return formatted_number


async def generate_text_info(df):
    name = str(df['Контрагент'].values[0])
    phone_number = str(int(df['Телефон номер'].values[0]))
    date = str(df['Период, день'].values[0])
    
    ostatok = str(await add_delimeters(df['Входящий остаток'].values[0]))
    prixod = str(await add_delimeters(df['Приход'].values[0]))
    rasxod = str(await add_delimeters(df['Расход'].values[0]))
    saldo = str(await add_delimeters(df['Исходящее сальдо'].values[0]))
    backticked_text = "Имя: " + name + "\n" + \
                      "Тел.: " + phone_number + "\n"  + \
                      "Дата: " + date + "\n"  + \
                      "Входящий остаток: " + ostatok + "\n"  + \
                      "Приход: " + prixod + "\n"  + \
                      "Погашение: " + rasxod + "\n"  + \
                      "Исходящий остаток: " + saldo + "\n"
    return backticked_text


async def generate_info(phone_number):
    df = pd.read_excel(db_filepath)
    mask = df["Телефон номер"] == 943770328
    df = df[mask]
    df_styled = df.style
    random_uuid = uuid.uuid4()
    table_img_path = os.path.join('temp', f'{random_uuid}.png')
    dfi.export(df_styled, table_img_path)
    return table_img_path

async def respond_for_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat.id
    ## getting contact object
    contact = update.message.contact
    phone_number = str(contact.phone_number)[3:]
    cache[chat_id] = phone_number
    if not await check_exist(phone_number):
        await update.message.reply_text(f'У вас нет записей :)')
        return ConversationHandler.END
    else:
        df = await last_record(phone_number)
        last_record_text = await generate_text_info(df) 
        last_record_text = "<i>Последняя запись:</i>\n\n" + last_record_text
        await update.message.reply_text(last_record_text, parse_mode=ParseMode.HTML)
        await update.message.reply_text(f'Отправьте дату в формате: <strong>ДД.ММ.ГГГГ</strong>', parse_mode=ParseMode.HTML)

    return DATE


async def send_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ## getting contact object
    date = update.message.text
    chat_id = update.message.chat.id
    phone_number = cache[chat_id]
    if not await check_exist(phone_number):
        await update.message.reply_text(f'У вас нет записей :)')
        return ConversationHandler.END
    else:
        df = await check_by_date(date, chat_id)
        if len(df) == 0:
            text = "На эту дату записей нет :("
        else:
            text = await generate_text_info(df)
        await update.message.reply_text(text)
    return DATE


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Саламалекум тогда.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


date_pattern = r"^\d{2}\.\d{2}\.\d{4}$"
conv_show_info = ConversationHandler(  
        entry_points=[CommandHandler("start", start)],
        states={
            CONTACT: [MessageHandler(filters.CONTACT, respond_for_contact),
                      MessageHandler(~filters.CONTACT, start)],
            DATE: [MessageHandler(filters.Regex(date_pattern), send_info)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )