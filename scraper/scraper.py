import requests
from bs4 import BeautifulSoup
import psycopg2
import time
import os

def main():
    conn = psycopg2.connect(
        host="db",
        port="5432",
        database=os.environ.get('POSTGRES_DB'),
        user=os.environ.get('POSTGRES_USER'),
        password=os.environ.get('POSTGRES_PASSWORD')
    )

    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS my_table (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    rating TEXT,
                    count TEXT,
                    tags TEXT)""")

    url = 'https://codeforces.com/problemset?order=BY_SOLVED_DESC&locale=ru'
    response = requests.get(url)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find('div', {'class': 'pagination'})
    pages = int(pagination.find_all('li')[-2].text)

    data = []

    for page in range(1, pages+1):
        response = requests.get(f'https://codeforces.com/problemset/page/{page}?order=BY_SOLVED_DESC&locale=ru')
        html = response.content

        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'problems'})


        for tr in table.find_all('tr'):
            row = []
            for i, td in enumerate(tr.find_all('td')):
                if i==1:
                    name_tags = td.text.strip().split("\n\n\n")
                    row.append(" ".join(name_tags[0].split()))
                    if len(name_tags)>1:
                        tags =  " ".join(name_tags[1].split()).replace('\r', '').replace('\n', '').strip().split(',')
                    row.append(tags)
                    continue
                if i==2:
                    continue
                if i==4:
                    row.append(td.text.strip()[1:])
                    continue
                row.append(td.text.strip())     
            if row:
                data.append(row)


    for row in data:
        cursor.execute("SELECT * FROM my_table WHERE id = %s", (row[0],))
        result = cursor.fetchone()
        if not result:
            cursor.execute("INSERT INTO my_table (id, name, rating, count, tags) VALUES (%s, %s, %s, %s, %s)", (row[0], row[1], row[3], row[4], ', '.join(row[2])))
            conn.commit()

    cursor.close()
    conn.close()



if __name__ == "__main__":
    while True:
        main()
        time.sleep(3600)

