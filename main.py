import random
import re
import sqlite3
import time

import telebot
from telebot import types

BOT_TOKEN = 'Ваш токен'  # Не забудьте заменить на ваш токен
bot = telebot.TeleBot(BOT_TOKEN)

DATABASE_FILE = 'casino.db'  # Файл базы данных

BONUS_COOLDOWN = 3600  # 3600 секунд = 1 час (настройте по своему усмотрению)
BONUS_MIN = 1000  # Минимальный бонус
BONUS_MAX = 10000 # Максимальный бонус


# Класс для работы с базой данных
class CasinoDB:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0.0,
                last_bonus INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def get_balance(self, user_id):
        self.cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0.0

    def get_last_bonus(self, user_id):
        self.cursor.execute("SELECT last_bonus FROM users WHERE id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0

    def update_balance(self, user_id, amount):
        try:
            self.cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка обновления баланса: {e}")
            return False

    def update_last_bonus(self, user_id):
        try:
            self.cursor.execute("UPDATE users SET last_bonus = ? WHERE id = ?", (int(time.time()), user_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка обновления last_bonus: {e}")
            return False

    def add_user(self, user_id):
        try:
            self.cursor.execute("INSERT INTO users (id, balance) VALUES (?, ?)", (user_id, 0.0))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка добавления пользователя: {e}")
            return False

    def close(self):
        self.conn.close()


answer = ["Бесспорно", "Предрешено", "Никаких сомнений", "Определённо да", "Можешь быть уверен в этом",
          "Мне кажется - да", "Вероятнее всего", "Хорошие перспективы", "Знаки говорят - да", "Да",
          "Пока неясно, попробуй снова", "Спроси позже", "Лучше не рассказывать",
          "Сейчас нельзя предсказать", "Сконцентрируйся и спроси опять", "Даже не думай",
          "Мой ответ - нет", "По моим данным - нет",
          "Перспективы не очень хорошие", "Весьма сомнительно"]


@bot.message_handler(commands=["play", "команды", "command"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Профиль")
    btn2 = types.KeyboardButton("Казино")
    btn3 = types.KeyboardButton("Магический шар")
    btn4 = types.KeyboardButton("/help")
    markup.add(btn1), markup.add(btn2), markup.add(btn3), markup.add(btn4)
    bot.send_message(message.chat.id, "Мои команды:\n1️⃣Профиль\n2️⃣Казино\n3️⃣Магический шар", reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """<b>Здравствуйте, дорогие игроки!</b>

С величайшим удовольствием представляю вам мою новую изысканную игру под названием "TashGames". В этом руководстве я с удовольствием раскрою перед вами тонкости и нюансы этого захватывающего бота, а также поведаю о доступных вам командах, которые откроют перед вами двери в мир безграничных возможностей.

<b>Профиль:</b> Эта команда предоставляет вам доступ к вашему личному профилю, где вы сможете увидеть свой ник, уникальный ID и текущий баланс.

<b>Казино:</b> Эта игра, словно рулетка судьбы, предлагает вам шанс испытать удачу. Введите `казино [сумма]` чтобы сделать ставку. В случае выигрыша вы удвоите свою ставку, а в случае поражения — потеряете её. В будущем я планирую обогатить правила этой игры, чтобы сделать процесс еще более увлекательным и непредсказуемым.

<b>Магический шар:</b> Эта команда подарит вам возможность заглянуть в будущее, словно с помощью волшебной хрустальной сферы. Введите `магический шар` и затем задайте свой вопрос. Однако не стоит забывать, что ответ на ваш вопрос будет случайным, как если бы вы обратились к таинственной цыганке на вокзале.

<b>Баланс:</b> Эта команда позволит вам в любой момент узнать ваш текущий баланс, чтобы вы могли контролировать свои финансовые потоки. Введите `баланс`.

<b>Список команд (/help):</b> Эта команда выведет это справочное сообщение.

<b>Желаю вам незабываемого времяпрепровождения в "TashGames"!</b>"""
    bot.send_message(message.chat.id, help_text, parse_mode='html')


@bot.message_handler(commands=['commands'])
def commands_command(message):
    bot.send_message(message.chat.id, message)


@bot.message_handler(commands=['casino'])
def handle_casino(message):
    user_id = message.from_user.id
    db = CasinoDB(DATABASE_FILE)
    if not db.get_balance(user_id):  # Проверка существования пользователя
        db.add_user(user_id)
    balance = db.get_balance(user_id)
    db.close()
    bot.reply_to(message, f"Добро пожаловать в казино! Ваш баланс: {balance:.2f}")


@bot.message_handler(func=lambda message: message.text.lower() == "казино")
def handle_casino_text(message):
    bot.send_message(message.chat.id, f"{message.from_user.username}, использование: «казино [сумма]» ❌")


@bot.message_handler(func=lambda message: message.text.lower() == 'профиль')
def profile(message):
    user_id = message.from_user.id
    db = CasinoDB(DATABASE_FILE)
    balance = db.get_balance(user_id)
    db.close()
    bot.send_message(message.chat.id,
                     f'{message.from_user.username}, Ваш профиль:\n'
                     f'<b>🔎 ID:</b> {message.from_user.id}\n'
                     f'<b>💰 Баланс:</b> {balance:.2f}₽\n'
                     f'<b>📅 Дата регистрации: [SOON]</b>',
                     parse_mode='html')

@bot.message_handler(func=lambda message: message.text.lower() == 'баланс')
def balance(message):
    user_id = message.from_user.id
    db = CasinoDB(DATABASE_FILE)
    balance = db.get_balance(user_id)
    db.close()
    bot.send_message(message.chat.id, f'<b>💰 Баланс:</b> {balance:.2f}₽', parse_mode='html')


@bot.message_handler(func=lambda message: message.text.lower() == "магический шар")
def magic_ball(message):
    bot.send_message(message.chat.id, "Задайте свой вопрос!")
    bot.register_next_step_handler(message, process_question)


def process_question(message):
    if re.fullmatch(r"[\w\s\?]*", message.text):
        bot.send_message(message.chat.id, random.choice(answer))
    else:
        bot.send_message(message.chat.id,
                         "Пожалуйста, задайте вопрос, используя только буквы, цифры и знаки вопроса")


@bot.message_handler(func=lambda message: re.match(r"^казино\s+(\d+(\.\d+)?)$", message.text, re.IGNORECASE))
def handle_casino_bet(message):
    try:
        match = re.match(r"^казино\s+(\d+(\.\d+)?)$", message.text, re.IGNORECASE)
        bet_amount = float(match.group(1))

        user_id = message.from_user.id
        db = CasinoDB(DATABASE_FILE)  # Создаем соединение здесь

        if not db.get_balance(user_id):
            db.add_user(user_id)
        balance = db.get_balance(user_id)

        if bet_amount > balance:
            bot.reply_to(message, "Недостаточно средств на балансе!")
        elif bet_amount <= 0:
            bot.reply_to(message, "Сумма ставки должна быть больше нуля!")
        else:
            result = random.choice(['win', 'lose'])
            if result == 'win':
                winnings = bet_amount
                db.update_balance(user_id, winnings)
                bot.reply_to(message, f"Вы выиграли! Ваш новый баланс: {db.get_balance(user_id):.2f}₽")
            else:
                db.update_balance(user_id, -bet_amount)
                bot.reply_to(message, f"Вы проиграли! Ваш новый баланс: {db.get_balance(user_id):.2f}₽")

        db.close()  # Закрываем соединение здесь

    except ValueError:
        bot.reply_to(message, "Неправильный формат ставки. Введите число после слова 'казино'.")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")


@bot.message_handler(commands=['bonus'])
def handle_bonus(message):
    user_id = message.from_user.id
    db = CasinoDB(DATABASE_FILE)
    if not db.get_balance(user_id):  # Проверка на существование пользователя
        db.add_user(user_id)
    last_bonus = db.get_last_bonus(user_id)
    current_time = int(time.time())

    if current_time - last_bonus >= BONUS_COOLDOWN:
        bonus_amount = random.randint(BONUS_MIN, BONUS_MAX)
        if db.update_balance(user_id, bonus_amount) and db.update_last_bonus(user_id):
            bot.reply_to(message,
                         f"Поздравляем! Вы получили бонус в размере {bonus_amount}₽! "
                         f"Ваш новый баланс: {db.get_balance(user_id):.2f}₽")
        else:
            bot.reply_to(message, "Ошибка при начислении бонуса.")
    else:
        time_left = BONUS_COOLDOWN - (current_time - last_bonus)
        bot.reply_to(message, f"Вы можете получить следующий бонус через {time_left} секунд.")
    db.close()


bot.infinity_polling()
