# baza_sql.py
"""
Модули кор бо базаи маълумот SQLite
Ҳама амалҳои хондан, навиштан ва ҳисобкунӣ дар ин ҷо ҷой гирифтаанд
"""
import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_PATH, ALLOWED_USER_ID

def init_database():
    """
    Сохтани ҷадвалҳои зарурӣ ҳангоми бори аввал оғоз кардан
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # Ҷадвали моҳҳои корӣ
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS months (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        month_year TEXT NOT NULL,
        start_date DATE NOT NULL,
        end_date DATE,
        is_closed BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, month_year)
    )
    ''')

    # Ҷадвали амалиётҳои молиявӣ
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        month_id INTEGER NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('income', 'expense', 'p2p')),
        amount REAL NOT NULL CHECK(amount > 0),
        reason TEXT DEFAULT 'Дигар',
        profit REAL DEFAULT 0,
        buy_rate REAL,
        sell_rate REAL,
        transaction_date DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (month_id) REFERENCES months(id) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()

def get_current_month_id(user_id=ALLOWED_USER_ID):
    """
    Гирифтани рақами моҳи ҷорӣ, агар мавҷуд набошад — ба таври худкор сохта мешавад
    """
    today = datetime.today()
    month_year = today.strftime("%Y-%m")
    start_date = today.replace(day=1).strftime("%Y-%m-%d")

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id FROM months WHERE user_id = ? AND month_year = ? AND is_closed = 0
    ''', (user_id, month_year))

    result = cursor.fetchone()

    if result:
        month_id = result[0]
    else:
        # Баста кардани моҳҳои пешина агар мавҷуд бошанд
        cursor.execute('''
            UPDATE months 
            SET is_closed = 1, end_date = DATE(start_date, '+1 month', '-1 day')
            WHERE user_id = ? AND is_closed = 0
        ''', (user_id,))
        # Сохтани моҳи нав
        cursor.execute('''
            INSERT INTO months (user_id, month_year, start_date)
            VALUES (?, ?, ?)
        ''', (user_id, month_year, start_date))
        conn.commit()
        month_id = cursor.lastrowid

    conn.close()
    return month_id

# --- Функсияҳои сабти маълумот ---
def add_income(amount, reason="Дигар", date=None, user_id=ALLOWED_USER_ID):
    """
    Сабти даромад ба базаи маълумот
    """
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")
    
    month_id = get_current_month_id(user_id)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transactions (user_id, month_id, type, amount, reason, transaction_date)
        VALUES (?, ?, 'income', ?, ?, ?)
    ''', (user_id, month_id, round(amount, 2), reason, date))

    conn.commit()
    conn.close()
    return True

def add_expense(amount, reason="Дигар", date=None, user_id=ALLOWED_USER_ID):
    """
    Сабти хароҷот ба базаи маълумот
    """
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")
    
    month_id = get_current_month_id(user_id)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transactions (user_id, month_id, type, amount, reason, transaction_date)
        VALUES (?, ?, 'expense', ?, ?, ?)
    ''', (user_id, month_id, round(amount, 2), reason, date))

    conn.commit()
    conn.close()
    return True

def add_p2p_transaction(buy_amount, buy_rate, sell_rate, reason="P2P мубодила", date=None, user_id=ALLOWED_USER_ID):
    """
    Ҳисоб кардан ва сабти амалиёти P2P
    """
    if not date:
        date = datetime.today().strftime("%Y-%m-%d")
    
    usdt = buy_amount / buy_rate
    sell_value = usdt * sell_rate
    profit = round(sell_value - buy_amount, 2)

    month_id = get_current_month_id(user_id)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO transactions 
        (user_id, month_id, type, amount, profit, buy_rate, sell_rate, reason, transaction_date)
        VALUES (?, ?, 'p2p', ?, ?, ?, ?, ?, ?)
    ''', (user_id, month_id, round(buy_amount, 2), profit, round(buy_rate, 2), round(sell_rate, 2), reason, date))

    conn.commit()
    conn.close()

    return {
        "usdt": round(usdt, 2),
        "sell_value": round(sell_value, 2),
        "profit": profit
    }

# --- Функсияҳои гирифтани ҳисоботҳо ---
def get_daily_report(user_id=ALLOWED_USER_ID):
    """
    Гирифтани ҳисоботи рӯзона
    """
    today = datetime.today().strftime("%Y-%m-%d")
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='p2p' THEN profit ELSE 0 END), 0)
        FROM transactions
        WHERE user_id = ? AND transaction_date = ?
    ''', (user_id, today))

    income, expense, p2p_profit = cursor.fetchone()
    conn.close()

    return {
        "date": today,
        "income": round(income, 2),
        "expense": round(expense, 2),
        "p2p_profit": round(p2p_profit, 2),
        "net": round(income - expense + p2p_profit, 2)
    }

def get_weekly_report(user_id=ALLOWED_USER_ID):
    """
    Гирифтани ҳисоботи ҳафтаина
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=7)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='p2p' THEN profit ELSE 0 END), 0)
        FROM transactions
        WHERE user_id = ? AND transaction_date BETWEEN ? AND ?
    ''', (user_id, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))

    income, expense, p2p_profit = cursor.fetchone()
    conn.close()

    return {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "p2p_profit": round(p2p_profit, 2),
        "net": round(income - expense + p2p_profit, 2)
    }

def get_monthly_report(user_id=ALLOWED_USER_ID):
    """
    Гирифтани ҳисоботи моҳона
    """
    month_id = get_current_month_id(user_id)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0),
            COALESCE(SUM(CASE WHEN type='p2p' THEN profit ELSE 0 END), 0),
            COUNT(*)
        FROM transactions
        WHERE user_id = ? AND month_id = ?
    ''', (user_id, month_id))

    income, expense, p2p_profit, count = cursor.fetchone()
    conn.close()

    return {
        "income": round(income, 2),
        "expense": round(expense, 2),
        "p2p_profit": round(p2p_profit, 2),
        "net": round(income - expense + p2p_profit, 2),
        "transactions_count": count
    }

def get_total_balance(user_id=ALLOWED_USER_ID):
    """
    Гирифтани маблағи умумии боқимонда
    """
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT 
            COALESCE(SUM(CASE WHEN type='income' THEN amount ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN type='expense' THEN amount ELSE 0 END), 0) +
            COALESCE(SUM(CASE WHEN type='p2p' THEN profit ELSE 0 END), 0)
        FROM transactions
        WHERE user_id = ?
    ''', (user_id,))

    total = cursor.fetchone()[0] or 0
    conn.close()
    return round(total, 2)

# Иҷрои сохтани ҷадвалҳо ҳангоми бор шудани модул
init_database()