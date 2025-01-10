import sqlite3
import telebot

def handle_admin_command(message, db):
    try:
        command_parts = message.text.split()
        if len(command_parts) < 2:
            bot.reply_to(message, "Неправильный формат команды. Используйте /admin <command> ...")
            return

        command = command_parts[1]

        if command == "set_balance":
            if len(command_parts) != 4:
                bot.reply_to(message, "Неправильный формат команды. Используйте /admin set_balance <user_id> <new_balance>")
                return
            user_id = int(command_parts[2])
            new_balance = float(command_parts[3])
            db.update_balance_admin(user_id, new_balance)
            bot.reply_to(message, f"Баланс пользователя {user_id} изменен на {new_balance:.2f}₽")

        elif command == "get_balance":
            if len(command_parts) != 3:
                bot.reply_to(message, "Неправильный формат команды. Используйте /admin get_balance <user_id>")
                return
            user_id = int(command_parts[2])
            balance = db.get_balance(user_id)
            bot.reply_to(message, f"Баланс пользователя {user_id}: {balance:.2f}₽")

        else:
            bot.reply_to(message, "Неизвестная команда админ-панели.")

    except (sqlite3.Error, sqlite3.IntegrityError) as e:
        bot.reply_to(message, f"Ошибка базы данных: {e}")
    except ValueError:
        bot.reply_to(message, "Неправильный формат данных. Проверьте введенные значения.")
    except IndexError:
        bot.reply_to(message, "Не хватает аргументов в команде.")
    except Exception as e:
        bot.reply_to(message, f"Произошла неизвестная ошибка: {e}")