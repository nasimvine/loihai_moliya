// Суроғаи дурусти сервер
const API_URL = "https://hisoboti-server.onrender.com/api";

// Мисоли фиристодани даромад
async function addIncome(amount, reason) {
    try {
        const response = await fetch(`${API_URL}/income`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount: parseFloat(amount), reason: reason })
        });
        const result = await response.json();
        alert(result.message);
        return result;
    } catch (error) {
        alert("Хато дар сабт: " + error);
    }
}

// Мисоли фиристодани хароҷот
async function addExpense(amount, reason) {
    try {
        const response = await fetch(`${API_URL}/expense`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amount: parseFloat(amount), reason: reason })
        });
        const result = await response.json();
        alert(result.message);
        return result;
    } catch (error) {
        alert("Хато дар сабт: " + error);
    }
}

// Мисоли гирифтани тавозун
async function getBalance() {
    try {
        const response = await fetch(`${API_URL}/balance`);
        const data = await response.json();
        document.getElementById("balance").innerText = `${data.total_balance} ${data.currency}`;
    } catch (error) {
        console.error("Хато:", error);
    }
}