import psycopg2
from psycopg2 import OperationalError
import json  # Добавляем импорт модуля JSON


def connect_to_db():
    try:
        conn = psycopg2.connect(
            database="DB_SERVER",
            user="postgres",
            password="0000",
            host="localhost",
            port="5432"
        )
        return conn
    except OperationalError as e:
        print(f"Ошибка подключения: {e}")
        return None


def fetch_data_by_id(connection, target_id):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user_data LIMIT 0")
        first_column = cursor.description[0][0]

        cursor.execute(
            f"SELECT * FROM user_data WHERE {first_column} = %s",
            (target_id,)
        )
        records = cursor.fetchall()

        if not records:
            print(f"Запись с ID {target_id} не найдена")
            return

        column_names = [desc[0] for desc in cursor.description]

        # Собираем данные в список словарей
        result = []
        for record in records:
            formatted_record = {col: val for col, val in zip(column_names, record)}
            result.append(formatted_record)

        # Конвертируем в JSON и выводим
        json_output = json.dumps(
            result,
            ensure_ascii=False,  # Для корректного отображения кириллицы
            indent=2,  # Форматирование с отступами
            default=str  # Конвертация нестандартных типов в строку
        )
        print(json_output)

    except Exception as e:
        print(f"Ошибка выполнения запроса: {e}")
        # Можно вернуть JSON с ошибкой вместо обычного текста
        # print(json.dumps({"error": str(e)}))
    finally:
        if connection:
            cursor.close()
            connection.close()


# Остальной код без изменений
def main():
    user_input = input("Введите 'start' для начала работы: ").strip().lower()

    if user_input != "start":
        print("Неверная команда")
        return

    try:
        target_id = int(input("Введите ID для поиска: "))
    except ValueError:
        print("ID должен быть целым числом")
        return

    conn = connect_to_db()
    if conn:
        fetch_data_by_id(conn, target_id)


if __name__ == "__main__":
    main()