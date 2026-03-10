#!/usr/bin/env python3
import vk_api
import feedparser
import schedule
import time
import requests
from datetime import datetime
import random

# ================= НАСТРОЙКИ =================
VK_TOKEN = "мойтокен"
GROUP_ID = ID_сообщества
POST_TIME = "17:36"    # время рассылки
# =============================================

# Стабильные RSS источники
RSS_SOURCES = [
    "https://tass.ru/rss/v2.xml"
]

def fetch_news():
    """Получает 5 последних новостей из ТАСС"""
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get("https://tass.ru/rss/v2.xml", headers=headers, timeout=10)

        if response.status_code != 200:
            return None
        feed = feedparser.parse(response.content)
        if not feed.entries:
            return None
        message = f"📰 ТАСС | Новости дня\n{datetime.now().strftime('%d.%m.%Y')}\n\n"

        for entry in feed.entries[:5]:
            title = entry.title
            summary = entry.get("summary", "")
            summary = summary.replace("<p>", "").replace("</p>", "")
            link = entry.link
            message += (
                f"🔹 {title}\n"
                f"{summary}\n\n"
                f"🔗 Источник:\n{link}\n\n"
            )
        return message
    except Exception as e:
        print("Ошибка получения новостей:", e)
        return None

def get_all_subscribers(vk, group_id):
    """Возвращает список user_id подписчиков, которые можно написать"""
    try:
        members = vk.groups.getMembers(group_id=group_id, fields="id")
        subscribers = members.get('items', [])
        # Преобразуем в числа, если возвращается словарь
        result = []
        for user in subscribers:
            if isinstance(user, dict):
                result.append(user['id'])
            else:
                result.append(user)
        return result
    except Exception as e:
        print("❌ Ошибка получения подписчиков:", e)
        return []

def send_daily_news():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Отправка новостей...")

    news_message = fetch_news()
    if not news_message:
        print("❌ Новости не получены")
        return
    try:
        vk_session = vk_api.VkApi(token=VK_TOKEN)
        vk = vk_session.get_api()
        subscribers = get_all_subscribers(vk, GROUP_ID)
        print(f"ℹ️ Подписчиков для рассылки: {len(subscribers)}")

        sent_count = 0
        for user_id in subscribers:
            try:
                vk.messages.send(
                    user_id=user_id,
                    message=news_message,
                    random_id=random.randint(1, 999999999)
                )
                sent_count += 1
            except Exception as e:
                # если пользователь не разрешил сообщения — пропускаем
                print(f"⚠ Не удалось отправить {user_id}: {e}")
                continue
        print(f"✅ Новости отправлены {sent_count} пользователям")

    except Exception as e:
        print("❌ Ошибка рассылки:", e)


def main():
    print("🚀 Бот запущен")
    print(f"⏰ Время рассылки: {POST_TIME}")

    schedule.every().day.at(POST_TIME).do(send_daily_news)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
