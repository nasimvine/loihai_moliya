// skript.js - Мантиқи тарафи муштарӣ
const API_URL = "http://127.0.0.1:8000";

// --- Функсияи гирифтани ҳисоботҳо ---
async function loadSummary() {
    try {
        const balance = await fetch(`${API_URL}/balance`).then(r => r.json());
        const daily = await fetch(`${API_URL}/report/daily`).then(r => r.json());
        const monthly = await fetch(`${API_URL}/report/monthly`).then(r => r.json());

        document.getElementById("total-balance").textContent = balance.total_balance;
        document.getElementById("daily-income").textContent = daily.income;
        document.getElementById("daily-expense").textContent = daily.expense;
        document.getElementById("monthly-income").textContent = monthly.income;
        document.getElementById("monthly-expense").textContent = monthly.expense;
        document.getElementById("monthly-p2p").textContent = monthly.p2p_profit;
        document.getElementById("monthly-net").textContent = monthly.net;
    } catch (error) {
        console.log("Хатогӣ дар пайвастшавӣ:", error);
    }
}

// --- Сабти даромад ---
async function submitIncome() {
    const amount = parseFloat(document.getElementById("income-amount").value);
    const reason = document.getElementById("income-reason").value.trim() || "Дигар";
    const date = document.getElementById("income-date").value;

    if (!amount || amount <= 0) {
        alert("❌ Маблағро дуруст ворид кунед!");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/income`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount, reason, date })
        });
        const result = await response.json();
        alert(result.message);
        document.getElementById("income-form").reset();
        loadSummary();
    } catch {
        alert("❌ Хатогӣ! Сервер кор намекунад.");
    }
}

// --- Сабти хароҷот ---
async function submitExpense() {
    const amount = parseFloat(document.getElementById("expense-amount").value);
    const reason = document.getElementById("expense-reason").value.trim() || "Дигар";
    const date = document.getElementById("expense-date").value;

    if (!amount || amount <= 0) {
        alert("❌ Маблағро дуруст ворид кунед!");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/expense`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount, reason, date })
        });
        const result = await response.json();
        alert(result.message);
        document.getElementById("expense-form").reset();
        loadSummary();
    } catch {
        alert("❌ Хатогӣ! Сервер кор намекунад.");
    }
}

// --- Сабти P2P ---
async function submitP2P() {
    const buyAmount = parseFloat(document.getElementById("p2p-amount").value);
    const buyRate = parseFloat(document.getElementById("p2p-buy").value);
    const sellRate = parseFloat(document.getElementById("p2p-sell").value);
    const reason = document.getElementById("p2p-reason").value.trim() || "P2P мубодила";

    if (!buyAmount || !buyRate || !sellRate || buyAmount <= 0 || buyRate <= 0 || sellRate <= 0) {
        alert("❌ Ҳама рақамҳоро дуруст ворид кунед!");
        return;
    }

    try {
        const response = await fetch(`${API_URL}/p2p`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                buy_amount: buyAmount,
                buy_rate: buyRate,
                sell_rate: sellRate,
                reason
            })
        });
        const result = await response.json();
        const details = result.details;
        alert(`${result.message}\nФоида: ${details.profit} сомон`);
        document.getElementById("p2p-form").reset();
        loadSummary();
    } catch {
        alert("❌ Хатогӣ! Сервер кор намекунад.");
    }
}

// Бор кардани маълумот ҳангоми кушодани саҳифа
window.onload = loadSummary;