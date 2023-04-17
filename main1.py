import random, sqlite3, logging, time, datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

class Roulette(StatesGroup):
    waiting_for_bet = State()
    waiting_for_spin = State()
    waiting_for_bonus = State()
    waiting_for_steal = State()


bot = Bot(token='6291371300:AAEz0uc9vVhP4nqa4Z37-wj2rcUld6Cp_mc')
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect('balances.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS balances
                  (user_id INTEGER PRIMARY KEY, name TEXT, balance INTEGER)''')
conn.commit()

@dp.message_handler(commands=['махакраш'])
async def commands(message: types.Message):
    await message.answer('<b>/бандит</b> - команда что бы играть в бандита обычного из рдно\n'
                         '<b>/б</b> - команда что бы баланс посмотреть\n'
                         '<b>/бонус</b> - команда что бы получить бонус, если ты бищара ебаный\n'
                         '<b>/богачи</b> - топ 10 акшасы дохуя кору ушин\n'
                         '<b>/урлау</b> - пиздишь у другого чела 10% его баланса\n'
                         '<b>/беру</b> - даешь сумму из своего баланса другому челику\n'
                         '<b>/дать</b> - кхахаха, никто кроме @onecelot им не может пользоваться', parse_mode='HTML')

@dp.message_handler(commands=['бандит'])
async def process_bandit_command(message: types.Message):
    try:
        command, amount = message.text.split()
        amount = int(amount)
    except ValueError:
        await message.reply("Используйте команду в формате: /бандит [сумма]")
        return
    except Exception as e:
        logging.exception(e)
        await message.reply("Произошла ошибка")
        return

    cursor.execute('SELECT * FROM balances WHERE user_id=?', (message.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute('INSERT INTO balances VALUES (?, ?, ?, ?)', (message.from_user.id, message.from_user.first_name, 5000, None))
        conn.commit()
        balance = 5000
    else:
        balance = row[2]

    if amount < 1:
        await message.reply("Ставка должна быть больше 1")
        return
    elif balance < amount:
        await message.reply("Недостаточно средств на балансе")
        return

    sent_message = await message.reply(f"{amount}\nЖди и молись!")

    chances = [(1, 100), (2, 10.0), (3, 5), (20, 2.0), (30, 1.5), (80, 0)]

    multiplier = 1
    for chance, factor in chances:
        if random.randint(1, 100) <= chance:
            multiplier = factor
            break

    time.sleep(3.5)

    new_amount = int(amount * multiplier)
    if amount == new_amount:
        await sent_message.edit_text(f"{amount}\nПовезло?\n{int(new_amount)}")
        balance += amount
    else:
        await sent_message.edit_text(f"{amount}\nНе повезло?\n{int(new_amount)}")
        balance += new_amount - amount

    cursor.execute('UPDATE balances SET balance=? WHERE user_id=?', (balance, message.from_user.id))
    conn.commit()

@dp.message_handler(commands=['б'])
async def process_balance_command(message: types.Message):
    cursor.execute('SELECT * FROM balances WHERE user_id=?', (message.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute('INSERT INTO balances VALUES (?, ?, ?, ?)', (message.from_user.id, message.from_user.first_name, 5000, None))
        conn.commit()
        balance = 5000
    else:
        balance = row[2]

    await message.reply(f'Ваш баланс: {balance}')

@dp.message_handler(commands=['дать'])
async def process_give_command(message: types.Message):
    try:
        command, amount = message.text.split()
        amount = int(amount)
    except ValueError:
        await message.reply("не тупи")
        return
    except Exception as e:
        logging.exception(e)
        await message.reply("ошибочка какая та")
        return
    if message.from_user.id != 994006554:
        await message.reply("У вас нет прав на выполнение этой команды")
        return

    cursor.execute('SELECT * FROM balances WHERE user_id=?', (message.reply_to_message.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute('INSERT INTO balances VALUES (?, ?, ?, ?)', (message.reply_to_message.from_user.id, message.reply_to_message.from_user.first_name, amount))
        conn.commit()
    else:
        cursor.execute('UPDATE balances SET balance=? WHERE user_id=?', (row[2]+amount, message.reply_to_message.from_user.id))
        conn.commit()

    await message.reply(f'Добавлено {amount} к балансу {message.reply_to_message.from_user.first_name}')

@dp.message_handler(commands=['богачи'])
async def process_richest_command(message: types.Message):
    cursor.execute('SELECT name, balance FROM balances ORDER BY balance DESC LIMIT 10')
    rows = cursor.fetchall()
    if len(rows) == 0:
        await message.reply('Нет богачей')
    else:
        richest_list = ''
        for i, row in enumerate(rows, 1):
            richest_list += f"{i}. {row[0]} - {row[1]}\n"
        await message.reply(f'Топ 10 богачей:\n{richest_list}')

@dp.message_handler(commands=['бонус'])
async def process_bonus_command(message: types.Message, state: FSMContext):
    cursor.execute("PRAGMA table_info(balances)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'bonus_date' not in columns:
        cursor.execute('ALTER TABLE balances ADD COLUMN bonus_date TEXT')
    today = time.strftime("%Y-%m-%d")
    cursor.execute('SELECT * FROM balances WHERE user_id=?', (message.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        cursor.execute('INSERT INTO balances VALUES (?, ?, ?, ?)', (message.from_user.id, message.from_user.first_name, 0))
        conn.commit()
        balance = 0
    else:
        balance = row[2]

    if len(row) > 3 and row[3] == today:
        bonus_time = datetime.datetime.strptime(today + " 23:59:59", "%Y-%m-%d %H:%M:%S") - datetime.datetime.now()
        await message.reply(
            f"Следующий бонус будет доступен через {bonus_time.seconds // 3600} часов {bonus_time.seconds // 60 % 60} минут")
        return

    cursor.execute('UPDATE balances SET balance=?, bonus_date=? WHERE user_id=?', (balance+3000, today, message.from_user.id))
    conn.commit()
    await message.reply("Вы получили бонус 3000")

@dp.message_handler(commands=['беру'])
async def process_give_command(message: types.Message, state: FSMContext):
    try:
        amount = int(message.text.split()[1])
        target_user_id = message.reply_to_message.from_user.id
    except (IndexError, ValueError, AttributeError):
        await message.reply('Используйте команду в формате: /беру [сумма] в ответ на сообщение пользователя, которому хотите перевести деньги')
        return

    cursor.execute('SELECT balance FROM balances WHERE user_id=?', (message.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        await message.reply('У вас нету счета')
        return
    balance = row[0]

    if amount > balance:
        await message.reply('У вас недостаточно денег на счете')
        return

    cursor.execute('SELECT name FROM balances WHERE user_id=?', (target_user_id,))
    row = cursor.fetchone()
    if row is None:
        await message.reply('Пользователь не зарегистрирован в чате')
        return
    target_user_name = row[0]

    cursor.execute('UPDATE balances SET balance=balance-? WHERE user_id=?', (amount, message.from_user.id))
    cursor.execute('UPDATE balances SET balance=balance+? WHERE user_id=?', (amount, target_user_id))
    conn.commit()

    await message.reply(f'Вы перевели <b>{amount}</b> монет пользователю <b>{target_user_name}</b>', parse_mode='HTML')

@dp.message_handler(commands=['урлау'])
async def process_steal_command(message: types.Message, state: FSMContext):
    try:
        target_user_id = message.reply_to_message.from_user.id
    except AttributeError:
        await message.reply('Используйте команду в ответ на сообщение пользователя, у которого хотите украсть деньги')
        return

    cursor.execute('SELECT balance FROM balances WHERE user_id=?', (target_user_id,))
    row = cursor.fetchone()
    if row is None:
        await message.reply('Пользователь не зарегистрирован в чате')
        return
    target_user_balance = row[0]

    if target_user_balance == 0:
        await message.reply('У пользователя нет денег на счете')
        return

    # Вычисляем 10% от баланса пользователя, которому ответили
    amount = int(target_user_balance * 0.1)

    cursor.execute('SELECT balance FROM balances WHERE user_id=?', (message.from_user.id,))
    row = cursor.fetchone()
    if row is None:
        await message.reply('У вас нету счета')
        return
    balance = row[0]

    if amount > balance:
        await message.reply('У вас недостаточно денег на счете для совершения кражи')
        return

    cursor.execute('UPDATE balances SET balance=balance-? WHERE user_id=?', (amount, target_user_id))
    cursor.execute('UPDATE balances SET balance=balance+? WHERE user_id=?', (amount, message.from_user.id))
    conn.commit()

    await message.reply(f'Вы украли <b>{amount}</b> монет у пользователя <b>{message.reply_to_message.from_user.first_name}</b>', parse_mode='HTML')



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)