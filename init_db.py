import sqlite3

def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # 订单表
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        transaction_time TEXT DEFAULT CURRENT_TIMESTAMP,
                        wallet_address TEXT NOT NULL,
                        guider_id INTEGER NOT NULL,
                        tour_type TEXT NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT NOT NULL
                    )''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database initialized.")
