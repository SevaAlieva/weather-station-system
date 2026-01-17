import time
import random
import psycopg2

DB_SETTINGS = {
    "dbname": "weather_db",
    "user": "weather_user",
    "password": "weather_pass",
    "host": "postgres",
    "port": 5432
}

def create_table():
    #создание таблицы в бд
    conn = psycopg2.connect(**DB_SETTINGS)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            temperature FLOAT,
            humidity INT,
            pressure FLOAT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("Таблица создана")

#генерация погодных даннвх
def generate_weather_data():
    temperature = round(random.uniform(10, 30), 2)  # 10-30°C
    humidity = random.randint(40, 80)  # 40-80%
    pressure = round(random.uniform(1000, 1020), 2)  # 1000-1020 гПа

    return temperature, humidity, pressure


def save_to_db(temperature, humidity, pressure):
    conn = psycopg2.connect(**DB_SETTINGS)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO weather (temperature, humidity, pressure) VALUES (%s, %s, %s)",
        (temperature, humidity, pressure)
    )

    conn.commit()
    cursor.close()
    conn.close()


def main():
    print("Запуск генератора погодных данных...")

    create_table()

    count = 0
    try:
        while True:
            count += 1

            temp, humidity, pressure = generate_weather_data()

            save_to_db(temp, humidity, pressure)

            print(f"Запись {count}: {temp}°C, {humidity}%, {pressure}гПа")

            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\nОстановлено. Всего записей: {count}")


if __name__ == "__main__":
    main()