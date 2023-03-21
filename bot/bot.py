import telebot
import psycopg2
from telebot import types
import os


conn = psycopg2.connect(
    database=os.environ.get('POSTGRES_DB'),
    user=os.environ.get('POSTGRES_USER'),
    password=os.environ.get('POSTGRES_PASSWORD'),
    host="db",
    port="5432",
)


bot = telebot.TeleBot(os.environ.get('TOKEN'))


@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет!  Напиши мне сложность и теги через пробел или id задачи в формате 12x")


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text = message.text.split()
    cur = conn.cursor()

    if text[0]=='tags':
        cur.execute(f"""
            SELECT DISTINCT trim(tag) AS tag
            FROM (
            SELECT unnest(string_to_array(tags, ',')) AS tag
            FROM my_table) AS subquery""")
    elif len(text)>1:
        tags = ' '.join(text[1:])
        cur.execute(f"""
            SELECT id, name, rating, count, tags
            FROM my_table
            WHERE rating = '{text[0]}' AND tags LIKE '{tags}'
            LIMIT 10""")
    elif text[0].isdigit():
        cur.execute(f"""
            SELECT id, name, rating, count, tags
            FROM my_table
            WHERE rating = '{text[0]}'
            LIMIT 10""")
    else:
        cur.execute(f"""
            SELECT id, name, rating, count, tags
            FROM my_table
            WHERE id = '{text[0]}'
            LIMIT 10""")
    
    rows = cur.fetchall()
    cur.close()
    if rows:
        response = "Вот что я нашел:\n\n"
        if len(rows[0])>2:
            for row in rows:
                response += f"{row[0]}\n{row[1]}\nСложность: {row[2]}\nhttps://codeforces.com/problemset/problem/{row[0][:-1]}/{row[0][-1]}\n\n"
        else:
            for row in rows:
                response += row[0] +'\n'
    else:
        response = "Ничего не нашел :("

    bot.send_message(message.chat.id, response)

bot.polling()
