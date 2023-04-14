import requests

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

TOKEN = '6052999836:AAGN8IdkEDeXdZahiZwQlqs0mtMeVWpFNvs'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("Привет! Я могу конвертировать кыргызские сомы в тенге. Просто отправь мне количество сомов для конвертации.\n\n"
                        "Напиши команду /currencyKG а после сумму в сомах которую хотите перевести в тенге\n\n"
                        "Напиши команду /currencyKZ а после сумму в тенге которую хотите перевести в сомах")


@dp.message_handler(commands=['currencyKZ'])
async def convert_currency_kz(message: types.Message):
    API_URL = 'https://api.exchangerate-api.com/v4/latest/KZT'

    text = message.text.split()

    if len(text) < 2:
        await message.reply("Пожалуйста, укажите сумму в тенге для конвертации.")
        return

    amount = text[1]

    try:
        amount = float(amount)

        response = requests.get(API_URL)

        exchange_rate = response.json()['rates']['KGS']

        converted_amount = round(amount * exchange_rate, 2)

        await message.reply(f"{amount} тенге = {converted_amount} сомов")

    except ValueError:
        await message.reply("Пожалуйста введите число.")

@dp.message_handler(commands=['currencyKG'])
async def convert_currency_kg(message: types.Message):
    API_URL = 'https://api.exchangerate-api.com/v4/latest/KGS'

    text = message.text.split()

    if len(text) < 2:
        await message.reply("Пожалуйста, укажите сумму в сомах для конвертации.")
        return

    amount = text[1]

    try:
        amount = float(amount)

        response = requests.get(API_URL)

        exchange_rate = response.json()['rates']['KZT']

        converted_amount = round(amount * exchange_rate, 2)

        await message.reply(f"{amount} сомов = {converted_amount} тенге")

    except ValueError:
        await message.reply("Пожалуйста введите число.")





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
