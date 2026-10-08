import telebot
from config import *
from logic import *

bot = telebot.TeleBot(TOKEN)
manager = DB_Map(DATABASE)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот, который может показывать города на карте. Напиши /help для списка команд.")


@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.send_message(
        message.chat.id,
        "Доступные команды:\n"
        "/show_city <город> — показать город на карте\n"
        "/remember_city <город> — сохранить город в твой список\n"
        "/show_my_cities — показать все сохранённые города на карте\n"
        "Города указывай на английском языке."
    )


@bot.message_handler(commands=['show_city'])
def handle_show_city(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажи город: /show_city Moscow")
        return
    city_name = parts[1].strip()

    if not manager.get_coordinates(city_name):
        bot.send_message(message.chat.id, 'Такого города я не знаю. Напиши на английском!')
        return

    path = f'{city_name}.png'.replace(' ', '_')
    manager.create_grapf(path, [city_name])
    with open(path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)


@bot.message_handler(commands=['remember_city'])
def handle_remember_city(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Укажи город: /remember_city Moscow")
        return
    user_id = message.chat.id
    city_name = parts[1].strip()
    if manager.add_city(user_id, city_name):
        bot.send_message(message.chat.id, f'Город {city_name} успешно сохранен!')
    else:
        bot.send_message(message.chat.id, 'Такого города я не знаю. Убедись, что он написан на английском!')


@bot.message_handler(commands=['show_my_cities'])
def handle_show_visited_cities(message):
    cities = manager.select_cities(message.chat.id)
    if not cities:
        bot.send_message(message.chat.id, "У тебя пока нет сохранённых городов.")
        return

    path = f'user_{message.chat.id}_cities.png'
    manager.create_grapf(path, cities)
    with open(path, 'rb') as photo:
        bot.send_photo(message.chat.id, photo)


if __name__ == "__main__":
    manager.create_user_table()
    bot.polling(none_stop=True)