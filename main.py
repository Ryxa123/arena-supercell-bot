import logging
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

NEWS_SOURCES = [
    "https://brawlstars.com/en/blog/feed",
    "https://clashroyale.com/blog/feed"
]

seen_links = set()

def fetch_news():
    items = []
    for url in NEWS_SOURCES:
        try:
            resp = requests.get(url)
            content = resp.text
            entries = content.split("<item>")[1:]
            for entry in entries:
                title = entry.split("<title>")[1].split("</title>")[0]
                link = entry.split("<link>")[1].split("</link>")[0]
                if link not in seen_links:
                    seen_links.add(link)
                    items.append((title, link))
        except Exception as e:
            logging.error(f"Ошибка при получении новостей: {e}")
    return items

def send_news(context: CallbackContext):
    bot: Bot = context.bot
    chat_id = context.job.context
    news = fetch_news()
    for title, link in news:
        bot.send_message(chat_id=chat_id, text=f"**{title}**\n{link}", parse_mode="Markdown")

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Я буду присылать тебе свежие новости из мира Supercell.")
    chat_id = update.message.chat_id
    context.job_queue.run_repeating(send_news, interval=3600, first=1, context=chat_id)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()
