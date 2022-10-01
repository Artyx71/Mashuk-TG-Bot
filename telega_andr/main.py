import sqlite3
import telebot
from telebot import types
import configparser

menu = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
komp = types.KeyboardButton(text=f"Компетенции")
rub = types.KeyboardButton(text=f"Рубрики")
menu.add(komp, rub)

config = configparser.ConfigParser()
config.read("inf.ini")
token = config["help"]["token"]

bot = telebot.TeleBot(token)

con = sqlite3.connect("test.db", check_same_thread=False)
cursor = con.cursor()

def print_komp(tg_id): #вывод компетенций
    cursor.execute(f"select * from competention")
    comp = cursor.fetchall()
    comp_keyb = types.InlineKeyboardMarkup(row_width=2)
    for i in comp:
        btn_type = types.InlineKeyboardButton(text=f"{i[1]}", callback_data=f"/select_comp_{i[0]}")
        comp_keyb.add(btn_type)
    bot.send_message(tg_id, "Выбери комтенецию", reply_markup=comp_keyb)

def print_games(tg_id, id_comp): # вывод названий игр из категории
    cursor.execute(f"select * from games where id_c={id_comp}")
    games = cursor.fetchall()
    if len(games) == 0:
        bot.send_message(tg_id, "Игры отсутствуют в данной компетенции")
        print_komp(tg_id)
        return
    games_keyb = types.InlineKeyboardMarkup(row_width=2)
    for i in games:
        btn_type = types.InlineKeyboardButton(text=f"{i[2]}", callback_data=f"/select_game_{i[0]}_{id_comp}")
        games_keyb.add(btn_type)
    back = types.InlineKeyboardButton(text=f"Назад", callback_data=f"/games_back")
    games_keyb.add(back)
    bot.send_message(tg_id, "Выбери игру", reply_markup=games_keyb)

def game_info(id_game, tg_id, id_comp): #информация об игре
    cursor.execute(f"select * from games where id_g={id_game}")
    info = cursor.fetchone()
    games_keyb = types.InlineKeyboardMarkup(row_width=2)
    back = types.InlineKeyboardButton(text=f"Назад", callback_data=f"/info_back_{id_comp}")
    games_keyb.add(back)
    bot.send_photo(tg_id, open(f"pics/{info[5]}", 'rb'), caption=f"'{info[2]}'\n\nОписание: {info[3]}\nИздатель: {info[4]}", reply_markup=games_keyb)

def print_rubr(tg_id): #вывод рубрик
    cursor.execute(f"select * from rubr")
    rubr = cursor.fetchall()
    if len(rubr) == 0:
        bot.send_message(tg_id, "Рубрики пока отсутствуют")
    rubr_keyb = types.InlineKeyboardMarkup(row_width=2)
    for i in rubr:
        btn_type = types.InlineKeyboardButton(text=f"{i[1]}", callback_data=f"/select_rubr_{i[0]}")
        rubr_keyb.add(btn_type)
    bot.send_message(tg_id, "Выбери рубрику", reply_markup=rubr_keyb)

def rubr_info(rubr_id, tg_id): #информация о рубрике
    cursor.execute(f"select * from rubr where id_r={rubr_id}")
    info = cursor.fetchone()
    rub_keyb = types.InlineKeyboardMarkup(row_width=2)
    back = types.InlineKeyboardButton(text=f"Назад", callback_data=f"/rubr_back")
    rub_keyb.add(back)
    bot.send_message(tg_id, f"{info[2]}", reply_markup=rub_keyb)

@bot.message_handler(commands=['start', 'help']) #здесь читаются команды через слеш
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет!", reply_markup=menu)

@bot.message_handler(func=lambda m: True) #здесь текстовые команды читаются
def echo_all(message):
    sender = message.chat.id
    messg = message.text
    if messg == "Компетенции":
        print_komp(tg_id=sender)
    elif messg == "Рубрики":
        print_rubr(tg_id=sender)
    else:
        bot.send_message(sender, "Не понимаю такой команды", reply_markup=menu)

@bot.callback_query_handler(func=lambda call:True) #а здесь встроенные кнопки в сообщения читаются
def callback_worker(call):
    bot.answer_callback_query(callback_query_id=call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    call_text = call.data
    call_sender = call.message.chat.id
    if "/select_comp_" in call_text:
        id_comp = call_text.replace("/select_comp_", "")
        print_games(call_sender, id_comp)
    elif call_text == "/games_back":
        print_komp(call_sender)
    elif "/select_game_" in call_text:
        game_info(call_text.replace("/select_game_", "").split("_")[0], call_sender, call_text.replace("/select_game_", "").split("_")[1])
    elif "/info_back_" in call_text:
        print_games(call_sender, call_text.replace("/info_back_", ""))
    elif "/select_rubr_" in call_text:
        rubr_info(call_text.replace("/select_rubr_", ""), call_sender)
    elif call_text == "/rubr_back":
        print_rubr(tg_id=call_sender)

if __name__ == '__main__': #запуск
    bot.polling(none_stop=True)