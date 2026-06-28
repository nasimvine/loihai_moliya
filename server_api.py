from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime, date
from pydantic import BaseModel
from config import DATABASE_PATH, CURRENCY

app = FastAPI(title="Системаи ҳисоботи молия")

# Иҷозати пайвастшавӣ аз ҳама ҷо
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Моделҳои маълумот
class IncomeData(BaseModel):
    amount: float
    reason: str = "Дигар"

class ExpenseData(BaseModel):
    amount: float
    reason: str = "Дигар"

class P2PData(BaseModel):
    buy_amount: float
    buy_rate: float
    sell_rate: float

# Пайвастшавӣ ба база
def get_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Эҷоди ҷадвалҳо
def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        reason TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ✅ Саҳифаи асосӣ илова шуд
@app.get("/")
async def root():
    try:
        return FileResponse("sahofai_aval.html")
    except:
        return {
            "status": "ok",
            "message": "✅ Сервери ҳисоботи молия фаъол аст!",
            "api_url": "https://hisoboti-server.onrender.com"
        }

# Пайваст кардани файлҳои статикӣ
app.mount("/static", StaticFiles(directory="."), name="static")

# Нуктаҳои коркарди дархостҳо
@app.post("/income")
def add_income(data: IncomeData):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Маблағ бояд мусбат бошад")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (type, amount, reason) VALUES (?, ?, ?)",
                ("даромад", round(data.amount, 2), data.reason))
    conn.commit()
    conn.close()
    return {"status": "ok", "message": f"✅ Даромад {data.amount} {CURRENCY} сабт шуд"}

@app.post("/expense")
def add_expense(data: ExpenseData):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Маблағ бояд мусбат бошад")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (type, amount, reason) VALUES (?, ?, ?)",
                ("хароҷот", round(data.amount, 2), data.reason))
    conn.commit()
    conn.close()
    return {"status": "ok", "message": f"💸 Хароҷот {data.amount} {CURRENCY} сабт шуд"}

@app.post("/p2p")
def add_p2p(data: P2PData):
    if data.buy_amount <= 0 or data.buy_rate <= 0 or data.sell_rate <= 0:
        raise HTTPException(status_code=400, detail="Ҳама рақамҳо бояд мусбат бошанд")
    usdt = round(data.buy_amount / data.buy_rate, 2)
    profit = round(usdt * data.sell_rate - data.buy_amount, 2)
    details = f"USDT: {usdt} | Қурб: {data.buy_rate} → {data.sell_rate} | Фоида: {profit}"
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO transactions (type, amount, reason, details) VALUES (?, ?, ?, ?)",
                ("p2p", profit, "Амалиёти P2P", details))
    conn.commit()
    conn.close()
    return {"status": "ok", "message": f"✅ Амалиёт сабт шуд, фоида: {profit} {CURRENCY}", "details": {"usdt": usdt, "profit": profit}}

@app.get("/balance")
def get_balance():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT SUM(CASE WHEN type='даромад' THEN amount WHEN type='хароҷот' THEN -amount ELSE amount END) AS total FROM transactions")
    row = cur.fetchone()
    conn.close()
    return {"total_balance": round(row["total"] or 0, 2), "currency": CURRENCY}

@app.get("/report/daily")
def daily_report():
    today = date.today().isoformat()
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT SUM(CASE WHEN type='даромад' THEN amount ELSE 0 END) AS income,
               SUM(CASE WHEN type='хароҷот' THEN amount ELSE 0 END) AS expense,
               SUM(CASE WHEN type='p2p' THEN amount ELSE 0 END) AS p2p_profit
        FROM transactions WHERE DATE(created_at) = ?
    """, (today,))
    row = cur.fetchone()
    conn.close()
    return {"income": round(row["income"] or 0, 2), "expense": round(row["expense"] or 0, 2), "p2p_profit": round(row["p2p_profit"] or 0, 2)}

@app.get("/report/monthly")
def monthly_report():
    month = datetime.now().strftime("%Y-%m")
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT SUM(CASE WHEN type='даромад' THEN amount ELSE 0 END) AS income,
               SUM(CASE WHEN type='хароҷот' THEN amount ELSE 0 END) AS expense,
               SUM(CASE WHEN type='p2p' THEN amount ELSE 0 END) AS p2p_profit,
               COUNT(*) AS count
        FROM transactions WHERE strftime('%Y-%m', created_at) = ?
    """, (month,))
    row = cur.fetchone()
    conn.close()
    return {
        "income": round(row["income"] or 0, 2),
        "expense": round(row["expense"] or 0, 2),
        "p2p_profit": round(row["p2p_profit"] or 0, 2),
        "net": round((row["income"] or 0) - (row["expense"] or 0) + (row["p2p_profit"] or 0), 2),
        "transactions_count": row["count"] or 0
    }

# Оғози сервер
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server_api:app", host="0.0.0.0", port=8000, reload=False)