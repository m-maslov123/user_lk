from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2 import OperationalError
import json

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов


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
            return {"error": f"Запись с ID {target_id} не найдена"}, 404

        column_names = [desc[0] for desc in cursor.description]
        result = []
        for record in records:
            formatted_record = {col: val for col, val in zip(column_names, record)}
            result.append(formatted_record)

        return json.dumps(result, ensure_ascii=False, default=str)

    except Exception as e:
        print(f"Ошибка выполнения запроса: {e}")
        return {"error": str(e)}, 500
    finally:
        if connection:
            cursor.close()
            connection.close()


@app.route('/get_user_data', methods=['GET'])
def get_user_data():
    try:
        target_id = int(request.args.get('user_id'))
    except (ValueError, TypeError):
        return jsonify({"error": "Неверный формат ID"}), 400

    conn = connect_to_db()
    if not conn:
        return jsonify({"error": "Ошибка подключения к БД"}), 500

    result = fetch_data_by_id(conn, target_id)
    return app.response_class(
        response=result[0] if isinstance(result, tuple) else result,
        status=result[1] if isinstance(result, tuple) else 200,
        mimetype='application/json'
    )
# Транзакция
@app.route('/transaction', methods=['POST'])
def make_transaction():
    """Новый метод для выполнения транзакции"""
    data = request.get_json()
    amount = data.get('amount', 1000)

    try:
        # 1. Получаем ID пользователя из параметров запроса
        target_id = int(request.args.get('user_id'))
    except (ValueError, TypeError):
        return jsonify({"error": "Неверный формат ID"}), 400

    # 2. Подключаемся к базе данных
    conn = connect_to_db()
    if not conn:
        return jsonify({"error": "Ошибка подключения к БД"}), 500

    try:
        # 3. Создаем курсор и начинаем транзакцию
        cursor = conn.cursor()

        # 4. Проверяем текущий баланс available
        cursor.execute("""
            SELECT available 
            FROM user_data 
            WHERE user_id = %s 
            FOR UPDATE  -- Блокируем запись для обновления
            """, (target_id,))

        current_available = cursor.fetchone()

        if not current_available:
            return jsonify({"error": "Пользователь не найден"}), 404

        if current_available[0] < 1000:
            return jsonify({"error": "Недостаточно средств для выполнения операции"}), 400

        # 5. Выполняем обновление available
        cursor.execute("""
            UPDATE user_data 
            SET available = available - %s 
            WHERE user_id = %s
            """, (amount, target_id,))

        # 6. Выполняем обновление cash
        cursor.execute("""
            UPDATE user_data 
            SET cash = cash + %s 
            WHERE user_id = %s
            """, (amount, target_id,))

        # 7. Фиксируем изменения в базе данных
        conn.commit()

        # 8. Возвращаем обновленные данные
        cursor.execute("SELECT * FROM user_data WHERE user_id = %s", (target_id,))
        updated_data = cursor.fetchone()
        column_names = [desc[0] for desc in cursor.description]

        return jsonify({
            "message": "Транзакция успешно выполнена",
            "data": dict(zip(column_names, updated_data))
        })

    except DatabaseError as e:
        # Откатываем транзакцию при ошибке
        conn.rollback()
        print(f"Ошибка базы данных: {e}")
        return jsonify({"error": "Ошибка выполнения транзакции"}), 500

    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500

    finally:
        # Всегда закрываем соединение
        if conn:
            cursor.close()
            conn.close()

# Авторизация
@app.route('/auth', methods=['POST'])
def authenticate():
    try:
        data = request.get_json()
        login = data['login']
        password = data['password']

        conn = connect_to_db()
        cursor = conn.cursor()

        # Ищем пользователя
        cursor.execute("""
            SELECT id 
            FROM credentials 
            WHERE login = %s AND password = %s
        """, (login, password))

        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Invalid credentials"}), 401

        return jsonify({"user_id": user[0]})

    except Exception as e:
        print(f"Auth error: {e}")
        return jsonify({"error": "Authentication failed"}), 500
    finally:
        if 'conn' in locals() and conn:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True, port=5000)