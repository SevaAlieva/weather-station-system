import psycopg2
import time
import random
from datetime import datetime
import os
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_connection(max_retries=30, delay=2):
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "postgres"),
                database=os.getenv("POSTGRES_DB", "weather_db"),
                user=os.getenv("POSTGRES_USER", "weather_user"),
                password=os.getenv("POSTGRES_PASSWORD", "weather_pass"),
                port=os.getenv("DB_PORT", "5432"),
                connect_timeout=5
            )
            logger.info("Подключение к БД установлено")
            return conn
        except Exception as e:
            logger.warning(f"Попытка {i + 1}/{max_retries}: БД еще не готова: {e}")
            if i == max_retries - 1:
                logger.error("Не удалось подключиться к PostgreSQL")
                raise
            time.sleep(delay)
    return None


def create_table(conn):
    sql = """
    CREATE TABLE IF NOT EXISTS weather_measurements (
        id SERIAL PRIMARY KEY,
        station_id INTEGER NOT NULL,
        temperature NUMERIC(4,2),
        humidity INTEGER,
        pressure NUMERIC(6,2),
        wind_speed NUMERIC(5,2),
        wind_direction VARCHAR(3),
        weather_conditions VARCHAR(50),
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_recorded_at ON weather_measurements(recorded_at);
    CREATE INDEX IF NOT EXISTS idx_station_id ON weather_measurements(station_id);
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
            conn.commit()
        logger.info("Таблица 'weather_measurements' готова")
    except Exception as e:
        logger.error(f"Ошибка создания таблицы: {e}")
        conn.rollback()

#генерация погодных данных
def generate_weather_data():
    station_id = random.randint(1, 3)  # 3 разные станции

    #температура в зависимости от времени суток
    hour = datetime.now().hour
    if 0 <= hour < 6:  # Ночь
        base_temp = 5 + random.uniform(-3, 3)
    elif 6 <= hour < 12:  # Утро
        base_temp = 15 + random.uniform(-2, 2)
    elif 12 <= hour < 18:  # День
        base_temp = 22 + random.uniform(-3, 3)
    else:  # Вечер
        base_temp = 18 + random.uniform(-2, 2)

    temperature = round(base_temp, 2)

    if temperature > 25:
        humidity = random.randint(30, 50)
    elif temperature > 15:
        humidity = random.randint(50, 70)
    else:
        humidity = random.randint(70, 90)

    pressure = round(1013 + random.uniform(-20, 20), 2)

    wind_speed = round(random.uniform(0, 15), 2)

    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    wind_direction = random.choice(directions)

    if temperature < 0:
        if humidity > 80:
            conditions = "Snow"
        else:
            conditions = "Clear, frosty"
    elif temperature < 10:
        if humidity > 85:
            conditions = "Fog"
        elif wind_speed > 10:
            conditions = "Windy, cool"
        else:
            conditions = "Cloudy"
    elif temperature < 25:
        if humidity > 80:
            conditions = "Rain"
        elif humidity < 30:
            conditions = "Sunny, dry"
        else:
            conditions = "Partly cloudy"
    else:
        if humidity > 70:
            conditions = "Hot and humid"
        else:
            conditions = "Hot and dry"

    return (station_id, temperature, humidity, pressure, wind_speed, wind_direction, conditions)


def main():
    conn = get_db_connection()
    create_table(conn)

    counter = 0
    try:
        while True:
            try:
                if conn.closed:
                    logger.warning("Соединение разорвано, переподключаемся...")
                    conn = get_db_connection(max_retries=5, delay=1)

                data = generate_weather_data()
                with conn.cursor() as cur:
                    sql = """
                    INSERT INTO weather_measurements 
                    (station_id, temperature, humidity, pressure, wind_speed, wind_direction, weather_conditions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    cur.execute(sql, data)
                    conn.commit()

                counter += 1

                if counter % 10 == 0:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    logger.info(f"[{timestamp}] Записей: {counter}, "
                                f"Станция {data[0]}, {data[6]}, темп: {data[1]}°C")

                time.sleep(1)

            except (psycopg2.OperationalError, psycopg2.InterfaceError) as e:
                logger.error(f"Ошибка БД: {e}")
                time.sleep(2)
                try:
                    if conn:
                        conn.close()
                    conn = get_db_connection(max_retries=5, delay=1)
                except:
                    pass

    except KeyboardInterrupt:
        logger.info(f"\n\nОстановлено. Всего записей: {counter}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
    finally:
        if conn and not conn.closed:
            conn.close()
            logger.info("Подключение к БД закрыто")


if __name__ == "__main__":
    main()