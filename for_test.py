import logging

from telegram import Update
from telegram.ext import ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /start command")
    await update.message.reply_text("Здарова бро, я твой помощник!")