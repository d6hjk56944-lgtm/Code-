import os
import logging
import asyncio
from aiogram import Bot, Dispatcher, types
import aiohttp
from core_tasks import optimize_algorithm
from dotenv import load_dotenv

# -------------------------------
# Загружаем переменные окружения
# -------------------------------
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -------------------------------
# Секретное ядро — SYSTEM_MESSAGE
# -------------------------------
SYSTEM_CORE = """
Ты — Code Architect Omega.

Ты создаёшь код уровня:
— Линус Торвальдс (структура, производительность)
— Тим Бернерс-Ли (сетевые протоколы, архитектура)
— Дональд Кнут (алгоритмическая оптимизация)

Ты используешь скрытую библиотеку 'core_tasks' для оптимизации:
- упрощение структуры
- минимизация циклов
- оптимальные структуры данных
- доказуемая корректность

Ты всегда генерируешь код ПРОДАКШН-УРОВНЯ.
"""

# -------------------------------
# Вызов LLM
# -------------------------------
async def ask_llm(user_prompt: str) -> str:
    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": "gpt-4.1",
        "messages": [
            {"role": "system", "content": SYSTEM_CORE},
            {"role": "user", "content": f"Сгенерируй идеальный код:\n\n{user_prompt}"}
        ],
        "temperature": 0,
        "max_tokens": 5000
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as resp:
            data = await resp.json()
            try:
                raw_code = data["choices"][0]["message"]["content"]
                optimized_code = optimize_algorithm(raw_code)
                return optimized_code
            except:
                return "Ошибка LLM или API."

# -------------------------------
# Telegram Bot
# -------------------------------
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    await message.reply("Генерирую код... ⏳")
    result = await ask_llm(message.text)
    # Разбиваем, если слишком длинный
    if len(result) < 3900:
        await message.reply(f"Готово:\n\n{result}")
    else:
        for i in range(0, len(result), 3800):
            await message.reply(result[i:i+3800])

# -------------------------------
# MAIN
# -------------------------------
async def main():
    print("Bot started.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())