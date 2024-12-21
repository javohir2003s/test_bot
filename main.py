import logging
import psycopg2
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F
import asyncio
import random
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# PostgreSQL serveriga ulanish
conn = psycopg2.connect(
    dbname="testlar_bazasi",  # O'zingizning ma'lumotlar bazasi nomini kiriting
    user="postgres",         # O'zingizning foydalanuvchi nomini kiriting
    password="Trader2024.",     # O'zingizning parolingizni kiriting
    host="localhost",             # Agar masofadan ulanayotgan bo'lsangiz, server IP manzilini kiriting
    port="5432"                   # PostgreSQLning standart porti
)

# Kursorni yaratish
cursor = conn.cursor()

API_TOKEN = '7905500529:AAE7tiyUpujKaXYlwsRQwxNroVSWcMdZx3Y'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# Foydalanuvchi uchun test holatini saqlash
user_tests = {}
user_test_progress = {}


@dp.message(lambda message: message.text == "/start")
async def start_handler(message: types.Message):
    # Klaviatura yaratish
    button_start = KeyboardButton(text="Testni boshlash")
    button_create_test = KeyboardButton(text="Test yaratish")
    button_help = KeyboardButton(text="Yordam")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_start, button_create_test, button_help]],
        resize_keyboard=True  # Klaviaturani avtomatik ravishda o'lchamini o'zgartirish
    )

    # Foydalanuvchiga salomlashish va klaviaturani yuborish
    await message.answer("Salom! Botga xush kelibsiz:", reply_markup=keyboard)

@dp.message(lambda message: message.text == 'Yordam')
async def help(mesage: types.Message):
    await mesage.answer("Admin bilan bog'lanish @pozitiv_bola")

@dp.message(lambda message: message.text == 'Testni tugatish')
async def finish_test(message: types.Message):
    if message.from_user.id in user_tests:
        # Agar foydalanuvchi test yaratish jarayonida bo'lsa
        if user_tests[message.from_user.id]['state'] == 'waiting_for_question':
            # Foydalanuvchi hali savol qo'shish jarayonida bo'lsa
            del user_tests[message.from_user.id]
            button_start = KeyboardButton(text="Testni boshlash")
            button_create_test = KeyboardButton(text="Test yaratish")
            button_help = KeyboardButton(text="Yordam")

            keyboard = ReplyKeyboardMarkup(
                    keyboard=[[button_start, button_create_test, button_help]],
                    resize_keyboard=True  # Klaviaturani avtomatik ravishda o'lchamini o'zgartirish
                )
            await message.answer("Test yaratish jarayoni tugatildi", reply_markup=keyboard)
        else:
            await message.answer("Test muvaffaqqiyatli qo'shildi!")
    else:
        await message.answer("Hozirda yaratish jarayonida bo'lmagan test mavjud.")


@dp.message(lambda message: message.text == 'Test yaratish')
async def create_test(message: types.Message):
    
    user_tests[message.from_user.id] = {'state': "waiting_for_question"}
    user_tests[message.from_user.id]['question_index'] = 1

    button_finish = KeyboardButton(text="Testni tugatish")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_finish]],
        resize_keyboard=True  # Klaviaturani avtomatik ravishda o'lchamini o'zgartirish
    )
    await message.answer("Testni savolini kiriting: ", reply_markup=keyboard)

@dp.message(lambda message: message.from_user.id in user_tests and user_tests[message.from_user.id]['state'] == "waiting_for_question")
async def add_question(message: types.Message):
    question_text = message.text
    user_tests[message.from_user.id]["question_text"] = question_text
    user_tests[message.from_user.id]['state'] = "waiting_for_option_a"


    await message.answer("Variant A ni kiriting: ")


@dp.message(lambda message: message.from_user.id in user_tests and user_tests[message.from_user.id]['state'] == 'waiting_for_option_a')
async def set_option_a(message: types.Message):
    user_tests[message.from_user.id]['option_a'] = message.text
    user_tests[message.from_user.id]['state'] = 'waiting_for_option_b'

    await message.answer("Variant B ni kiriting:")


@dp.message(lambda message: message.from_user.id in user_tests and user_tests[message.from_user.id]['state'] == 'waiting_for_option_b')
async def set_option_b(message: types.Message):
    user_tests[message.from_user.id]['option_b'] = message.text
    user_tests[message.from_user.id]['state'] = 'waiting_for_option_c'

    await message.answer("Variant C ni kiriting:")

@dp.message(lambda message: message.from_user.id in user_tests and user_tests[message.from_user.id]['state'] == 'waiting_for_option_c')
async def set_option_c(message: types.Message):
    user_tests[message.from_user.id]['option_c'] = message.text
    user_tests[message.from_user.id]['state'] = 'waiting_for_option_d'

    await message.answer("Variant D ni kiriting:")

@dp.message(lambda message: message.from_user.id in user_tests and user_tests[message.from_user.id]['state'] == 'waiting_for_option_d')
async def set_option_d(message: types.Message):
    user_tests[message.from_user.id]['option_d'] = message.text
    user_tests[message.from_user.id]['state'] = 'waiting_for_correct_option'

    await message.answer("To'g'ri variantni (A, B, C, D) kiriting:")

