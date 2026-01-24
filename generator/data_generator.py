import time
import random
import psycopg2
from datetime import datetime


def connect_db():
    try:
        conn = psycopg2.connect(
            host="weather-postgres",
            database="weather_db",
            user="weather_user",
            password="weather_pass",
            port="5432"
        )
        print("Подключено к базе данных")
        return conn
    except:
        print("Ожидание базы данных...")
        time.sleep(2)
        return connect_db()



def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            station_id INTEGER,
            temperature FLOAT,
            humidity INTEGER,
            pressure FLOAT,
            wind_speed FLOAT,
            wind_direction VARCHAR(10),
            conditions VARCHAR(50),
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Таблица создана")


def get_temperature():
    hour = datetime.now().hour

    if hour < 6:  # ночь (0-6)
        temp = 5 + random.uniform(-5, 5)
    elif hour < 12:  # утро (6-12)
        temp = 15 + random.uniform(-5, 5)
    elif hour < 18:  # день (12-18)
        temp = 22 + random.uniform(-7, 7)
    else:
        temp = 18 + random.uniform(-8, 8)

    return round(temp, 1)


def get_humidity(temp):
    if temp > 25:
        return random.randint(20, 50)
    elif temp > 15:
        return random.randint(40, 70)
    else:
        return random.randint(60, 90)


def main():
    create_table()

    count = 0
    while True:
        try:
            conn = connect_db()
            cursor = conn.cursor()

            station = random.randint(1, 3)  #3 станции
            temp = get_temperature()
            humidity = get_humidity(temp)
            pressure = round(1013 + random.uniform(-20, 20), 1)
            wind_speed = round(random.uniform(0, 12), 1)
            wind_dir = random.choice(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'])

            if temp < 0:
                conditions = "Мороз"
            elif temp < 5:
                conditions = "Очень холодно"
            elif temp < 10:
                conditions = "Холодно"
            elif temp < 15:
                conditions = "Прохладно"
            elif temp < 20:
                conditions = "Тепло"
            elif temp < 25:
                conditions = "Жарко"
            else:
                conditions = "Очень жарко"

            cursor.execute("""
                INSERT INTO weather 
                (station_id, temperature, humidity, pressure, wind_speed, wind_direction, conditions)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (station, temp, humidity, pressure, wind_speed, wind_dir, conditions))

            conn.commit()
            cursor.close()
            conn.close()

            count += 1
            if count % 10 == 0:
                print(f"[{datetime.now().strftime('%H:%M')}] Записей: {count}, Температура: {temp}°C")

            time.sleep(1)

        except Exception as e:
            print(f"Ошибка: {e}")
            time.sleep(2)


if __name__ == "__main__":
    main()