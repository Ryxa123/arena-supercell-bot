import logging
import requests
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, JobQueue
import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

NEWS_SOURCES = [
   # 🟢 ОФИЦИАЛЬНЫЕ ИГРЫ SUPERСELL
    "https://brawlstars.com/en/blog/feed",
    "https://clashroyale.com/blog/feed",
    "https://clashofclans.com/blog/rss.xml",
    "https://boombeach.com/en/blog/rss.xml",
    "https://hayday.com/en/blog/rss.xml",
    "https://supercell.com/en/games/squadbusters/blog/",

    # 🔵 YOUTUBE – СОЗДАТЕЛИ КОНТЕНТА
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCqod5rDCIaa1X_jk2WcgKTA",  # KairosTime
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCs2YJwD5oFnrSJY5N3aV5Fw",  # Lex
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCpGzT4wecuWM0BH9mPiulXg",  # Orange Juice
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCN3ypF4OU3TXI4X3W6BeXZw",  # Nubbz3
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCl_m_4Le3Y5eoVzJwM4vWgA",  # Ray Brawl Stars
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCLz0UlfPBZ7jyDrc-LNLwFg",  # Relyt
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCYLNjhOJ8tG0wiEs4fRyWfg",  # Ark – Clash Royale
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCdZz4NBFPpj5vZIcXW6cfhg",  # Chief Pat

    # 🔴 REDDIT – ОБСУЖДЕНИЯ, СЛИВЫ, БАГИ
    "https://rsshub.app/reddit/r/BrawlStars",
    "https://rsshub.app/reddit/r/BrawlStars/search?q=leak&sort=new",
    "https://rsshub.app/reddit/r/ClashRoyale",
    "https://rsshub.app/reddit/r/ClashRoyale/search?q=update&sort=new",
    "https://rsshub.app/reddit/r/ClashOfClans",
    "https://rsshub.app/reddit/user/BrawlStarsLeaks/submitted",
    "https://rsshub.app/reddit/user/ClashRoyaleDev/submitted",

    # 🟡 TWITTER – SLASH RSS
    "https://nitter.net/BrawlStars/rss",
    "https://nitter.net/ClashRoyale/rss",
    "https://nitter.net/ClashOfClans/rss",
    "https://nitter.net/KairosTimeGaming/rss",
    "https://nitter.net/OJeveryday/rss",
    "https://nitter.net/BrawlLeaks/rss",
    "https://nitter.net/BrawlStarsNews/rss",

    # 🟣 САЙТЫ И АГРЕГАТОРЫ
    "https://www.brawlify.com/blog/feed",
    "https://starpowerlist.com/rss",
    "https://clashspot.net/blog/rss",
    "https://clash.world/feed/",
    "https://clash-champions.com/feed/",
    "https://royaleapi.com/blog/rss",
    "https://www.clashtrack.com/rss/news",
    "https://brawlnews.ru/feed",
    "https://clashnews.ru/feed",
    "https://metahub.gg/feed",

    # ⚫ АЛЬТЕРНАТИВНЫЕ ПЛАТФОРМЫ
    "https://rss.app/feeds/YOuTube/KairosTime",
    "https://rss.app/feeds/YouTube/LexBS",
    "https://rsshub.app/github/Supercell/BrawlStars/releases",
    "https://rsshub.app/github/Supercell/ClashRoyale/releases"
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
    context.job_queue.run_repeating(send_news, interval=30, first=1, context=chat_id)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    updater.start_polling()
    updater.idle()