@dp.message(lambda message: message.from_user.id in user_tests and user_tests[message.from_user.id]['state'] == 'waiting_for_correct_option')
async def set_correct_option(message: types.Message):
    correct_option = message.text.upper()

    if correct_option not in ['A', 'B', 'C', 'D']:
        await message.answer("Iltimos, to'g'ri variantni (A, B, C, D) kiriting:")
        return
    question_text = user_tests[message.from_user.id]['question_text']
    option_a = user_tests[message.from_user.id]['option_a']
    option_b = user_tests[message.from_user.id]['option_b']
    option_c = user_tests[message.from_user.id]['option_c']
    option_d = user_tests[message.from_user.id]['option_d']

    cursor.execute("""
            INSERT INTO questions (question, option1, option2, option3, option4, correct_option)
            VALUES (%s, %s, %s, %s, %s, %s)
                   
        """, (question_text,option_a, option_b, option_c, option_d, correct_option))
    
    conn.commit()

    user_tests[message.from_user.id]['state'] = 'waiting_for_question'
    user_tests[message.from_user.id]['question_index'] += 1

    button_finish = KeyboardButton(text="Testni tugatish")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_finish]],
        resize_keyboard=True  # Klaviaturani avtomatik ravishda o'lchamini o'zgartirish
    )

    await message.answer(f"Yangi savolni kiriting  (Savol {user_tests[message.from_user.id]['question_index']}):", reply_markup=keyboard)


score = {}

# Testni boshlash komandasi
@dp.message(lambda message: message.text == "Testni boshlash")
async def start_test(message: types.Message):
    # Tasodifiy savolni olish
    cursor.execute("SELECT id, question, option1, option2, option3, option4, correct_option FROM questions ORDER BY random() LIMIT 1")
    row = cursor.fetchone()
    
    if row:

        question_id, question_text, option_a, option_b, option_c, option_d, correct_option = row
        user_test_progress[message.from_user.id] = {
            "question_id": question_id,
            "correct_option": correct_option,
            'score': 0
        }

        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="A"), KeyboardButton(text="B")],
                [KeyboardButton(text="C"), KeyboardButton(text="D")],
                [KeyboardButton(text="exit")]   

            ],
            resize_keyboard=True
        )

        await message.answer(f"Savol: {question_text}\n\nA: {option_a}\nB: {option_b}\nC: {option_c}\nD: {option_d}", reply_markup=keyboard)

    else:
        await message.answer("Hozircha test savollari mavjud emas.")

@dp.message(lambda message: message.text in ['A', 'B', 'C', 'D'] and message.from_user.id in user_test_progress)
async def check_answer(message: types.Message):
    user_id = message.from_user.id
    user_data = user_test_progress[user_id]
    
    if message.text == user_data['correct_option']:
        user_test_progress[user_id]['score'] += 1
        await message.answer(f"To'g'ri javob! Balingiz {user_test_progress[user_id]['score']} Keyingi savolga o'tamiz.")
    else:
        await message.answer("Noto'g'ri javob. Yana urinib ko'ring!")

    cursor.execute("SELECT id, question, option1, option2, option3, option4, correct_option FROM questions WHERE id != %s ORDER BY random() LIMIT 1", (user_data['question_id'],))
    row = cursor.fetchone()

    if row:
        question_id, question_text, option_a, option_b, option_c, option_d, correct_option = row

        # Foydalanuvchi uchun yangi savolni saqlash
        user_test_progress[user_id] = {
            'question_id': question_id,
            'correct_option': correct_option,
            "score": user_test_progress[user_id]['score']
        }

        keyboard = ReplyKeyboardMarkup(
        keyboard=[
                [KeyboardButton(text="A"), KeyboardButton(text="B")],
                [KeyboardButton(text="C"), KeyboardButton(text="D")],
                [KeyboardButton(text="exit")]   
            ],
            resize_keyboard=True
        )

        await message.answer(f"Savol: {question_text}\n\nA: {option_a}\nB: {option_b}\nC: {option_c}\nD: {option_d}", reply_markup=keyboard)
    else:
        del user_test_progress[user_id]
        button_start = KeyboardButton(text="Testni boshlash")
        button_create_test = KeyboardButton(text="Test yaratish")
        button_help = KeyboardButton(text="Yordam")

        keyboard = ReplyKeyboardMarkup(
                keyboard=[[button_start, button_create_test, button_help]],
                resize_keyboard=True  # Klaviaturani avtomatik ravishda o'lchamini o'zgartirish
                )
        await message.answer("Barcha savollar tugadi!", reply_markup=keyboard   )

# Foydalanuvchi javobi
@dp.message(lambda message: message.text.lower() == "exit")
async def exit_handler(message: types.Message):
    button_start = KeyboardButton(text="Testni boshlash")
    button_create_test = KeyboardButton(text="Test yaratish")
    button_help = KeyboardButton(text="Yordam")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_start, button_create_test, button_help]],
        resize_keyboard=True  # Klaviaturani avtomatik ravishda o'lchamini o'zgartirish
                )
    await message.answer(f"Test tugatildi. Siz {user_test_progress[message.from_user.id]['score']} ball to'pladingiz", reply_markup=keyboard)



# Botni ishga tushirish
async def main():
    dp.message.register(start_handler)
    dp.message.register(finish_test)
    dp.message.register(create_test)
    dp.message.register(add_question)
    dp.message.register(set_option_a)
    dp.message.register(set_option_b)
    dp.message.register(set_option_c)
    dp.message.register(set_option_d)
    dp.message.register(set_correct_option)
    dp.message.register(start_test)
    dp.message.register(exit_handler)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
