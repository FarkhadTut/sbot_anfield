from telegram.ext import (
    ApplicationBuilder, 
    )

from action.conversations import (
    main_conversation,
    )

from telegram import (
    Update,
)
from config import telegram_token
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

app = ApplicationBuilder().token(telegram_token()).build()
app.add_handler(main_conversation)
app.run_polling(allowed_updates=Update.ALL_TYPES)