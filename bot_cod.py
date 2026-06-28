import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command

TOKEN = "ТОКЕНИ_БОТИ_ХУДРО_ИНҶО_НАВИСЕД"
API_SERVER = "https://hisoboti-server.onrender.com/api"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start_handler(message: types.Message):
    await message.answer("Салом! Ман боти ҳисоботи молия ҳастам. Фармонҳоро истифода баред:\n/balance - Тавозун\n/daily - Ҳисоботи рӯзона")

@dp.message(Command("balance"))
async def balance_handler(message: types.Message):
    try:
        res = requests.get(f"{API_SERVER}/balance", timeout=10)
        data = res.json()
        await message.answer(f"💰 Тавозуни умумӣ: {data['total_balance']} {data['currency']}")
    except Exception as e:
        await message.answer("❌ Сервер дастрас нест ё хато рух дод")

@dp.message(Command("daily"))
async def daily_handler(message: types.Message):
    try:
        res = requests.get(f"{API_SERVER}/report/daily", timeout=10)
        d = res.json()
        await message.answer(f"📊 Ҳисоботи имрӯза:\n➕ Даромад: {d['income']}\n➖ Хароҷот: {d['expense']}\n💵 Фоида P2P: {d['p2p_profit']}")
    except Exception as e:
        await message.answer("❌ Хато дар гирифтани ҳисобот")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())