from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import InputFile
import asyncio

API_TOKEN = '7900008680'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

buttom_1 = KeyboardButton(text='Рассчитать')
buttom_2 = KeyboardButton(text='Информация')
buttom_3 = KeyboardButton(text='Купить')
kb_repl = ReplyKeyboardMarkup([[buttom_1, buttom_2, buttom_3]], resize_keyboard=True)
# kb_repl.add(buttom_1)
# kb_repl.add(buttom_2)
# kb_repl.add(buttom_3)

kb_inline = InlineKeyboardMarkup()
buttom_1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
buttom_2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_inline.add(buttom_1)
kb_inline.add(buttom_2)

kb_product = InlineKeyboardMarkup()
buttom_3 = InlineKeyboardButton(text='Лечебный сбор трав № 1', callback_data='product_buying')
buttom_4 = InlineKeyboardButton(text='Лечебный сбор трав № 2', callback_data='product_buying')
buttom_5 = InlineKeyboardButton(text='Лечебный сбор трав № 3', callback_data='product_buying')
buttom_6 = InlineKeyboardButton(text='Лечебный сбор трав № 4', callback_data='product_buying')
kb_product.add(buttom_3)
kb_product.add(buttom_4)
kb_product.add(buttom_5)
kb_product.add(buttom_6)


class UserState(StatesGroup):
    gender = State()
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(lambda message: message.text == 'Информация')
async def inform(message):
    text_about = 'Программа рассчета нормы калорий, исходя из вашего пола, возраста, роста и веса.'
    with open('./image/fon_dobavki.jpg', 'rb') as img:
        await message.answer_photo(img, text_about)


@dp.message_handler(commands='start')
async def start_command(message: Message):
    text_start = 'Привет! Я помогу тебе рассчитать норму калорий.'
    await message.answer(f'Добро пожаловать, уважаемый {message.from_user.username}\n' + text_start,
                         reply_markup=kb_repl)

@dp.message_handler(lambda message: message.text == 'Рассчитать')
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=kb_inline)


# Создаем список продуктов с их описаниями и ценами
products = [
    {
        'name':'Лечебный сбор трав № 1',
        'description':'Лечебные травы горного Алтая для восстанавливания организма',
        'price':100,
        'photo_path':'./image/sbor_trav_1.jpg'
    },
    {
        'name':'Лечебный сбор трав № 2',
        'description':'Лечебные травы горного Алтая для восстанавливания организма',
        'price':200,
        'photo_path':'./image/sbor_trav_2.jpg'
    },
    {
        'name':'Лечебный сбор трав № 3',
        'description':'Лечебные травы горного Алтая для восстанавливания организма',
        'price':300,
        'photo_path':'./image/sbor_trav_3.jpg'
    },
    {
        'name':'Лечебный сбор трав № 4',
        'description':'Лечебные травы горного Алтая для восстанавливания организма',
        'price':400,
        'photo_path':'./image/sbor_trav_4.jpg'
    }
]


@dp.message_handler(lambda message:message.text == 'Купить')
async def get_buying_list(message: types.Message):
    for product in products:
        # Формируем строку с информацией о продукте
        text = f'Название: {product["name"]}\nОписание: {product["description"]}\nЦена: {product["price"]}'

        # Отправляем сообщение с описанием продукта
        await message.answer(text)

        # Отправляем картинку продукта
        photo = InputFile(product['photo_path'])
        await message.answer_photo(photo)

    # Выводим Inline меню после информации о всех продуктах
    await message.answer('Выберите товар для покупки:', reply_markup=kb_product)


@dp.callback_query_handler(lambda call:call.data == 'product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели товар!")


@dp.callback_query_handler(lambda query: query.data == 'calories')
async def get_callback_button(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Вы выбрали расчет нормы калорий.')
    await bot.send_message(callback_query.from_user.id, 'Введите Ваш пол: 1 - Мужской; 2 - Женский')
    await UserState.gender.set()

@dp.callback_query_handler(lambda query: query.data == 'formulas')
async def get_formulas(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Вы выбрали формулы расчёта.')
    formula = (
        "Формула Миффлина-Сан Жеора:\n\n"
        "Для мужчин:\n"
        "BMR = 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) + 5\n\n"
        "Для женщин:\n"
        "BMR = 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(лет) - 161"
    )
    await bot.send_message(callback_query.from_user.id, formula)  # Отправляем формулу в ответ


@dp.message_handler(state=UserState.gender)
async def set_gender(message: Message, state: FSMContext):
    try:
        gender = int(message.text)
        if gender != 1 and gender != 2:
            raise ValueError("Пол человека должен быть положительным числом: 1 - Мужской, 2 - Женский")

        await state.update_data(gender=gender)  # Обновляем данные о поле человека
        await message.answer('Теперь введи свой возраст в годах:')
        await UserState.age.set()

    except ValueError:
        await message.answer('Пожалуйста, введи свой корректный пол в виде числа: 1 - Мужской, 2 - Женский')


@dp.message_handler(state=UserState.age)
async def set_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age <= 0 or age > 100:
            raise ValueError("Возраст должен быть положительным числом")

        await state.update_data(age=age)  # Обновляем данные о возрасте
        await message.answer('Теперь введи свой рост в сантиметрах:')
        await UserState.growth.set()

    except ValueError:
        await message.answer('Пожалуйста, введи корректный возраст в виде числа.')


@dp.message_handler(state=UserState.growth)
async def set_growth(message: Message, state: FSMContext):
    try:
        growth = float(message.text)
        if growth <= 50 or growth > 250:
            raise ValueError("Рост должен быть в пределах от 50 до 250 см")

        await state.update_data(growth=growth)  # Обновляем данные о росте
        await message.answer('И последний шаг – введи свой вес в килограммах:')
        await UserState.weight.set()

    except ValueError:
        await message.answer('Пожалуйста, введи корректный рост в виде числа.')


@dp.message_handler(state=UserState.weight)
async def set_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        if weight <= 10 or weight > 300:
            raise ValueError("Вес должен быть в пределах от 10 до 300 кг")

        await state.update_data(weight=weight)  # Обновляем данные о весе
        data = await state.get_data()  # Получаем все сохраненные данные
        await send_calories(data, message, state)  # Отправляем результат расчета калорий

    except ValueError:
        await message.answer('Пожалуйста, введи корректный вес в виде числа.')


@dp.message_handler()
async def all_messages(message: types.Message):
    await message.answer('Введите команду /start, чтобы начать общение.')


async def send_calories(data, message: Message, state: FSMContext):
    data = await state.get_data()
    gender = int(data['gender'])
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    if gender == 1:
        # Формула Миффлина-Сан Жеора для расчета базовой потребности в калориях
        bmr = 10 * weight + 6.25 * growth - 5 * age + 5  # пример для мужчин
    elif gender == 2:
        # Формула Миффлина-Сан Жеора для расчета базовой потребности в калориях
        bmr = 10 * weight + 6.25 * growth - 5 * age - 161  # пример для женщин
    else:
        await message.answer('Пожалуйста, введи свой корректный пол в виде числа.')

    await message.answer(f"Ваша базовая потребность в калориях составляет {bmr:.2f} ккал.")

    await state.finish()  # Завершаем работу машины состояний


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
