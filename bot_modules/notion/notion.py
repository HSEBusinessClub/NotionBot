import requests
import os

import logging
import emoji
from aiogram import types, Dispatcher, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from psycopg2.extensions import cursor as psycopg2_cursor
from psycopg2 import connect
from db import ADD_USER

from bot_modules.notion.state import NotionState

NAME_BTN_TEXT = "Имя и фамилия"
EMAIL_BTN_TEXT = "Почта"


class Notion:
    """
    Class for dealing with Notion data
    """

    def __init__(
            self,
            cursor: psycopg2_cursor,
            connection: connect,
            dp: Dispatcher
    ) -> None:
        self.tasks_notion_db_id = "a902342198ff414abebf6be56acbdf0a"
        self.users_notion_db_id = "ef16c7929fe747be8b0ebfe0241b3477"
        self.url_base = "https://api.notion.com/v1/databases/"
        self.api_key = os.environ["NOTION_API_KEY"]
        self.cursor: psycopg2_cursor = cursor
        self.connect: connect = connection
        self.dp = dp

        self.emojis = {
            "smile": emoji.emojize(":grinning_face_with_smiling_eyes:"),
            "sad": emoji.emojize(":crying_face:"),
            "hi-hand": emoji.emojize(":waving_hand:")
        }

    def start(self):
        """
        start command
        """

        async def start_cmd(message: types.Message):
            text_ans = "Привет!" + self.emojis["hi-hand"] + "\n\n"
            text_ans += "Я Notion бот Бизнес-клуба HSE!\n\n"
            text_ans += "Буду напоминать тебе о задачах!\n\n"
            text_ans += "Для получения доступа выбери способ идентификации!"

            kb = [
                [
                    types.KeyboardButton(text=EMAIL_BTN_TEXT),
                    types.KeyboardButton(text=NAME_BTN_TEXT)
                ],
            ]

            keyboard = types.ReplyKeyboardMarkup(
                keyboard=kb,
                resize_keyboard=True,
                input_field_placeholder="Выберите способ подачи"
            )

            await message.answer(
                text_ans,
                reply_markup=keyboard
            )

        return start_cmd

    def set_user_state(self, new_state: NotionState, text: str):

        async def set_state_cmd(message: types.Message, state: FSMContext):
            await message.answer(text)
            await state.set_state(new_state)

        return set_state_cmd

    def add_user_with_email(self):
        """
        returns async func, which add person to db on email
        """

        async def add_user_cmd(message: types.Message, state: FSMContext):
            """
            async func, which add person to db
            """

            entities = message.entities or []

            user_email = None
            for item in entities:
                if item.type == "email":
                    user_email = item.extract_from(message.text)

            if not user_email:
                # не нашли почту в введённом сообщении
                text_ans = "Нужно указать почту!"
                text_ans += self.emojis["sad"]
                text_ans += "\nВведите почту заново"

                await message.reply(text_ans)
                return

            notion_users = [{"email": user_email}]  # self.get_user_notion_db()
            for user in notion_users:
                if (
                    "email" in user.keys()
                    and user["email"] == user_email   # ЗАГЛУШКА
                ):
                    ADD_USER_QUERY = ADD_USER(user_email, message.chat.id)
                    logging.log(level=logging.INFO, msg=ADD_USER_QUERY)
                    self.cursor.execute(ADD_USER_QUERY)
                    self.connect.commit()

                    text_ans = f"Отлично, {user_email}, "
                    text_ans += "буду стараться быть полезным"
                    text_ans += self.emojis["smile"]

                    await message.answer(
                        text_ans,
                        reply_markup=types.ReplyKeyboardRemove()
                    )
                    await state.set_state(NotionState.user_logged)
                    break
            else:
                text_ans = "Пользователя с такой почтой нету"
                text_ans += self.emojis["sad"]
                text_ans += "\nПопробуйте начать команду заново"
                text_ans += self.emojis["smile"]

                await message.reply(text_ans)
                await state.set_state(NotionState.typing_email_to_login)

        return add_user_cmd

    def add_user_with_name(self):

        async def add_user_cmd(message: types.Message, state: FSMContext):

            notion_users = [{"aba": "caba"}]  # self.get_user_notion_db()

            if len(message.text.split()) != 2:
                text_ans = "Нужно указать имя и фамилию!"
                text_ans += "\nВведите заново"
                text_ans += self.emojis["smile"]

                await message.reply(text_ans)
                return

            name, surname = message.text.split()

            for user in notion_users:
                if name == surname:  # ЗАГЛУШКА 2 строки
                    ADD_USER_QUERY = ADD_USER(name + " " + surname,
                                              message.chat.id)
                    self.cursor.execute(ADD_USER_QUERY)
                    self.connect.commit()

                    text_ans = f"Отлично, {name}, "
                    text_ans += "буду стараться быть полезным"
                    text_ans += self.emojis["smile"]

                    await message.answer(text_ans, reply_markup=None)
                    await state.set_state(NotionState.logged)
                    break

            else:
                text_ans = "Такого имени в таблице нет"
                text_ans += self.emojis["sad"] + "\n\n"
                text_ans += "Введите данные заново"

                await message.reply(
                    text_ans,
                    reply_markup=types.ReplyKeyboardRemove()
                )
                await state.set_state(NotionState.typing_name_to_login)

        return add_user_cmd

    def get_user_notion_db(self) -> [dict]:
        """
        returns all users in Notion db
        """

        url_req = self.url_base + f"{self.users_notion_db_id}/query"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key,
            "Notion-Version": "2022-06-28"
        }

        query_params = {
            "filter": {
                {
                    "property": "Статус ",
                    "equals": "Активный"
                }
            }
        }

        resp = requests.post(url_req, headers=headers, json=query_params)
        if (299 >= resp.status_code() >= 200):
            return resp.json()
        raise Exception("wrong query")

    def get_undone_tasks_db(self) -> dict:
        """
        returns all tasks with status
        "Backlog" / "Not started" / "In progress"
        """

        url_req = self.url_base + f"{self.tasks_notion_db_id}/query"

        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key,
            "Notion-Version": "2022-06-28"
        }

        query_params = {
            "filter": {
                "or": [
                    {
                        "property": "Статус",
                        "equals": "Backlog"
                    },
                    {
                        "property": "Статус",
                        "equals": "Not started"
                    },
                    {
                        "property": "Статус",
                        "equals": "In progress"
                    }
                ]
            }
        }

        resp = requests.post(url_req, data=query_params, headers=headers)
        if (299 >= resp.status_code() >= 200):
            return resp.json()
        raise Exception("wrong query")

    def set_routes(self):
        """
        add notion routes to bot
        """
        add_user_with_name = self.add_user_with_name()
        add_user_with_email = self.add_user_with_email()

        set_email_state = self.set_user_state(
            NotionState.typing_email_to_login,
            text="Введите почту, которая указана в notion"
        )
        set_name_state = self.set_user_state(
            NotionState.typing_name_to_login,
            text="Введите имя и фамилию как указано в notion"
        )

        self.dp.message(
            F.text == NAME_BTN_TEXT
        )(set_name_state)

        self.dp.message(
            NotionState.typing_name_to_login
        )(add_user_with_name)

        self.dp.message(
            F.text == EMAIL_BTN_TEXT,
        )(set_email_state)

        self.dp.message(
            NotionState.typing_email_to_login
        )(add_user_with_email)

        self.dp.message(Command("start"))(self.start())
