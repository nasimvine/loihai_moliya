from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime, date
from pydantic import BaseModel
import os

app = FastAPI(title="Системаи ҳисоботи молия")

# Иҷозати пурраи дастрасӣ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE, "moliya.db")
CURRENCY = "сомонӣ"

# --------------------------
# 📄 Дастрасӣ ба ҳама саҳифаҳо ва файлҳо
# --------------------------
@app.get("/")
def index():
    return FileResponse(os.path.join(BASE, "sahofai_aval.html"))

@app.get("/dizayn.css")
def dizayn_css():
    return FileResponse(os.path.join(BASE, "dizayn.css"))

@app.get("/style.css")
def style_css():
    return FileResponse(os.path.join(BASE, "style.css"))

@app.get("/skript.js")
def skript_js():
    return FileResponse(os.path.join(BASE, "skript.js"))

@app.get("/sahofai_daromad.html")
def sah_daromad():
    return FileResponse(os.path.join(BASE, "sahofai_daromad.html"))

@app.get("/sahofai_harojot.html")
def sah_harojot():
    return FileResponse(os.path.join(BASE, "sahofai_harojot.html"))

@app.get("/sahofai_p2p.html")
def sah_p2p():
    return FileResponse(os.path.join(BASE, "sahofai_p2p.html"))

@app.get("/sahofai_hisobot.html")
def sah_hisobot():
    return FileResponse(os.path.join(BASE, "sahofai_hisobot.html"))

# --------------------------
# 🗄️ Базаи маълумот
# --------------------------
def get_db():
    conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

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

# --------------------------
# 📋 Моделҳо ва API барои сабти маълумот
# --------------------------
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

@app.post("/api/income")
def add_income(data: IncomeData):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Маблағ бояд мусбат бошад")
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO transactions (type, amount, reason) VALUES (?, ?, ?)",
            ("даромад", round(data.amount, 2), data.reason)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return {"status": "ok", "message": f"✅ Даромад {data.amount} {CURRENCY} сабт шуд", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Хато: {str(e)}")

@app.post("/api/expense")
def add_expense(data: ExpenseData):
    if data.amount <= 0:
        raise HTTPException(status_code=400, detail="Маблағ бояд мусбат бошад")
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO transactions (type, amount, reason) VALUES (?, ?, ?)",
            ("хароҷот", round(data.amount, 2), data.reason)
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return {"status": "ok", "message": f"💸 Хароҷот {data.amount} {CURRENCY} сабт шуд", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Хато: {str(e)}")

@app.post("/api/p2p")
def add_p2p(data: P2PData):
    if data.buy_amount <= 0 or data.buy_rate <= 0 or data.sell_rate <= 0:
        raise HTTPException(status_code=400, detail="Ҳама рақамҳо бояд мусбат бошанд")
    try:
        usdt = round(data.buy_amount / data.buy_rate, 2)
        profit = round(usdt * data.sell_rate - data.buy_amount, 2)
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO transactions (type, amount, reason, details) VALUES (?, ?, ?, ?)",
            ("p2p", profit, "Амалиёти P2P", f"USDT: {usdt} | Қурб: {data.buy_rate} → {data.sell_rate}")
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return {"status": "ok", "message": f"✅ Фоида: {profit} {CURRENCY} сабт шуд", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Хато: {str(e)}")

@app.get("/api/balance")
def get_balance():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT SUM(CASE 
                WHEN type='даромад' THEN amount 
                WHEN type='хароҷот' THEN -amount 
                ELSE amount END) AS total 
            FROM transactions
        """)
        row = cur.fetchone()
        conn.close()
        return {"total_balance": round(row["total"] or 0, 2), "currency": CURRENCY}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Хато: {str(e)}")

@app.get("/api/report/daily")
def daily_report():
    today = date.today().isoformat()
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                SUM(CASE WHEN type='даромад' THEN amount ELSE 0 END) AS income,
                SUM(CASE WHEN type='хароҷот' THEN amount ELSE 0 END) AS expense,
                SUM(CASE WHEN type='p2p' THEN amount ELSE 0 END) AS p2p
            FROM transactions WHERE DATE(created_at) = ?
        """, (today,))
        row = cur.fetchone()
        conn.close()
        return {
            "income": round(row["income"] or 0, 2),
            "expense": round(row["expense"] or 0, 2),
            "p2p_profit": round(row["p2p"] or 0, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Хато: {str(e)}")

# --------------------------
# 🚀 Оғози сервер
# --------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("server_api:app", host="0.0.0.0", port=port)