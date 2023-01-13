import os

import logging

import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, KeyboardButton
from aiogram.utils import executor

API_TOKEN = os.environ.get('API_TOKEN')
TOKEN = os.environ.get('TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO)
#
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# создаём форму и указываем поля
class Form(StatesGroup):
    name = State()
    age = State()
    gender = State()


# Начинаем наш диалог


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await Form.name.set()
    await message.reply("Привет! Как тебя зовут?")


# Добавляем возможность отмены, если пользователь передумал заполнять
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('ОК')


# Сюда приходит ответ с именем
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await Form.next()
    await message.reply("Сколько тебе лет?")


# Проверяем возраст
@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.age)
async def process_age_invalid(message: types.Message):
    return await message.reply("Напиши возраст или напиши /cancel")


# Принимаем возраст и узнаём пол
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.age)
async def process_age(message: types.Message, state: FSMContext):
    await Form.next()
    await state.update_data(age=int(message.text))

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("М", "Ж")
    markup.add("Другое")

    await message.reply("Укажи пол (кнопкой)", reply_markup=markup)


# Проверяем пол
@dp.message_handler(lambda message: message.text not in ["М", "Ж", "Другое"], state=Form.gender)
async def process_gender_invalid(message: types.Message):
    return await message.reply("Не знаю такой пол. Укажи пол кнопкой на клавиатуре")


# Сохраняем пол, выводим анкету
@dp.message_handler(state=Form.gender)
async def process_gender(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['gender'] = message.text

        p_data = {
            'external_id': message.from_user.id,
            'name': data['name'],
            'age': data['age'],
            'gender': data['gender']
        }
        # send personal data to save it
        await post_data(review_data=p_data, url='http://localhost:8000/bot_users/')

    await Form.next()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    organization = get_organizations()

    for item in organization:
        markup.add(KeyboardButton(item['org_name']))

    await message.reply('Choose organization', reply_markup=markup)


@dp.message_handler(state=Form.organization)
async def process_organization(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        organization = message.text
        for item in get_organizations():
            if item['org_name'] == organization:
                data['organization'] = item['id']
                data['organization_name'] = item['org_name']
                break

    await Form.next()
    await message.reply('Write review')


@dp.message_handler(state=Form.review)
async def process_review(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['review'] = message.text

        markup = types.ReplyKeyboardRemove()

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('Hi! Nice to meet you', md.bold(data['name'])),
                md.text('Age:', md.code(data['age'])),
                md.text('Gender', data['gender']),
                md.text('Organization', data['organization_name']),
                md.text('Your review', data['review']),
                sep='\n',
            ),
            reply_markup=markup,
            parse_mode=ParseMode.MARKDOWN
        )

        await post_data({
            'organization': int(data['organization']),
            'bot_user': int(message.from_user.id),
            'content': data['review']
        }, url='http://localhost:8000/reviews/')

    await Form.organization.set()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
