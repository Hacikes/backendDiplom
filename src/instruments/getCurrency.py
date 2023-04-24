#(f'postgresql+asyncpg://getCurrency:getCurrency@localhost:5432/test')

import requests
import psycopg2
import time

def get_exchange_rate(pair):
    url = f"https://api.exchangeratesapi.io/latest?symbols={pair}&base=RUB"
    response = requests.get(url)
    data = response.json()
    if "rates" in data:
        return data["rates"].get(pair)
    else:
        return None

def insert_exchange_rate(pair, rate):
    conn = psycopg2.connect(
        host="localhost",
        database="test",
        user="getCurrency",
        password="getCurrency"
    )

    cur = conn.cursor()

    cur.execute("INSERT INTO exchange_rates (currency_pair, rate) VALUES (%s, %s)", (pair, rate))

    conn.commit()

    cur.close()
    conn.close()

while True:
    pairs = ["EURRUB", "USDRUB", "GBPRUB", "HKDRUB"]

    for pair in pairs:
        rate = get_exchange_rate(pair)
        if rate is not None:
            insert_exchange_rate(pair, rate)

    try:
        time.sleep(3600) # Обновляем каждый час
    except KeyboardInterrupt:
        print("Программа остановлена вручную")
        break
