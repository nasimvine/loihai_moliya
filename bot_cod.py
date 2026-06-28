"""
Логикаи пурраи Telegram Bot
Бо меню, фармонҳо ва қабули маълумот
"""
import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import BOT_TOKEN, ALLOWED_USER_ID

API_URL = "http://127.0.0.1:8000"

# Калиди нави бот
BOT_TOKEN = "8958152466:AAEIJBHqMtHSQSqz1rEwbTCRnPnpzi6jXls"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Ҳолатҳо барои қабули маълумот аз корбар ---
class InputStates(StatesGroup):
    waiting_income = State()
    waiting_expense = State()
    waiting_p2p = State()

# --- Менюи асосӣ ---
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Сабти даромад", callback_data="income")],
        [InlineKeyboardButton(text="💸 Сабти хароҷот", callback_data="expense")],
        [InlineKeyboardButton(text="📈 Ҳисоб P2P", callback_data="p2p")],
        [InlineKeyboardButton(text="📊 Ҳисоботҳо", callback_data="reports")],
        [InlineKeyboardButton(text="🔎 Ҳолати умумӣ", callback_data="check")]
    ])

@dp.message(CommandStart())
async def start_cmd(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        await message.answer("❌ Шумо иҷозати истифодаи ин ботро надоред!")
        return
    await message.answer(
        "👋 Хуш омадед ба системаи идоракунии молияи шахсӣ!\n\n"
        "Бот: @hisoboti_nasim_bot\n"
        "Барои идома аз менюи зер интихоб кунед:",
        reply_markup=main_menu()
    )

@dp.message(Command("check"))
async def check_cmd(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    try:
        balance = requests.get(f"{API_URL}/balance", timeout=5).json()
        daily = requests.get(f"{API_URL}/report/daily", timeout=5).json()
        monthly = requests.get(f"{API_URL}/report/monthly", timeout=5).json()

        text = f"""🔎 ҲОЛАТИ УМУМӢ

💵 Маблағи умумӣ: {balance['total_balance']} сомон

📅 Имрӯз:
• Даромад: {daily['income']} сомон
• Хароҷот: {daily['expense']} сомон
• Фоида P2P: {daily['p2p_profit']} сомон

📆 Ин моҳ:
• Даромад: {monthly['income']} сомон
• Хароҷот: {monthly['expense']} сомон
• Фоида P2P: {monthly['p2p_profit']} сомон
• Фоидаи холис: {monthly['net']} сомон
• Шумораи амалиёт: {monthly['transactions_count']}
"""
        await message.answer(text)
    except Exception as e:
        await message.answer(f"❌ Хатогӣ! Сервер кор намекунад ё пайваст нест.\nТафсилот: {str(e)}")

@dp.message(Command("report"))
async def report_cmd(message: types.Message):
    if message.from_user.id != ALLOWED_USER_ID:
        return
    try:
        res = requests.get(f"{API_URL}/report/monthly", timeout=5).json()
        text = f"""📊 ҲИСОБОТИ МОҲОНА

💵 Даромад: {res['income']} сомон
💸 Хароҷот: {res['expense']} сомон
📈 Фоида аз P2P: {res['p2p_profit']} сомон
✅ Фоидаи холис: {res['net']} сомон
🔢 Шумораи амалиёт: {res['transactions_count']}
"""
        await message.answer(text)
    except Exception as e:
        await message.answer(f"❌ Хатогӣ! Сервер кор намекунад.\n{str(e)}")

@dp.callback_query()
async def menu_handler(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id != ALLOWED_USER_ID:
        await callback.answer("Иҷозат нест!")
        return

    if callback.data == "income":
        await callback.message.answer("💰 Маблағ ва сабаби даромадро нависед:\nНамуна: `500 | Музди кор`")
        await state.set_state(InputStates.waiting_income)

    elif callback.data == "expense":
        await callback.message.answer("💸 Маблағ ва сабаби хароҷотро нависед:\nНамуна: `120 | Хӯрокворӣ`")
        await state.set_state(InputStates.waiting_expense)

    elif callback.data == "p2p":
        await callback.message.answer("📈 Маълумоти амалиёти P2P-ро нависед:\nНамуна: `1000 | 11.2 | 11.5`\n(Маблағ харид | Қурб харид | Қурб фурӯш)")
        await state.set_state(InputStates.waiting_p2p)

    elif callback.data == "reports":
        await report_cmd(callback.message)

    elif callback.data == "check":
        await check_cmd(callback.message)

    await callback.answer()

@dp.message(InputStates.waiting_income)
async def process_income(message: types.Message, state: FSMContext):
    try:
        if "|" in message.text:
            amount_part, reason = message.text.split("|", 1)
            amount = float(amount_part.strip())
            reason = reason.strip() if reason.strip() else "Дигар"
        else:
            amount = float(message.text.strip())
            reason = "Дигар"

        response = requests.post(f"{API_URL}/income", json={"amount": amount, "reason": reason}, timeout=5)
        result = response.json()
        await message.answer(result["message"], reply_markup=main_menu())
    except Exception as e:
        await message.answer(f"❌ Формат нодуруст ё хатогӣ дар фиристодан!\n{str(e)}")
    await state.clear()

@dp.message(InputStates.waiting_expense)
async def process_expense(message: types.Message, state: FSMContext):
    try:
        if "|" in message.text:
            amount_part, reason = message.text.split("|", 1)
            amount = float(amount_part.strip())
            reason = reason.strip() if reason.strip() else "Дигар"
        else:
            amount = float(message.text.strip())
            reason = "Дигар"

        response = requests.post(f"{API_URL}/expense", json={"amount": amount, "reason": reason}, timeout=5)
        result = response.json()
        await message.answer(result["message"], reply_markup=main_menu())
    except Exception as e:
        await message.answer(f"❌ Формат нодуруст ё хатогӣ!\n{str(e)}")
    await state.clear()

@dp.message(InputStates.waiting_p2p)
async def process_p2p(message: types.Message, state: FSMContext):
    try:
        parts = message.text.split("|")
        buy_amount = float(parts[0].strip())
        buy_rate = float(parts[1].strip())
        sell_rate = float(parts[2].strip())

        response = requests.post(f"{API_URL}/p2p", json={
            "buy_amount": buy_amount,
            "buy_rate": buy_rate,
            "sell_rate": sell_rate
        }, timeout=5)
        result = response.json()
        details = result["details"]

        text = f"""✅ Амалиёт сабт шуд:

💸 Маблағ харид: {buy_amount} сомон
💱 Қурб харид: {buy_rate}
💵 USDT гирифта: {details['usdt']}
📈 Қурб фурӯш: {sell_rate}
💰 Маблағ гирифта: {details['sell_value']} сомон
💲 Фоида: {details['profit']} сомон
"""
        await message.answer(text, reply_markup=main_menu())
    except Exception as e:
        await message.answer(f"❌ Формат нодуруст! Намуна: `1000 | 11.2 | 11.5`\n{str(e)}")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())