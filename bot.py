# Устанавливаем библиотеку aiogram
# pip install -U --pre aiogram
# Импортируем классы и методы
from aiogram import Bot, Dispatcher
from aiogram.filters import Text, Command
from aiogram.types import Message
from telebot import types
from config import token  # из файла config.py забираем нашу переменную с токеном

import random


# Создаем объекты бота и диспетчера
bot: Bot = Bot(token)
dp: Dispatcher = Dispatcher()

# Количество попыток, доступных пользователю в игре
ATTEMPTS: int = 5

# словарь с данными пользователей
users: dict = {}

# Функция рандомного числа
def get_random_number():
    return random.randint(1, 100)


# Этот хэндлер будет срабатывать на команду "/start"
@dp.message(Command(commands='start'))
async def process_start_command(message: Message):
    await message.answer((f'Привет, {message.chat.first_name}! \nДавай сыграем в игру "Угадай число"?\n\n'
                         'Чтобы получить правила игры и список доступных '
                         'команд - смотрите МЕНЮ \n'
                          'или отправьте команду /help'))

    # создадим две кнопки "Да", "Нет"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Объект представлят клавиатуру с опциями ответа
    item1 = types.KeyboardButton("Да")
    markup.add(item1)  # Добавляем кнопку к клавиатуре
    item2 = types.KeyboardButton("Нет")
    markup.add(item2)  # Добавляем кнопку к клавиатуре

    await message.answer('Выберите действие', reply_markup=markup)
    await message.answer(text='👇')

    # Если пользователь только запустил бота и его нет в словаре '
    # 'users - добавляем его в словарь
    if message.from_user.id not in users:
        users[message.from_user.id] = {'in_game': False,
                                       'secret_number': None,
                                       'attempts': None,
                                       'total_games': 0,
                                       'wins': 0}
        print(users)

# Этот хэндлер будет срабатывать на команду "/help"
@dp.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer((f'Правила игры:\n\nЯ загадываю число от 1 до 100, '
                          f'а вам нужно его угадать\nУ вас есть {ATTEMPTS} '
                          f'попыток\n\nДоступные команды:\n'
                          f'/start - начать игру \n'
                          f'/help - правила игры и список команд\n'
                          f'/cancel - выйти из игры\n'
                          f'/stat - посмотреть статистику\n\n'   
                          f'Давай сыграем?'))

# Этот хэндлер будет срабатывать на команду "/stat"
@dp.message(Command(commands='stat'))
async def process_stat_command(message:Message):
    print(message)
    await message.answer((f'Всего игр сыграно: {users[message.from_user.id]["total_games"]} \n'
                          f'Игр выиграно: {users[message.from_user.id]["wins"]}'))

# Этот хэндлер будет срабатывать на команду "/cancel"
@dp.message(Command(commands='cancel'))
async def process_cancel_command(message:Message):
    if users[message.from_user.id]['in_game']:
        await message.answer('Вы вышли из игры. Если захотите сыграть '
                             'снова - напишите об этом')
        await message.answer(text='👇')
        users[message.from_user.id]['in_game'] = False
    else:
        await message.answer('А мы итак с вами не играем. '
                             'Может, сыграем разок?')
        await message.answer(text='😉')

# Этот хэндлер будет срабатывать на согласие пользователя сыграть в игру
@dp.message(Text(text=['Да', 'Давай', 'Сыграем', 'Игра', 'Играть'], ignore_case=True)) # игнор регистра True
async def process_positive_answer(message:Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer('Ура!\n\nЯ загадал число от 1 до 100, '
                             'попробуй угадать!')
        users[message.from_user.id]['in_game'] = True
        users[message.from_user.id]['secret_number'] = get_random_number()
        users[message.from_user.id]['attempts'] = ATTEMPTS
    else:
        await message.answer('Пока мы играем в игру я могу '
                             'реагировать только на числа от 1 до 100 '
                             'и команды /cancel и /stat')

# Этот хэндлер будет срабатывать на отказ пользователя сыграть в игру
@dp.message(Text(text=['Нет', 'Не хочу', 'Не', 'Не буду'], ignore_case=True))  # игнор регистра True
async def process_negative_answer(message:Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer('Жаль :(\n\nЕсли захотите поиграть - просто '
                             'напишите об этом')
        await message.answer(text='👇')
    else:
        await message.answer('Мы же сейчас с вами играем. Присылайте, '
                             'пожалуйста, числа от 1 до 100 ;)')
        await message.answer(text='😉')

# Этот хэндлер будет срабатывать на отправку пользователем чисел от 1 до 100
@dp.message(lambda x: x.text and x.text.isdigit() and 1 <= int(x.text) <= 100) # фильтр значений по содержимому text, цифры и диапазон
async def process_number_answer(message:Message):
    print(message)
    if users[message.from_user.id]['in_game']:
        if int(message.text) == users[message.from_user.id]['secret_number']:
            await message.answer('Ура!!! Вы угадали число!\n\n'
                                 'Может, сыграем еще?')
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
            users[message.from_user.id]['wins'] +=1
            await bot.send_sticker(message.from_user.id,
                             sticker='CAACAgIAAxkBAAMSZChPJFJ_gpcIwkkvHkSuvSlw5NUAAgUBAAJhg2MGwbf5qhfi9HEvBA')
            await process_stat_command(message)
        elif int(message.text) > users[message.from_user.id]['secret_number']:
            users[message.from_user.id]['attempts'] -= 1
            await message.answer(f'Мое число меньше \n'
                                 f"У вас осталось попыток: {users[message.from_user.id]['attempts']}")
        elif int(message.text) < users[message.from_user.id]['secret_number']:
            users[message.from_user.id]['attempts'] -= 1
            await message.answer(f'Мое число больше \n'
                                 f"У вас осталось попыток: {users[message.from_user.id]['attempts']}")
        if users[message.from_user.id]['attempts'] == 0:
            await message.answer(f'К сожалению, у вас больше не осталось '
                                 f'попыток. Вы проиграли :(\n\nМое число '
                                 f'было {users[message.from_user.id]["secret_number"]}\n\nДавайте '
                                 f'сыграем еще?')
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['total_games'] += 1
            await bot.send_sticker(message.from_user.id,
                             sticker='CAACAgIAAxkBAAMWZChPyvJ8we6C7SS0ZoIG2gHTytAAAloFAAI_lcwKGxa5hb0gw50vBA')
            await process_stat_command(message)
    else:
        await message.answer('Мы еще не играем. Хотите сыграть?')
        await bot.send_sticker(message.from_user.id,
                               sticker='CAACAgIAAxkBAAMYZChQohHyObLiA3AHNPIJ2JerpM8AAuAAA2GDYwY-cwIBW2KNuS8E')


# Этот хэндлер будет срабатывать на остальные любые сообщения
@dp.message()
async def process_another_answer(message:Message):
    if users[message.from_user.id]['in_game']:
        await message.answer('Мы же сейчас с вами играем. '
                             'Присылайте, пожалуйста, числа от 1 до 100')
        await message.answer(text='😉')
    else:
        await message.answer('Я довольно ограниченный бот, давайте '
                             'просто сыграем в игру?')
        await message.answer(text='👇')


# Запускаем бота
if __name__ == '__main__':
    dp.run_polling(bot)


