import sqlite3
import pandas as pd


db_path = 'database.db'


def create_db():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            phone_number TEXT,
            first_name TEXT,
            last_name TEXT,
            username TEXT,
            last_interaction TEXT,
            last_dialog TEXT,
            dialog_state TEXT DEFAULT 'start',
            dialog_score INTEGER DEFAULT 0,
            last_question TEXT,
            last_qa TEXT,
            last_time_duration INTEGER DEFAULT 0,
            last_num_token INTEGER DEFAULT 0,
            num_queries INTEGER DEFAULT 0,
            buffer_memory TEXT None,
            tg_source INTEGER DEFAULT 1
        )
        '''
    )

    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS docs (
            doc_id TEXT PRIMARY KEY,
            doc_name TEXT,
            last_update TEXT
        )
        '''
    )

    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            score_name TEXT,
            score_text TEXT,
            score INTEGER,
            time_duration INTEGER,
            date_estimate TEXT,
            num_token INTEGER,
            tg_source INTEGER DEFAULT 1
        )
        '''
    )

    connection.commit()
    connection.close()


def add_columns_if_not_exist():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]

    new_columns = [
        ("buffer_memory", "TEXT", None),
        ("tg_source", "INTEGER", 1)
    ]

    for column_name, column_type, default_value in new_columns:
        if column_name not in columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")

    cursor.execute("PRAGMA table_info(history)")
    columns = [info[1] for info in cursor.fetchall()]

    new_columns = [
        ("tg_source", "INTEGER", 1)
    ]

    for column_name, column_type, default_value in new_columns:
        if column_name not in columns:
            cursor.execute(f"ALTER TABLE history ADD COLUMN {column_name} {column_type} DEFAULT {default_value}")
    connection.commit()
    connection.close()


def add_user(user_data):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, phone_number, first_name, last_name, username, last_interaction, "
        "last_dialog, dialog_state, dialog_score, last_question, last_qa, last_time_duration, last_num_token, "
        "num_queries, buffer_memory, tg_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        user_data,
    )

    connection.commit()
    connection.close()


def add_doc(user_data):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        '''INSERT OR IGNORE INTO docs (doc_id, doc_name, last_update) VALUES (?, ?, ?);''',
        user_data
    )

    connection.commit()
    connection.close()


def add_history(history_data):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO history (user_id , score_name, score_text, score, time_duration, date_estimate, "
        "num_token, tg_source) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        history_data,
    )

    connection.commit()
    connection.close()


def get_buffer_memory(user_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT buffer_memory FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    connection.close()

    return result


def update_buffer_memory(user_id, buffer_memory):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET buffer_memory = ? WHERE user_id = ?",
        (buffer_memory, user_id),
    )

    connection.commit()
    connection.close()


def get_user_entry(user_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    connection.close()

    return True if result else False


def get_user(user_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    connection.close()

    return result if result else [i for i in range(11)]


def get_doc_entry(doc_id):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM docs WHERE doc_id = ?", (doc_id,))
    result = cursor.fetchone()
    connection.close()

    return True if result else False


def update_last_interaction(user_id, last_interaction):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET last_interaction = ? WHERE user_id = ?",
        (last_interaction, user_id),
    )

    connection.commit()
    connection.close()


def update_last_dialog(user_id, last_dialog):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET last_dialog = ? WHERE user_id = ?",
        (last_dialog, user_id),
    )

    connection.commit()
    connection.close()


def update_last_update(doc_id, last_update):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE docs SET last_update = ? WHERE doc_id = ?",
        (last_update, doc_id),
    )

    connection.commit()
    connection.close()


def update_dialog_score(user_id, dialog_score):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET dialog_score = ? WHERE user_id = ?",
        (dialog_score, user_id),
    )

    connection.commit()
    connection.close()


def update_dialog_state(user_id, dialog_state):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET dialog_state = ? WHERE user_id = ?",
        (dialog_state, user_id),
    )

    connection.commit()
    connection.close()


def update_qa(user_id, last_qa):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET last_question= ?, last_qa = ? WHERE user_id = ?",
        (last_qa[0], last_qa[1], user_id),
    )

    connection.commit()
    connection.close()


def update_last_num_token(user_id, num_token):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET last_num_token = ? WHERE user_id = ?",
        (num_token, user_id),
    )

    connection.commit()
    connection.close()


def update_num_queries(user_id, num_queries):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET num_queries = ? WHERE user_id = ?",
        (num_queries, user_id),
    )

    connection.commit()
    connection.close()


def update_last_time_duration(user_id, time_duration):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute(
        "UPDATE users SET last_time_duration = ? WHERE user_id = ?",
        (time_duration, user_id),
    )

    connection.commit()
    connection.close()


def get_all_users():
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users")
    # Query all records from the users table
    result = cursor.fetchall()
    connection.close()

    return result


def get_df_users():
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)

    # Query all records from the users table
    result = pd.read_sql_query("SELECT * FROM users", connection)
    connection.close()

    return result


def get_df_docs():
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)

    # Query all records from the users table
    result = pd.read_sql_query("SELECT * FROM docs", connection)
    connection.close()

    return result


def get_df_history():
    # Connect to the SQLite database
    connection = sqlite3.connect(db_path)

    # Query all records from the users table
    result = pd.read_sql_query("SELECT * FROM history", connection)
    connection.close()

    return result

# if __name__ == '__main__':
#     db_path = '../database.db'
#     df = get_df_users()
#     df.to_csv("users.csv")
#     df.to_excel("users.xlsx", index=False)
