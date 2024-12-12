from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

API_TOKEN = '7900008680'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

buttom_1 = KeyboardButton(text='Рассчитать')
buttom_2 = KeyboardButton(text='Информация')
kb_repl = ReplyKeyboardMarkup([[buttom_1, buttom_2]], resize_keyboard=True)
# kb_repl.add(buttom_1)
# kb_repl.add(buttom_2)

kb_inline = InlineKeyboardMarkup()
buttom_1 = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
buttom_2 = InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb_inline.add(buttom_1)
kb_inline.add(buttom_2)


class UserState(StatesGroup):
    gender = State()
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(lambda message: message.text == 'Информация')
async def inform(message):
    await message.answer('Программа рассчета нормы калорий, исходя из вашего пола, возраста, роста и веса.')


@dp.message_handler(commands='start')
async def start_command(message: Message):
    await message.answer('Привет! Я помогу тебе рассчитать норму калорий.', reply_markup=kb_repl)


@dp.message_handler(lambda message: message.text == 'Рассчитать') # main_menu
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=kb_inline)


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
