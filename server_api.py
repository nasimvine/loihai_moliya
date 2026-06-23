# server_api.py
"""
Backend API бо FastAPI
Пайвасткунандаи веб-сайт, бот ва базаи маълумот
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from baza_sql import (
    add_income, add_expense, add_p2p_transaction,
    get_daily_report, get_weekly_report, get_monthly_report,
    get_total_balance
)
from config import API_HOST, API_PORT, ALLOWED_USER_ID
import uvicorn

app = FastAPI(
    title="Системаи идоракунии молия",
    description="API барои сабт ва ҳисобкунии даромад, хароҷот ва P2P",
    version="1.0.0"
)

# Иҷозат барои кор аз тарафи браузер
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Моделҳои санҷиши маълумот ---
class IncomeSchema(BaseModel):
    amount: float = Field(gt=0, description="Маблағи даромад (бояд аз сифр зиёд бошад)")
    reason: str = Field(default="Дигар", max_length=100)
    date: str | None = None
    user_id: int = ALLOWED_USER_ID

class ExpenseSchema(BaseModel):
    amount: float = Field(gt=0, description="Маблағи хароҷот (бояд аз сифр зиёд бошад)")
    reason: str = Field(default="Дигар", max_length=100)
    date: str | None = None
    user_id: int = ALLOWED_USER_ID

class P2PSchema(BaseModel):
    buy_amount: float = Field(gt=0)
    buy_rate: float = Field(gt=0)
    sell_rate: float = Field(gt=0)
    reason: str = Field(default="P2P мубодила", max_length=100)
    date: str | None = None
    user_id: int = ALLOWED_USER_ID

# --- Нуқтаҳои API ---
@app.post("/income", summary="Сабти даромад")
def create_income(data: IncomeSchema):
    try:
        add_income(data.amount, data.reason, data.date, data.user_id)
        return {"status": "success", "message": "✅ Даромад бо муваффақият сабт шуд"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ Хатогӣ: {str(e)}")

@app.post("/expense", summary="Сабти хароҷот")
def create_expense(data: ExpenseSchema):
    try:
        add_expense(data.amount, data.reason, data.date, data.user_id)
        return {"status": "success", "message": "✅ Хароҷот бо муваффақият сабт шуд"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ Хатогӣ: {str(e)}")

@app.post("/p2p", summary="Ҳисоб ва сабти амалиёти P2P")
def create_p2p(data: P2PSchema):
    try:
        result = add_p2p_transaction(
            data.buy_amount, data.buy_rate, data.sell_rate,
            data.reason, data.date, data.user_id
        )
        return {
            "status": "success",
            "message": "✅ Амалиёти P2P сабт шуд",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"❌ Хатогӣ: {str(e)}")

@app.get("/report/daily", summary="Ҳисоботи рӯзона")
def daily_report(user_id: int = ALLOWED_USER_ID):
    return get_daily_report(user_id)

@app.get("/report/weekly", summary="Ҳисоботи ҳафтаина")
def weekly_report(user_id: int = ALLOWED_USER_ID):
    return get_weekly_report(user_id)

@app.get("/report/monthly", summary="Ҳисоботи моҳона")
def monthly_report(user_id: int = ALLOWED_USER_ID):
    return get_monthly_report(user_id)

@app.get("/balance", summary="Маблағи умумии боқимонда")
def get_balance(user_id: int = ALLOWED_USER_ID):
    return {"total_balance": get_total_balance(user_id)}

if __name__ == "__main__":
    uvicorn.run(app, host=API_HOST, port=API_PORT)