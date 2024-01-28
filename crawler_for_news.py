
import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2 import Error
from aiogram import Bot, Dispatcher, executor
API_TOKEN = '6864801093:AAFZKVGU6Wo3eaSQM9nrU81DV3LNQ7MjzkM'
if not API_TOKEN:
    raise ValueError("Telegram API token not found")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

async def send_message_to_telegram(message):
    try:
        await bot.send_message(chat_id='-4103413678', text=message)
    except Exception as e:
        print(f"Error sending message: {str(e)}")

async def scrape_website_and_insert(url):
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="6Ea2Df4*fg15eF1cFd33bA555-dF*3DA",
            host="viaduct.proxy.rlwy.net",
            port="25923",
            database="railway"
        )
        cursor = connection.cursor()
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            for article in soup.find_all('article', class_='post'):
                image_tag = article.find('img', class_='img-responsive img-fullwidth thumbnail')
                if image_tag:
                    image_url = image_tag.get('src')
                    title = article.find('h4', class_='entry-title').text.strip()
                    created_at = article.find('span', class_='mb-10 text-gray-darkgray mr-10 font-13').text.strip()
                    content_ = article.find('div', class_='entry-content')
                    content = content_.find('p').text.strip()
                    read_more_link = article.find('a', class_='btn-read-more')['href']
                    cursor.execute("SELECT title FROM news WHERE title = %s", (title,))
                    existing_title = cursor.fetchone()
                    if existing_title:
                        print(f"Skipping duplicate entry: {title}")
                    else:
                        insert_query = """INSERT INTO news (title, body, owner, createdAt, image) 
                                          VALUES (%s, %s, %s, %s, %s)"""
                        record_to_insert = (title, content, read_more_link, created_at, image_url)
                        cursor.execute(insert_query, record_to_insert)
                        connection.commit()
                        message = f"New entry added:\nTitle: {title}\nContent: {content}\nRead more: {read_more_link}"
                        await send_message_to_telegram(message)
        else:
            print(f"Status Code: {response.status_code}")
    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        await send_message_to_telegram(f"Error occurred: {str(error)}")
    finally:
        if connection:
            cursor.close()
            connection.close()

if __name__ == "__main__":
    url = 'https://www.uzpharm-control.uz'
    executor.start(dp, scrape_website_and_insert(url))
