import telebot
from telebot import types  # библиотека для кнопок
import time  # для оптимизации бота
import sqlite3
import os #работа с файлами
import uuid
import pandas as pd

bot = telebot.TeleBot("5392461531:AAGdArPbmztFJv_YbbWU3cDiw5WXrs6EWwQ")

conn = sqlite3.connect('updatedDB.db', check_same_thread=False)
cursor = conn.cursor()
cursorObj = conn.cursor()

cursorObj.execute("""CREATE TABLE IF NOT EXISTS Users (
               users_id  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
               user_id   VARCHAR    UNIQUE ON CONFLICT IGNORE,
               user_name VARCHAR    NOT NULL ON CONFLICT IGNORE);""")
conn.commit()

cursorObj.execute("""CREATE TABLE IF NOT EXISTS Bots (
               bot_id   VARCHAR PRIMARY KEY UNIQUE ON CONFLICT IGNORE NOT NULL,
               bot_name VARCHAR NOT NULL,
               users_id INTEGER REFERENCES Users (users_id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL);""")
conn.commit()

cursorObj.execute("""CREATE TABLE IF NOT EXISTS Buttons (
               button_id      INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
               button_name    VARCHAR NOT NULL,
               button_text    TEXT,
               button_filepath TEXT,
               bot_id         VARCHAR REFERENCES Bots (bot_id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL);""")
conn.commit()

def db_users(userID: str, userName: str, ):
    cursor.execute('INSERT INTO Users (user_id, user_name) VALUES (?, ?)', (userID, userName, ))
    conn.commit()

def db_bots(bottoken: str, botname: str, usersID: int,):
    cursor.execute('INSERT INTO Bots (bot_id, bot_name, users_id) VALUES (?, ?, ?)', (bottoken, botname, usersID, ))
    conn.commit()

def db_buttons_t(button_name: str, button_txt: str, botID: str,):
    cursor.execute('INSERT INTO Buttons (button_name, button_text, bot_id) VALUES (?, ?, ?)', (button_name, button_txt, botID,))
    conn.commit()

def db_buttons_f(buttn_name: str, file_path: str, botsID: str,):
    cursor.execute('INSERT INTO Buttons (button_name, button_filepath, bot_id) VALUES (?, ?, ?)', (buttn_name, file_path, botsID,))
    conn.commit()

def db_buttons_tf(butn_name: str, butn_txt: str, files_path: str, boteID: str,):
    cursor.execute('INSERT INTO Buttons (button_name, button_text, button_filepath, bot_id) VALUES (?, ?, ?, ?)', (butn_name, butn_txt, files_path, boteID,))
    conn.commit()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('/createbot')
    itembtn5 = types.KeyboardButton('/templates')
    itembtn2 = types.KeyboardButton('/addbuttons')
    itembtn3 = types.KeyboardButton('/deletebot')
    itembtn4 = types.KeyboardButton('/about')
    markup.add(itembtn1, itembtn5, itembtn2, itembtn3, itembtn4)
    name = message.from_user.first_name
    if name == 'Builder':
        name = 'Пользователь'
    else:
        pass
    bot.send_message(message.chat.id, "Здравствуйте, "
                     + name
                     + ". Это конструктор Telegram-ботов. Выберите одну из предложенных ниже команд для начала работы."
                       "\nКоманда /createbot позволит создать бота в конструкторе."
                       "\nКоманда /templates позволит выбрать шаблон будущего телеграмм-бота."
                       "\nКоманда /addbuttons позволит улучшить ваших созданных телеграмм-ботов."
                       "\nКоманда /deletebot позволит удалить бота (телеграмм-бот будет удален из базы данных "
                       "и не подлежит дальнейшей работе в конструкторе)."
                       "\nКоманда /about позволит посмотреть инструкцию по работе с конструктором."
                     , reply_markup=markup)

@bot.message_handler(commands=['createbot'])
def new_bot(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id, "Вы выбрали создание нового бота")
    msg = bot.send_message(message.chat.id, 'Введите название бота', reply_markup=markup)
    global user_ID
    user_ID = message.from_user.id
    global user_Name
    user_Name = message.from_user.first_name
    #print(user_Name)
    db_users(userID=user_ID, userName=user_Name)
    cur = conn.cursor()
    cur.execute(f"SELECT users_id FROM Users WHERE user_name='{user_Name}';")
    global users_ID
    dbCallResult = cur.fetchone()
    users_ID = int(dbCallResult[0])
    bot.register_next_step_handler(msg, get_token)

def get_token(message):
    msg = bot.send_message(message.chat.id, 'Введите токен бота')
    global bot_name
    bot_name = message.text
    bot.register_next_step_handler(msg, bot_created)

def bot_created(message):
    global bot_token
    bot_token = message.text
    #print(bot_token, bot_name, users_ID)
    #db_bots(bottoken=bot_token, botname=bot_name, usersID=users_ID)
    my_file = open(bot_name + '.py', 'a', encoding="utf-8")
    text_for_file = "import telebot\nfrom telebot import types\n" \
                    'token=' + '"' + bot_token + '"\nbot=telebot.TeleBot(token)\n' \
                                            "\n@bot.message_handler(commands=['start'])\ndef start_message(message):" \
                            "\n\tbot.send_message(message.chat.id,'Привет, я " + bot_name + "')\n"
    my_file.write(text_for_file)
    my_file.close()
    my_file = open(bot_name + '.py', 'a', encoding="utf-8")
    text_for_file = "\nbot.infinity_polling()"
    my_file.write(text_for_file)
    my_file.close()
    key = types.InlineKeyboardMarkup(row_width=1)
    butons = types.InlineKeyboardButton(text="Сохранить информацию о боте",
                                       callback_data="Сохранить информацию о боте")
    butond = types.InlineKeyboardButton(text='Не сохранять информацию о боте',
                                        callback_data='Не сохранять информацию о боте')
    key.add(butons, butond)
    bot.send_message(message.chat.id, f"Ваш бот {bot_name} почти создан, для окончания этого процесса "
                                      f"сохраните информацию о нем.", reply_markup=key)

@bot.callback_query_handler(func=lambda call: True)
def bot_save(call):
    if call.data == 'Сохранить информацию о боте':
        bot.send_message(call.message.chat.id, "Бот успешно создан. Его данные успешно занесены в базу данных!"
                                                "\nДля добавления к нему различных кнопок воспользуйтесь /addbuttons или выберите шаблон через /templates")
        db_bots(bottoken=bot_token, botname=bot_name, usersID=users_ID)
        bot.delete_message(call.message.chat.id, call.message.id)


    elif call.data == 'Не сохранять информацию о боте':
        bot.send_message(call.message.chat.id, "Бот не создан. Данные о боте не будут занесены в базу данных!"
                                                "\nДля начала работы конструктора воспользуйтесь командой  /start")
        bot.delete_message(call.message.chat.id, call.message.id)

    elif call.data == 'Создать кнопку с текстом':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание кнопки с текстом.\nВведите нзавание для кнопки с текстом.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_cont)
    elif call.data == 'Создать кнопку с фотографией':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание кнопки с фото.\nВведите название для кнопки с фото.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_photo)
    elif call.data == 'Создать кнопку с видео':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание кнопки с видео.\nВведите название для кнопки с видео.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_video)
    elif call.data == 'Создать уникальную кнопку':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание уникальной кнопки.'
                                                     '\nВведите название для уникальной кнопки.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_integ_cont)

    elif call.data == 'Текстовка':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание дополнительной кнопки с текстом. ' 
                                                     '\nВведите название для дополнительной кнопки с текстом.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_cont)
    elif call.data == 'Добавить другую кнопку':
        message = bot.send_message(call.message.chat.id, 'Вы были перенесены к пункту выбора кнопок.')
        bot.delete_message(call.message.chat.id, call.message.id)
        up_start(message)
    elif call.data == 'Уникальная':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание дополнительной уникальной кнопки. '
                                                     '\nВведите название для дополнительной уникальной кнопки.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_integ_cont)
    elif call.data == 'Фотография':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание дополнительной кнопки с фото. '
                                                     '\nВведите название для дополнительной кнопки с фото.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_photo)
    elif call.data == 'Видеозапись':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание дополнительной кнопки с видео. '
                                                     '\nВведите название для дополнительной кнопки с видео.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_video)

    elif call.data == 'Вернуться на главный экран':
        message = bot.send_message(call.message.chat.id, 'Вы успешно вернулись на стартовый экран.')
        bot.delete_message(call.message.chat.id, call.message.id)
        send_welcome(message)

    elif call.data == 'Завершить редактирование бота':
        message=bot.send_message(call.message.chat.id, f'Вы завершили редактирование своего бота {str(nameofthebot[0])}.')
        bot.delete_message(call.message.chat.id, call.message.id)

        with open(userbot+".py", "r", encoding='utf-8') as f:
            bot.send_document(message.chat.id, f)
            f.close()

        with open(userbot + '.py', 'r', encoding="utf-8") as f:
            old_data = f.read()
            new_data = old_data.replace("\n\tbttttn = types.KeyboardButton('bttttn')",
                                        f"")
            f.close()

        with open(userbot + '.py', 'w', encoding="utf-8") as f:
            f.write(new_data)
            f.close()

        with open(userbot + '.py', 'r', encoding="utf-8") as g:
            oldest_data = g.read()
            newest_data = oldest_data.replace(", bttttn1", f"")
            g.close()

        with open(userbot + '.py', 'w', encoding="utf-8") as g:
            g.write(newest_data)
            g.close()

        cursor = conn.cursor()
        cursor.execute("SELECT bot_id FROM Bots WHERE Bots.bot_name=?", (userbot,))
        botid = cursor.fetchone()
        cursor.execute("SELECT COUNT(button_name) FROM Buttons WHERE bot_id=?", (botid[0],))

        result = cursor.fetchone()[0]
        print(result)
        if result == 0:
            with open(userbot + '.py', 'r', encoding="utf-8") as f:
                old_data = f.read()
                new_data = old_data.replace(f"\n\tbot.send_message(message.chat.id,'Для вывода всех кнопок используйте /buttons')",
                                            "")
                f.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as f:
                f.write(new_data)
                f.close()

        my_file = open(userbot + '.py', 'a', encoding="utf-8")
        text_for_file = "\nbot.infinity_polling()"
        my_file.write(text_for_file)
        my_file.close()

        send_welcome(message)

    elif call.data == 'Магазин':
        message = bot.send_message(call.message.chat.id, 'Вы выбрали шаблон "Магазин товаров и услуг" для своего бота.')
        bot.delete_message(call.message.chat.id, call.message.id)
        userShopDB(call)
        tshop_filltype(message)


    elif call.data == 'ШМТекстом':
        message = bot.send_message(call.message.chat.id, 'Вы выбрали заполнением шаблона при помощи текстовых сообщений.')
        bot.delete_message(call.message.chat.id, call.message.id)
        start_shop(message)

    elif call.data == 'ШМExcel':
        message = bot.send_message(call.message.chat.id, 'Вы выбрали заполнением шаблона при помощи файла Excel.')
        bot.delete_message(call.message.chat.id, call.message.id)
        tshop_choice(message)

    elif call.data == 'Тестирование':
        message = bot.send_message(call.message.chat.id, 'Вы выбрали шаблон "Тестирование" для своего бота')
        bot.delete_message(call.message.chat.id, call.message.id)
        Tcreate(message)

    elif call.data == 'ДобавитьТовар':
        message = bot.send_message(call.message.chat.id, 'Вы хотите пополнить корзину.')
        bot.delete_message(call.message.chat.id, call.message.id)
        tsBuy(message)
    elif call.data == 'Корзина':
        message = bot.send_message(call.message.chat.id, 'Вы перешли в корзину.')
        bot.delete_message(call.message.chat.id, call.message.id)
        USID=call.from_user.id
        tsCart1(message, USID)
    elif call.data == 'Купить':
        cursor = conn.cursor()
        cursor.execute(f"SELECT SUM(tsList_price*tsCart_num) as Цена FROM tsList, tsCart WHERE tsList_id=tsCart_Lid ")
        finPrice = cursor.fetchall()
        ab = []
        ab = finPrice[0]
        #print(ab[0])
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT tsCart_verification FROM tsCart WHERE tsCart_Uid='{call.from_user.id}'")
            uuuid = cursor.fetchall()
            print('результат запроса на верификацию '+uuuid)
            global guid_str
            guid_str = uuuid[0]
            if not guid_str:
                guid = uuid.uuid4()
                guid_str = str(guid)
                print('значение верификации1 ' + str(guid))
            pass
        except:
            guid = uuid.uuid4()
            guid_str = str(guid)
            print('значение верификации2 ' + str(guid))
            pass
        asssf=call.from_user.id
        print(asssf)
        cursor.execute(f"UPDATE tsCart SET tsCart_verification = '{guid_str}' WHERE tsCart_Uid = '{str(asssf)}'")
        conn.commit()
        bot.send_message(call.message.chat.id, f'Используя данные реквизиты: 0000-1111-2222-3333, оплатите {ab[0]} рублей с комментарием {guid_str}')
        #bot.delete_message(call.message.chat.id, call.message.id)
    elif call.data == 'ПочиститьКорзину':
        message = bot.send_message(call.message.chat.id,
                         f'Корзина очищена и вы возвращены в каталог.')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tsCart WHERE tsCart_Uid = ?", (call.from_user.id,))
        conn.commit()
        bot.delete_message(call.message.chat.id, call.message.id)
        tsBuy(message)

@bot.message_handler(commands=['addbuttons'])
def bot_chose(message):
    global nameUser
    nameUser = message.from_user.first_name
    cursor = conn.cursor()
    cursor.execute(f"SELECT users_id FROM Users WHERE user_name='{nameUser}';")
    global users_ID
    dbCallResult = cursor.fetchone()
    userIDCheck = int(dbCallResult[0])
    cursor = conn.cursor()
    cursor.execute(f"SELECT bot_name FROM Bots WHERE Bots.users_id='{userIDCheck}';")
    name = cursor.fetchall()
    print(name)
    my_list = ["\nСписок ботов, которых вы создали:\n"]
    for x in name:
        my_list.append(' | '.join(x))
    my_str = '\n'.join(my_list)
    msg = bot.send_message(message.chat.id, 'Прежде чем начать работу, '
                                      'необходимо выбрать - с каким чат-ботом будет проводиться работа.'
                                      '\nНапишите имя бота из предложенного списка, чтобы продолжить с ним работу, '
                                            'или используйте /return, чтобы вернуться на стартовый экран.'+my_str)
    bot.register_next_step_handler(msg, bot_check)

def bot_check(message):
    global userbot
    userbot = message.text
    cursor = conn.cursor()
    cursor.execute("SELECT bot_name FROM Bots WHERE Bots.bot_name=?", (userbot,))
    global  nameofthebot
    nameofthebot = cursor.fetchone()
    cursor = conn.cursor()
    cursor.execute("SELECT bot_name FROM Bots WHERE Bots.bot_name=?", (userbot,))
    ubot = cursor.fetchone()
    if ubot:
        cursor.execute("SELECT bot_id FROM Bots WHERE Bots.bot_name=?", (userbot,))
        botid = cursor.fetchone()
        cursor.execute("SELECT COUNT(button_name) FROM Buttons WHERE bot_id=?", (botid[0],))

        result = cursor.fetchone()[0]
        print(result)
        if result == 0:
            with open(userbot + '.py', 'r', encoding="utf-8") as f:
                old_data = f.read()
                new_data = old_data.replace("\ndef start_message(message):",
                                            f"\ndef start_message(message):\n\tbot.send_message(message.chat.id,'Для вывода всех кнопок используйте /buttons')")
                f.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as f:
                f.write(new_data)
                f.close()

            my_file = open(userbot + '.py', 'a', encoding="utf-8")
            text_for_file = "\n@bot.message_handler(commands=['buttons'])\ndef show_buttons(message):\n\t" \
                            "markup = types.ReplyKeyboardMarkup()" \
                            "\n\tbttttn = types.KeyboardButton('bttttn')" \
                            "\n\tmarkup.row(bttttn1)" \
                            "\n\tbot.send_message(message.chat.id, 'Выберите команду:', reply_markup=markup)"
            my_file.write(text_for_file)
            my_file.close()
        else:
            with open(userbot + '.py', 'r', encoding="utf-8") as f:
                old_data = f.read()
                new_data = old_data.replace("\n\tmarkup = types.ReplyKeyboardMarkup()",
                                            f"\n\tmarkup = types.ReplyKeyboardMarkup()\n\tbttttn = types.KeyboardButton('bttttn')")
                f.close()
            with open(userbot + '.py', 'w', encoding="utf-8") as f:
                f.write(new_data)
                f.close()
            with open(userbot + '.py', 'r', encoding="utf-8") as f:
                old_data = f.read()
                new_data = old_data.replace("\n\tmarkup.row(",
                                            f"\n\tmarkup.row(bttttn1,")
                f.close()
            with open(userbot + '.py', 'w', encoding="utf-8") as f:
                f.write(new_data)
                f.close()



        with open(userbot + '.py', 'r', encoding="utf-8") as f:
            old_data = f.read()
            new_data = old_data.replace('\nbot.infinity_polling()', '')
            f.close()
        with open(userbot + '.py', 'w', encoding="utf-8") as f:
            f.write(new_data)
            f.close()
        message = bot.send_message(message.chat.id, f'Вы выбрали редактирование бота {userbot}.')

        up_start(message)
    elif ubot is None:
        if userbot == '/return':
            message = bot.send_message(message.chat.id, 'Вы вернулись на стартовый экран.')
            send_welcome(message)
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка, такого бота нет! Выберите другого '
                                                    'или воспользуйтесь /return, чтобы вернуться на стартовый экран.')
            bot.register_next_step_handler(msg, bot_check)

def up_start(message):
    key = types.InlineKeyboardMarkup(row_width=1)
    but_1 = types.InlineKeyboardButton(text="Создать кнопку с текстом",
                                       callback_data="Создать кнопку с текстом")
    but_2 = types.InlineKeyboardButton(text="Создать кнопку с фотографией",
                                       callback_data="Создать кнопку с фотографией")
    but_3 = types.InlineKeyboardButton(text="Создать кнопку с видео",
                                       callback_data="Создать кнопку с видео")
    but_4 = types.InlineKeyboardButton(text="Создать уникальную кнопку",
                                       callback_data="Создать уникальную кнопку")
    but_end = types.InlineKeyboardButton(text="Завершить редактирование бота",
                                         callback_data="Завершить редактирование бота")
    key.add(but_1,but_2,but_3, but_4, but_end)
    bot.send_message(message.chat.id, "Выберите следующее действие", reply_markup=key)

def btn_cont(message):
    msg = bot.send_message(message.chat.id, 'Введите содержание для кнопки')
    global btn_name
    btn_name = message.text
    #print('Имя кнопки-', btn_name)
    bot.register_next_step_handler(msg, btn_end)

def btn_end(message):
    key = types.InlineKeyboardMarkup(row_width=1)
    butn = types.InlineKeyboardButton(text="Добавить еще кнопку",
                                       callback_data="Текстовка")
    butn2 = types.InlineKeyboardButton(text="Добавить другую кнопку",
                                      callback_data="Добавить другую кнопку")
    key.add(butn,butn2)
    bot.send_message(message.chat.id, "Кнопка успешно создана! "
                                      "\nПожалуйста, выберите следующее действие", reply_markup=key)
    global btn_content
    btn_content = message.text
    usN = message.from_user.id
    cursor = conn.cursor()
    cursor.execute(f"SELECT users_id FROM Users WHERE user_id='{usN}';")
    usID = cursor.fetchone()
    usIDc = int(usID[0])
    cursor = conn.cursor()
    cursor.execute(f"SELECT bot_id FROM Bots WHERE users_id='{usIDc}' AND bot_name='{userbot}';")
    res = cursor.fetchone()
    bot_ID = str(res[0])
    db_buttons_t(button_name=btn_name, button_txt=btn_content, botID=bot_ID)
    mes_id=message.message_id
    my_file = open(userbot + '.py', 'a', encoding="utf-8")
    text_for_file = "\n@bot.message_handler(commands=['"+btn_name+"'])\ndef start_message_"+str(mes_id)+"(message):" \
                    "\n\tbot.send_message(message.chat.id,'"+btn_content+"')\n"
    my_file.write(text_for_file)
    my_file.close()

    with open(userbot + '.py', 'r', encoding="utf-8") as f:
        old_data = f.read()
        new_data = old_data.replace("\n\tbttttn = types.KeyboardButton('bttttn')", f"\n\ta{btn_name} = types.KeyboardButton('/{btn_name}')\n\tbttttn = types.KeyboardButton('bttttn')")
        f.close()

    with open(userbot + '.py', 'w', encoding="utf-8") as f:
        f.write(new_data)
        f.close()

    with open(userbot + '.py', 'r', encoding="utf-8") as g:
        oldest_data = g.read()
        newest_data = oldest_data.replace("bttttn1", f"a{btn_name}, bttttn1")
        g.close()

    with open(userbot + '.py', 'w', encoding="utf-8") as g:
        g.write(newest_data)
        g.close()

def btn_photo(message):
    msg = bot.send_message(message.chat.id, 'Отправьте боту фотографию, обязательно нажмите на '
                                            '"Сжать изображение", которую Вы хотите прикрепить к кнопке.')
    global btn_photo_name
    btn_photo_name = message.text
    #print('Имя кнопки с фото-', btn_photo_name)
    bot.register_next_step_handler(msg, get_photo)

def btn_photo_end(message):
    key = types.InlineKeyboardMarkup(row_width=1)

    butn = types.InlineKeyboardButton(text="Добавить еще кнопку",
                                      callback_data="Фотография")
    butn2 = types.InlineKeyboardButton(text="Добавить другую кнопку",
                                       callback_data="Добавить другую кнопку")
    key.add(butn, butn2)
    bot.send_message(message.chat.id, "Кнопка успешно создана! "
                                      "\nПожалуйста, выберите следующее действие", reply_markup=key)

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    if message.content_type == 'photo':
        photo = message.photo
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        path = file_info.file_path
        downloaded_file = bot.download_file(file_info.file_path)
        src = '' + file_info.file_path
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        if photo:
            usName = message.from_user.id
            cursor = conn.cursor()
            cursor.execute(f"SELECT users_id FROM Users WHERE user_id='{usName}';")
            ownID = cursor.fetchone()
            ownIDc = int(ownID[0])
            cursor = conn.cursor()
            cursor.execute(f"SELECT bot_id FROM Bots WHERE users_id='{ownIDc}';")
            res = cursor.fetchone()
            bots_ID = str(res[0])
            db_buttons_f(buttn_name=btn_photo_name, file_path=path, botsID=bots_ID)
            fileID = str(fileID)
            fileID = fileID.replace('-', '')
            my_file = open(userbot+'.py', 'a', encoding="utf-8")
            text_for_file = "\n@bot.message_handler(commands=['"+btn_photo_name+"'])\ndef start_photo_"+fileID+"(message):"\
            +"\n\tphoto = open('"+path+"', 'rb')"+"\n\tbot.send_photo(message.chat.id, photo, timeout=60)\n"
            my_file.write(text_for_file)
            my_file.close()

            with open(userbot + '.py', 'r', encoding="utf-8") as f:
                old_data = f.read()
                new_data = old_data.replace("\n\tbttttn = types.KeyboardButton('bttttn')",
                                            f"\n\ta{btn_photo_name} = types.KeyboardButton('/{btn_photo_name}')\n\tbttttn = types.KeyboardButton('bttttn')")
                f.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as f:
                f.write(new_data)
                f.close()

            with open(userbot + '.py', 'r', encoding="utf-8") as g:
                oldest_data = g.read()
                newest_data = oldest_data.replace("bttttn1", f"a{btn_photo_name}, bttttn1")
                g.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as g:
                g.write(newest_data)
                g.close()

            message = bot.send_message(message.chat.id, "Фотография сохранена !")
            btn_photo_end(message)

def btn_video(message):
    msg = bot.send_message(message.chat.id, 'Отправьте боту видео, которое Вы хотите прикрепить к кнопке.')
    global btn_video_name
    btn_video_name = message.text
    #print('Имя кнопки с видео-', btn_video_name)
    bot.register_next_step_handler(msg, get_video)

def btn_video_end(message):
    key = types.InlineKeyboardMarkup(row_width=1)
    butn = types.InlineKeyboardButton(text="Добавить еще кнопку",
                                      callback_data="Видеозапись")
    butn2 = types.InlineKeyboardButton(text="Добавить другую кнопку",
                                       callback_data="Добавить другую кнопку")
    key.add(butn, butn2)
    bot.send_message(message.chat.id, "Кнопка успешно создана! "
                                      "\nПожалуйста, выберите следующее действие", reply_markup=key)

@bot.message_handler(content_types=['video'])
def get_video(message):
    if message.content_type == 'video':
        video = message.video
        id_save=message.video.file_id
        file_info = bot.get_file(message.video.file_id)
        src = '' + file_info.file_path
        with open(src, "wb") as f:
            file_content = bot.download_file(file_info.file_path)
            f.write(file_content)
        if video:
            usName = message.from_user.id
            cursor = conn.cursor()
            cursor.execute(f"SELECT users_id FROM Users WHERE user_id='{usName}';")
            ownID = cursor.fetchone()
            ownIDc = int(ownID[0])
            cursor = conn.cursor()
            cursor.execute(f"SELECT bot_id FROM Bots WHERE users_id='{ownIDc}';")
            res = cursor.fetchone()
            bots_ID = str(res[0])
            db_buttons_f(buttn_name=btn_video_name, file_path=file_info.file_path, botsID=bots_ID)
            message = bot.send_message(message.chat.id, "Видео сохранено !")
            btn_video_end(message)
            id_save = str(id_save)
            id_save = id_save.replace('-', '')
            my_file = open(userbot+'.py', 'a', encoding="utf-8")
            text_for_file = "\n@bot.message_handler(commands=['" + btn_video_name + "'])\ndef start_video_"+id_save+"(message):" \
                            + "\n\tvideo = open('" + file_info.file_path + "', 'rb')" \
                            + "\n\tbot.send_video(message.chat.id, video, timeout=60)\n"
            my_file.write(text_for_file)
            my_file.close()

            with open(userbot + '.py', 'r', encoding="utf-8") as f:
                old_data = f.read()
                new_data = old_data.replace("\n\tbttttn = types.KeyboardButton('bttttn')",
                                            f"\n\ta{btn_video_name} = types.KeyboardButton('/{btn_video_name}')\n\tbttttn = types.KeyboardButton('bttttn')")
                f.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as f:
                f.write(new_data)
                f.close()

            with open(userbot + '.py', 'r', encoding="utf-8") as g:
                oldest_data = g.read()
                newest_data = oldest_data.replace("bttttn1", f"a{btn_video_name}, bttttn1")
                g.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as g:
                g.write(newest_data)
                g.close()

def btn_integ_cont(message):
    msg = bot.send_message(message.chat.id, 'Отправьте боту файл, обязательно с подписью, '
                                            'который Вы хотите прикрепить к кнопке.')
    global integration_name
    integration_name = message.text
    global usIntgName
    usIntgName = message.from_user.id
    bot.register_next_step_handler(msg, btn_integ_mid)

def btn_integ_end(message):
    key = types.InlineKeyboardMarkup(row_width=1)
    butn = types.InlineKeyboardButton(text="Добавить такую же кнопку",
                                      callback_data="Уникальная")
    butn2 = types.InlineKeyboardButton(text="Добавить другую кнопку",
                                       callback_data="Добавить другую кнопку")
    key.add(butn, butn2)
    bot.send_message(message.chat.id, "Уникальная кнопка успешно создана! "
                                      "\nПожалуйста, выберите следующее действие", reply_markup=key)

#Кнопка с файлами
@bot.message_handler(content_types=['document', 'video', 'photo'])
def btn_integ_mid(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        src = '' + file_info.file_path

        with open(src, "wb") as f:
            file_content = bot.download_file(file_info.file_path)
            f.write(file_content)

        file_info = bot.get_file(message.document.file_id)
        doc_id=message.document.file_id
        src = '' + message.document.file_name
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = message.json['document']['file_name']
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        desc = message.caption
        message = bot.send_message(message.chat.id, "Файл с подписью успешно сохранен!")
        cursor = conn.cursor()
        cursor.execute(f"SELECT users_id FROM Users WHERE user_id='{usIntgName}';")
        ownID = cursor.fetchone()
        ownIDc = int(ownID[0])
        cursor = conn.cursor()
        cursor.execute(f"SELECT bot_id FROM Bots WHERE users_id='{ownIDc}';")
        res = cursor.fetchone()
        bots_ID = str(res[0])
        db_buttons_tf(butn_name=integration_name, files_path=file_info.file_path, butn_txt=desc, boteID=bots_ID)
        doc_id = str(doc_id)
        doc_id = doc_id.replace('-', '')
        btn_integ_end(message)
        my_file = open(userbot + '.py', 'a', encoding="utf-8")
        text_for_file = "\n@bot.message_handler(commands=['" + integration_name + "'])\ndef start_integdoc_"+doc_id+"(message):"\
                        + "\n\tdocument = open('" + file_info.file_path + "', 'rb')" \
                        + "\n\tbot.send_document(message.chat.id, document"+f", caption='{desc}', timeout=60)"
        my_file.write(text_for_file)
        my_file.close()

        with open(userbot + '.py', 'r', encoding="utf-8") as f:
            old_data = f.read()
            new_data = old_data.replace("\n\tbttttn = types.KeyboardButton('bttttn')",
                                        f"\n\ta{integration_name} = types.KeyboardButton('/{integration_name}')\n\tbttttn = types.KeyboardButton('bttttn')")
            f.close()

        with open(userbot + '.py', 'w', encoding="utf-8") as f:
            f.write(new_data)
            f.close()

        with open(userbot + '.py', 'r', encoding="utf-8") as g:
            oldest_data = g.read()
            newest_data = oldest_data.replace("bttttn1", f"a{integration_name}, bttttn1")
            g.close()

        with open(userbot + '.py', 'w', encoding="utf-8") as g:
            g.write(newest_data)
            g.close()

    if message.video:
        video = message.video
        file_info = bot.get_file(message.video.file_id)
        src = '' + file_info.file_path
        id2_save = message.video.file_id
        descr = message.caption
        with open(src, "wb") as f:
            file_content = bot.download_file(file_info.file_path)
            f.write(file_content)
        if video:
            message = bot.send_message(message.chat.id, "Видео с подписью успешно сохранено!")
            cursor = conn.cursor()
            cursor.execute(f"SELECT users_id FROM Users WHERE user_id='{usIntgName}';")
            ownID = cursor.fetchone()
            ownIDc = int(ownID[0])
            cursor = conn.cursor()
            cursor.execute(f"SELECT bot_id FROM Bots WHERE users_id='{ownIDc}';")
            res = cursor.fetchone()
            bots_ID = str(res[0])
            db_buttons_tf(butn_name=integration_name, files_path=file_info.file_path, butn_txt=descr,
                          boteID=bots_ID)
            btn_integ_end(message)
            id2_save = str(id2_save)
            id2_save = id2_save.replace('-', '')
            my_file = open(userbot+'.py', 'a', encoding="utf-8")
            text_for_file = "\n@bot.message_handler(commands=['" + integration_name + "'])\ndef start_integvid_"+id2_save+"(message):" \
                                         + "\n\t\n\tvideo = open('" + file_info.file_path + "', 'rb')" \
                                     + "\n\tbot.send_video(message.chat.id, video"+f", caption='{descr}', timeout=60)\n"
            my_file.write(text_for_file)
            my_file.close()

            with open(userbot + '.py', 'r', encoding="utf-8") as f:
                old_data = f.read()
                new_data = old_data.replace("\n\tbttttn = types.KeyboardButton('bttttn')",
                                            f"\n\ta{integration_name} = types.KeyboardButton('/{integration_name}')\n\tbttttn = types.KeyboardButton('bttttn')")
                f.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as f:
                f.write(new_data)
                f.close()

            with open(userbot + '.py', 'r', encoding="utf-8") as g:
                oldest_data = g.read()
                newest_data = oldest_data.replace("bttttn1", f"a{integration_name}, bttttn1")
                g.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as g:
                g.write(newest_data)
                g.close()

    if message.photo:
        photo = message.photo
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        path = file_info.file_path
        downloaded_file = bot.download_file(file_info.file_path)
        src = '' + file_info.file_path
        descript = message.caption
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        if photo:
            message = bot.send_message(message.chat.id, "Фотография с подписью успешно сохранена!")
            cursor = conn.cursor()
            cursor.execute(f"SELECT users_id FROM Users WHERE user_id='{usIntgName}';")
            ownID = cursor.fetchone()
            ownIDc = int(ownID[0])
            cursor = conn.cursor()
            cursor.execute(f"SELECT bot_id FROM Bots WHERE users_id='{ownIDc}';")
            res = cursor.fetchone()
            bots_ID = str(res[0])
            db_buttons_tf(butn_name=integration_name, files_path=file_info.file_path, butn_txt=descript,
                          boteID=bots_ID)
            btn_integ_end(message)
            fileID = str(fileID)
            fileID = fileID.replace('-', '')
            my_file = open(userbot + '.py', 'a', encoding="utf-8")
            text_for_file = "\n@bot.message_handler(commands=['" + integration_name + "'])\ndef start_integphoto_"+fileID+"(message):" \
                            + "\n\tphoto = open('" + path + "', 'rb')" + "" \
                                                                         "\n\tbot.send_photo(message.chat.id, photo" + f", caption='{descript}', timeout=60)\n"
            my_file.write(text_for_file)
            my_file.close()

            with open(userbot + '.py', 'r', encoding="utf-8") as f:
                old_data = f.read()
                new_data = old_data.replace("\n\tbttttn = types.KeyboardButton('bttttn')",
                                            f"\n\ta{integration_name} = types.KeyboardButton('/{integration_name}')\n\tbttttn = types.KeyboardButton('bttttn')")
                f.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as f:
                f.write(new_data)
                f.close()

            with open(userbot + '.py', 'r', encoding="utf-8") as g:
                oldest_data = g.read()
                newest_data = oldest_data.replace("bttttn1", f"a{integration_name}, bttttn1")
                g.close()

            with open(userbot + '.py', 'w', encoding="utf-8") as g:
                g.write(newest_data)
                g.close()

@bot.message_handler(commands=['about'])
def about(message):
   bot.send_message(message.chat.id, "Данный конструктор Telegram-ботов позволяет любому пользователю создавать своих чат-ботов для Telegram."
                                     "Созданные боты пишутся на языке программирования Python с поддержкой СУБД SQLiteStudio."
                                     "Для лучшей работы конструктора некоторые данные пользователя (имя пользователя, идентификатор) сохраняются в базе данных, "
                                     "чтобы улучшить работу бота.")
   bot.send_message(message.chat.id,
                    "Перед началом работы с конструктором, прежде всего, необходимо обладать токеном (уникальным идентафикатором бота, получаемый ТОЛЬКО у @BotFather).")
   bot.send_message(message.chat.id,
                    "Конструктор поддерживает следующий список команд: "
                    "\n /createbot - создает бота в конструкторе с дальнейшей возможностью его изменять (требуется токен бота);"
                    "\n /addbuttons - выводит список Ваших ботов в конструкторе с возможностью изменить их (внимательно следуйте инструкциям);"
                    "\n /deletebot - выводит список Ваших ботов в конструкторе, которых можно из него удалить;"
                    "\n /templates - позволяет выбрать настраевамый шаблон для Ваших ботов в конструкторе (поддерживается шаблон магазина и тестирования);"
                    "\n /about - описание работы конструктора конструктора, сейчас Вы находитесь тут!")
   key = types.InlineKeyboardMarkup(row_width=1)
   butonr = types.InlineKeyboardButton(text="Вернуться на стартовый экран",
                                       callback_data="Вернуться на главный экран")
   key.add(butonr)
   bot.send_message(message.chat.id, f"Чтобы вернуть на главный экран, пожалуйста, воспользуйтесь кнопкой ниже.", reply_markup=key)

@bot.message_handler(commands=['templates'])
def bot_chose_temp(message):
    global nameUser
    nameUser = message.from_user.first_name
    cursor = conn.cursor()
    cursor.execute(f"SELECT users_id FROM Users WHERE user_name='{nameUser}';")
    global users_ID
    dbCallResult = cursor.fetchone()
    userIDCheck = int(dbCallResult[0])
    cursor = conn.cursor()
    cursor.execute(f"SELECT bot_name FROM Bots WHERE Bots.users_id='{userIDCheck}';")
    name = cursor.fetchall()
    my_list = []
    for x in name:
        my_list.append(' | '.join(x))
    my_str = '\n\n'.join(my_list)

    msg = bot.send_message(message.chat.id, 'Прежде чем выбрать шаблон, '
                                      'необходимо выбрать - с каким чат-ботом будет проводиться работа.'
                                      f'\nНапишите имя бота, с которым продолжить работу или используйте /return, '
                                            f'чтобы вернуться назад.', reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, 'Ниже представлен список ваших ботов:\n\n'+my_str)
    bot.register_next_step_handler(msg, bot_check_temp)


def bot_check_temp(message):
    global userbot
    userbot = message.text
    cursor = conn.cursor()
    cursor.execute("SELECT bot_name FROM Bots WHERE Bots.bot_name=?", (userbot,))
    global  nameofthebot
    nameofthebot = cursor.fetchone()
    cursor = conn.cursor()
    cursor.execute("SELECT bot_name FROM Bots WHERE Bots.bot_name=?", (userbot,))
    ubot = cursor.fetchone()
    cursor = conn.cursor()
    cursor.execute("SELECT bot_id FROM Bots WHERE Bots.bot_name=?", (userbot,))
    tokenofbot = cursor.fetchone()
    if ubot:
        my_file = open(userbot + '.py', 'w', encoding="utf-8")
        text_for_file = "import telebot\nfrom telebot import types\n" \
                        'token=' + '"' + str(tokenofbot[0]) + '"\nbot=telebot.TeleBot(token)\n' \
                                                     "\n@bot.message_handler(commands=['start'])\ndef start_message(message):" \
                                                     "\n\tbot.send_message(message.chat.id,'Привет, я " + userbot + ". Для помощи с шаблоном воспольщуйтесь /help.')\n"
        my_file.write(text_for_file)
        my_file.close()
        message = bot.send_message(message.chat.id, f'Вы выбрали бота {userbot}.')
        template(message)
    elif ubot is None:
        if userbot == '/return':
            message = bot.send_message(message.chat.id, 'Вы вернулись на стартовый экран.')
            send_welcome(message)
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка, такого бота нет! Выберите другого '
                                                    'или воспользуйтесь /return, чтобы вернуться на стартовый экран.')
            bot.register_next_step_handler(msg, bot_check_temp)

def template(message):
    key = types.InlineKeyboardMarkup(row_width=1)
    butons = types.InlineKeyboardButton(text="Шаблон: Магазин товаров и услуг",
                                        callback_data="Магазин")
    butond = types.InlineKeyboardButton(text='Шаблон: Тестирование',
                                        callback_data='Тестирование')
    key.add(butons, butond)
    bot.send_message(message.chat.id, f"Вы перешли к выбору шаблона для бота.", reply_markup=key)

def tshop_filltype(message):
    key = types.InlineKeyboardMarkup(row_width=1)
    but_1 = types.InlineKeyboardButton(text="Заполнить текстовыми сообщениями.",
                                       callback_data="ШМТекстом")
    but_2 = types.InlineKeyboardButton(text="Заполнить при помощи Excel файла.",
                                       callback_data="ШМExcel")

    key.add(but_1, but_2)
    bot.send_message(message.chat.id, "Перед добавлением шаблона магазина вашему боту, нужно заполнить каталог товаров. "
                                      "Выберите один из вариантов.", reply_markup=key)

def tshop_choice(message):
    msg = bot.send_message(message.chat.id,
                           'Отправьте боту файл формата Excel (.xlsx), для примера используйте Example.xlsx.')
    with open("Example.xlsx", "rb") as f:
        bot.send_document(message.chat.id, f)
        f.close()
    bot.register_next_step_handler(msg, tshop_consume)

@bot.message_handler(content_types=['document'])
def tshop_consume(message):
    file_name = message.document.file_name
    file_name = file_name.split('.')
    if file_name[1] == 'xlsx':
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open(userbot+'file.xlsx', 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, 'Файл Excel был успешно загружен.')
        tshop_xlimport(message)
    else:
        bot.reply_to(message, 'Пожалуйста, загрузите файл формата Excel (.xlsx)')
        tshop_choice(message)

def tshop_xlimport(message):
    df = pd.read_excel(userbot+'file.xlsx')
    connection = sqlite3.connect(userbot+'shopDB.db', check_same_thread=False)
    cursorr = connection.cursor()
    for index, row in df.iterrows():
        cursorr.execute('INSERT INTO tsList (tsList_name, tsList_price, tsList_limit) VALUES (?,?,?)',
                       (row['Товар'], row['Цена'], row['Количество']))
    bot.send_message(message.chat.id, 'Данные из Excel были успешно ипортированы.')
    connection.commit()
    connection.close()
    my_file = open(userbot + '.py', 'a', encoding="utf-8")
    text_for_file = f"\nconn = sqlite3.connect('{userbot}shopDB.db', check_same_thread=False)" \
                    "\ncursor = conn.cursor()" \
                    "\ncursorObj = conn.cursor()\n"
    my_file.write(text_for_file)
    my_file.close()
    output_file = open(userbot + ".py", "a", encoding="utf-8")
    with open("ShopCode.txt", "r", encoding="utf-8") as scan:
        output_file.write(scan.read())
    output_file.close()
    with open(userbot + '.py', 'r', encoding="utf-8") as f:
        old_data = f.read()
        new_data = old_data.replace('import telebot', 'import telebot\nimport sqlite3\nimport uuid')
        f.close()
    with open(userbot + '.py', 'w', encoding="utf-8") as f:
        f.write(new_data)
        f.close()
    with open(userbot + ".py", "r", encoding='utf-8') as f:
        bot.send_document(message.chat.id, f)
        f.close()
    with open(userbot + "shopDB.db", "rb") as f:
        bot.send_document(message.chat.id, f)
        f.close()
    send_welcome(message)
    bot.send_message(message.chat.id,
                     'Товары и услуги более не добавляются. Каталог товаров для шаблона магазина успешно создан')

#счетчик
count_urls = [0]
def userShopDB(call):
    call.from_user.id
    global connect
    connect = sqlite3.connect(userbot+'shopDB.db', check_same_thread=False)
    global cur
    cur = connect.cursor()

    cursorObject = connect.cursor()

    cursorObject.execute("""CREATE TABLE IF NOT EXISTS tsCart (
                           tsCart_Uid VARCHAR (50) NOT NULL,
                           tsCart_Lid INTEGER REFERENCES tsList (tsList_id) ON DELETE CASCADE ON UPDATE CASCADE NOT NULL,
                           tsCart_num INTEGER NOT NULL,
                           tsCart_bought BOOLEAN DEFAULT (0) NOT NULL,
                           tsCart_date DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP),
                           tsCart_verification VARCHAR,
                           tsCart_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE);""")
    connect.commit()

    cursorObject.execute("""CREATE TABLE IF NOT EXISTS tsList (
                               tsList_id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,
                               tsList_name TEXT NOT NULL,
                               tsList_price VARCHAR (50) NOT NULL,
                               tsList_limit INTEGER NOT NULL DEFAULT (1) );""")
    connect.commit()



def start_shop(message):
    global text_user
    text_user = message.text
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = types.KeyboardButton('Добавить')
    button2 = types.KeyboardButton('Не добавлять')
    keyboard.add(button1, button2)
    if count_urls[0] == 0:
        with open(userbot + '.py', 'r', encoding="utf-8") as f:
            old_data = f.read()
            new_data = old_data.replace('import telebot', 'import telebot\nimport sqlite3\nimport uuid')
            f.close()
        with open(userbot + '.py', 'w', encoding="utf-8") as f:
            f.write(new_data)
            f.close()


        msg = bot.send_message(message.chat.id, 'Хотите добавить товар в каталог ?', reply_markup=keyboard)
        bot.register_next_step_handler(msg, solution)
    elif count_urls[0] > 0:
        global listLimit
        listLimit = message.text
        db_tempShoplist(sList_name = listName, sList_price = listPrice, sList_Limit = listLimit)
        msg = bot.send_message(message.chat.id, 'Товар добавлен\n'
                                                'Вы хотите добавить еще один?', reply_markup=keyboard)
        bot.register_next_step_handler(msg, solution)


def solution(message):
    if message.text == 'Добавить':
        count_urls[0] += 1
        msg = bot.send_message(message.chat.id, 'Введите название товара.', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, solution2)
    elif message.text == 'Не добавлять':
        my_file = open(userbot + '.py', 'a', encoding="utf-8")
        text_for_file = f"\nconn = sqlite3.connect('{userbot}shopDB.db', check_same_thread=False)" \
                        "\ncursor = conn.cursor()" \
                        "\ncursorObj = conn.cursor()\n"
        my_file.write(text_for_file)
        my_file.close()
        output_file = open(userbot+".py", "a", encoding="utf-8")
        with open("ShopCode.txt", "r", encoding="utf-8") as scan:
            output_file.write(scan.read())
        output_file.close()
        with open(userbot+".py", "r", encoding='utf-8') as f:
            bot.send_document(message.chat.id, f)
            f.close()
        with open(userbot+"shopDB.db", "rb") as f:
            bot.send_document(message.chat.id, f)
            f.close()
        send_welcome(message)
        bot.send_message(message.chat.id, 'Товары и услуги более не добавляются. Каталог товаров для шаблона магазина успешно создан')


def solution2(message):
    msg = bot.send_message(message.chat.id, 'Введите цену товара, для обозначения дробей используйте символ "." ')
    global listName
    listName = message.text
    print('name ', listName)
    bot.register_next_step_handler(msg, solution3)

def solution3(message):
    msg = bot.send_message(message.chat.id, 'Введите количество товаров. Обязательно в виде целого числа.')
    global listPrice
    listPrice = message.text
    print('price ', listPrice)
    bot.register_next_step_handler(msg, start_shop)


#слева переменная для записи/справа переменная из функции
#db_users(userID=user_ID, userName=user_Name)
def db_tempShoplist(sList_name: str, sList_price: str, sList_Limit:int, ):
    cur.execute('INSERT INTO tsList (tsList_name, tsList_price, tsList_Limit) VALUES (?, ?, ?)', (sList_name, sList_price, sList_Limit, ))
    connect.commit()



@bot.message_handler(commands=['deletebot'])
def del_bot(message):
    nameUser = message.from_user.first_name
    cursor = conn.cursor()
    cursor.execute(f"SELECT users_id FROM Users WHERE user_name='{nameUser}';")
    dbCallResult = cursor.fetchone()
    global userIDdel
    userIDdel = int(dbCallResult[0])
    cursor = conn.cursor()
    cursor.execute(f"SELECT bot_name FROM Bots WHERE Bots.users_id='{userIDdel}';")
    name_bot = cursor.fetchall()
    my_list = ["Список ботов, которых Вы создали:\n"]
    for x in name_bot:
        my_list.append(' | '.join(x))
    my_str = '\n'.join(my_list)
    msg = bot.send_message(message.chat.id, 'Напишите имя бота, из предложенного списка, которого Вы хотите удалить или используйте /return, чтобы вернуться на стартовый экран.'
        '\n\nВНИМАНИЕ: бот будет удален из базы данных также, как и его хранимый файл в конструкторе!' + my_str)
    bot.register_next_step_handler(msg, bot_remove)

def bot_remove(message):
    check_remove = message.text
    cursor = conn.cursor()
    cursor.execute(f"SELECT bot_id FROM Bots WHERE Bots.users_id='{userIDdel}';")
    IDoftheBot = cursor.fetchone()
    #print(IDoftheBot[0])
    cursor = conn.cursor()
    cursor.execute(f"SELECT bot_name FROM Bots WHERE Bots.bot_name='{check_remove}';")
    name_bot = cursor.fetchone()
    if name_bot:
        cursor.execute("DELETE FROM Buttons WHERE Buttons.bot_id = ?", (IDoftheBot[0],))
        conn.commit()
        cursor.execute("DELETE FROM Bots WHERE Bots.bot_name = ?", (check_remove,))
        conn.commit()
        os.remove(check_remove + '.py')
        bot.send_message(message.chat.id, 'Бот ' + check_remove + ' был успешно удален !')
        send_welcome(message)
    elif name_bot is None:
        if check_remove == '/return':
            message = bot.send_message(message.chat.id, 'Вы вернулись на стартовый экран.')
            send_welcome(message)
        else:
            msg = bot.send_message(message.chat.id, 'Такого бота нет в списке, напишите имя бота из списка '
                                                    'или воспользуйтесь командой /return, чтобы вернуться на стартовый экран.')
            bot.register_next_step_handler(msg, bot_remove)

count_times = [0]
@bot.message_handler(commands=['buy'])
def tsBuy(message):
    bot.send_message(message.chat.id, 'Вот каталог товаров:\n')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT 'Товар: ' || tsList_name || '.', 'Цена: ' || tsList_price || ' рублей,', 'в количестве '||  tsList_limit || '.' FROM tsList")
    rows = cursor.fetchall()
    my_list = ["\n"]
    for x in rows:
        my_list.append(' '.join(map(str, (x))))
    my_str = '\n\n'.join(map(str, my_list))
    bot.send_message(message.chat.id, my_str)



    msg = bot.send_message(message.chat.id, 'Введите название товара из каталога, а также его количество через запятую.')
    bot.register_next_step_handler(msg, tsBuyL)

def tsBuyL(message):
    # id user'a
    global tscuID
    tscuID = message.from_user.id
    print(tscuID, ' id usera ?')
    global buyName
    buyName = message.text
    a=[]
    a=buyName.split(sep=',')
    #buyName.split(sep=' ')
    print(a[0],a[1])
    check=str(a[0])

    # проверка на наличие товара
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT tsList_name FROM tsList WHERE tsList_name='{check}'")
        cCheckn = cursor.fetchone()
        print(f'name of товара {cCheckn[0]}')
    except:
        bot.send_message(message.chat.id, 'Такого товара нет, попробуйте еще раз.')
        tsBuy(message)

        #проверка на количества
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT tsList_Limit FROM tsList WHERE tsList_name='{str(a[0])}'")
    cLim = cursor.fetchone()
    if round(int(a[1])) <= 0:
        bot.send_message(message.chat.id, 'Введенное Вами количество неверно.')
        tsBuy(message)

    # проверка на количество, если ввел больше, чем доступно = сколько есть
    if round(int(a[1])) > int(cLim[0]):
        a[1]=int(cLim[0])
    print(f'Количество товара {a[1]}')

    cursor = conn.cursor()
    cursor.execute(
        f"SELECT tsList_id FROM tsList WHERE tsList_name='{a[0]}'")
    cName = cursor.fetchone()
    print(f'id товара {cName[0]}')

    db_tempShopcart(tscartUID=tscuID, tscartIID=cName[0], tscartNum=int(a[1]))

    bot.send_message(message.chat.id, f'В корзину было добавлено {a[0]} в количестве ({int(a[1])}).')

    key = types.InlineKeyboardMarkup(row_width=1)
    butontsa = types.InlineKeyboardButton(text="Добавить еще товар",
                                        callback_data="ДобавитьТовар")
    butontsc = types.InlineKeyboardButton(text='Перейти в корзину',
                                        callback_data='Корзина')
    key.add(butontsa, butontsc)
    bot.send_message(message.chat.id, f"Хотите добавить в корзину еще товар?", reply_markup=key)

#слева переменная для записи/справа переменная из функции
#db_users(userID=user_ID, userName=user_Name)


def db_tempShopcart(tscartUID: str, tscartIID: str, tscartNum: int,):
    cursor.execute('INSERT INTO tsCart (tsCart_Uid, tsCart_Lid, tsCart_num) VALUES (?, ?, ?)', (tscartUID, tscartIID, tscartNum, ))
    conn.commit()

@bot.message_handler(commands=['mycart'])
def tsCart(message):
    print(message.from_user.id)
    if message.text:
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT tsCart_Uid FROM tsCart WHERE tsCart_Uid='{message.from_user.id}'")
            usId = cursor.fetchall()
            print(f'id usera {usId[0]}')
        except:
            bot.send_message(message.chat.id, 'Ваш идентификатор не найден, поробуйте еще раз.')
            tsBuy(message)

    bot.send_message(message.chat.id, 'Ваша корзина товаров:\n')
    global usID
    usId=message.from_user.id
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT 'Название товара: ' || tsList_name || ',' , 'его количесвто: ' || tsCart_num || '.' , 'Цена: ' || (tsList_price*tsCart_num) || ' рублей.' as Цена FROM tsList, tsCart WHERE tsList_id=tsCart_Lid AND tsCart_Uid = {message.from_user.id}")
    rows = cursor.fetchall()
    print(rows)
    my_list = ["\n"]
    for x in rows:
        my_list.append(' '.join(map(str, (x))))
    my_str = '\n\n'.join(map(str, my_list))
    key = types.InlineKeyboardMarkup(row_width=1)
    butontsa1 = types.InlineKeyboardButton(text="Добавить еще товар",
                                          callback_data="ДобавитьТовар")
    butontsb1 = types.InlineKeyboardButton(text='Купить',
                                          callback_data='Купить')
    butontscl = types.InlineKeyboardButton(text='Очистить корзину',
                                          callback_data='ПочиститьКорзину')
    key.add(butontsa1, butontsb1, butontscl)
    bot.send_message(message.chat.id, my_str, reply_markup=key)


def tsCart1(message, USID):
    print(message.from_user.id)
    if message.text:
        try:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT tsCart_Uid FROM tsCart WHERE tsCart_Uid='{message.from_user.id}'")
            usId = cursor.fetchall()
            print(f'id usera {usId[0]}')
        except:
            bot.send_message(message.chat.id, 'Ваш идентификатор не найден, поробуйте еще раз.')
            tsBuy(message)

    bot.send_message(message.chat.id, 'Ваша корзина товаров:\n')
    global usID
    usId=message.from_user.id
    cursor = conn.cursor()
    cursor.execute(
        f"SELECT 'Название товара: ' || tsList_name || ',' , 'его количесвто: ' || tsCart_num || '.' , 'Цена: ' || (tsList_price*tsCart_num) || ' рублей.' as Цена FROM tsList, tsCart WHERE tsList_id=tsCart_Lid AND tsCart_Uid = {message.from_user.id}")
    rows = cursor.fetchall()
    print(rows)
    my_list = ["\n"]
    for x in rows:
        my_list.append(' '.join(map(str, (x))))
    my_str = '\n\n'.join(map(str, my_list))
    key = types.InlineKeyboardMarkup(row_width=1)
    butontsa1 = types.InlineKeyboardButton(text="Добавить еще товар",
                                          callback_data="ДобавитьТовар")
    butontsb1 = types.InlineKeyboardButton(text='Купить',
                                          callback_data='Купить')
    butontscl = types.InlineKeyboardButton(text='Очистить корзину',
                                          callback_data='ПочиститьКорзину')
    key.add(butontsa1, butontsb1, butontscl)
    bot.send_message(message.chat.id, my_str, reply_markup=key)


#answers = {}
global numQ
numQ = 0
@bot.message_handler(commands=["testtemp"])
def Tcreate(message):
    print(f'Номер вопроса в тесте {numQ}')
    if numQ == 0:
        my_file = open(userbot + '.py', 'a', encoding="utf-8")
        text_for_file = "\n@bot.message_handler(commands=['help'])" \
                        "\ndef start_message(message):" \
	                    "\n\tbot.send_message(message.chat.id,'Используйте следующие команды для взаимодействия со своим шаблоном: " \
                        "/test для прохождения сформированного в конструкторе теста.') " \
                        "\nglobal score" \
                        "\nscore = 0" \
                        "\n@bot.message_handler(commands=['test'])"
        my_file.write(text_for_file)
        my_file.close()
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        button1 = types.KeyboardButton('Создать вопрос')
        button2 = types.KeyboardButton('Не создавать')
        keyboard.add(button1, button2)
        msg = bot.send_message(message.chat.id, 'Для создания теста нужен хотя бы один вопрос. Вы хотите его создать?', reply_markup=keyboard)
        bot.register_next_step_handler(msg, TcreateQstn)
    elif numQ > 0:

        keyboards = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        buttons1 = types.KeyboardButton('Создать еще один вопрос')
        buttons2 = types.KeyboardButton('Закончить созадние теста')
        keyboards.add(buttons1, buttons2)
        bot.send_message(message.chat.id, 'Вы хотите создать еще один вопрос для своего теста ?', reply_markup=keyboards)
        bot.register_next_step_handler(message, TcreateQstn)



def TcreateQstn(message):
    global numQ
    if message.text == 'Создать вопрос':
        numQ += 1
        print(f"Вопрос №{numQ}")
        msg = bot.send_message(message.chat.id, 'Введите содержание вопроса.', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, TcreateAnsw)
    elif message.text == 'Создать еще один вопрос':
        numQ += 1
        print(f"Вопрос №{numQ}")
        my_file = open(userbot + '.py', 'a', encoding="utf-8")
        text_for_file = f"\n\tbot.send_message(message.chat.id, 'Следующий вопрос.')" \
                        f"\n\tquestion{numQ}(message)"
        my_file.write(text_for_file)
        my_file.close()
        msg = bot.send_message(message.chat.id, 'Введите содержание вопроса.', reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, TcreateAnsw)
    elif message.text == 'Не создавать':
        bot.send_message(message.chat.id, 'Новый вопрос более не создается.', reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'Закончить созадние теста':
        bot.send_message(message.chat.id, 'Шаблон теста успешно закончен.', reply_markup=types.ReplyKeyboardRemove())

        my_file = open(userbot + '.py', 'a', encoding="utf-8")
        text_for_file = f"\n\tbot.send_message(message.chat.id, 'Тестирование закончено.')" \
                        f"\n\ttest_result(message)" \
                        f"\ndef test_result(message):" \
                        f"\n\tpercentage = (score / totalQuestions) * 100" \
                        "\n\tbot.send_message(message.chat.id, f'Ваш результат: {score} из {totalQuestions}\\nПроцент правильных ответов: {int(percentage)}%')" \
                        "\nbot.infinity_polling()"
        my_file.write(text_for_file)
        my_file.close()
        with open(userbot+".py", "r", encoding='utf-8') as f:
            bot.send_document(message.chat.id, f)
            f.close()
        send_welcome(message)
    else:
        bot.send_message(message.chat.id, 'Выбран неправильный вариант ответа!')

def TcreateAnsw(message):
    msg = bot.send_message(message.chat.id,'Сколько ответов будет у создаваемого вопроса? Обязательно вводите целое число!')
    global tQstn
    tQstn = message.text
    print("Текст вопроса:",tQstn)
    bot.register_next_step_handler(msg, TcreateAnswloop)

def TcreateAnswloop(message):
    global tQAnsw
    tQAnsw = message.text
    print('Количество ответов', tQAnsw)
    temporaryCount = []
    message = bot.send_message(message.chat.id, f'Вводите поочередно содержание ответов, всего их будет {tQAnsw}')
    bot.register_next_step_handler(message, TAnswloop, temporaryCount)


def TAnswloop(message, temporaryCount):
    answers = {}
    if len(temporaryCount)<int(tQAnsw):
        temporaryCount.append(message.text)
        bot.send_message(message.chat.id, f'Вариант ответа "{message.text}" для вопроса №{numQ}  "{tQstn}" успешно запомнен.')
        bot.register_next_step_handler(message, TAnswloop, temporaryCount)
        if len(temporaryCount)==int(tQAnsw):
            for num in range(1, int(tQAnsw) + 1):
                answers[num] = temporaryCount[num - 1]
                #print(answers[num])
            print(f"Ответы у вопроса №{numQ}:", answers)
            result = [f'Ответ #{key} - {value}' for key, value in answers.items()]
            print(result)
            user_question = [f'\nСписок созданных ответов у вопроса №{numQ} - "{tQstn}":\n']
            for x in result:
                user_question.append(''.join(x))
            user_answers = '\n'.join(user_question)
            bot.send_message(message.chat.id, 'Ответы были успешно сформированы.'+user_answers)
            bot.send_message(message.chat.id, 'Какие из них будут являться правильными? Напишите номера этих ответов, для раздлеления используйте пробел.')
            bot.register_next_step_handler(message, TRAnsw, answers)

def TRAnsw(message, answers):
    rightans = {}
    global TRA
    TRA = str(message.text)
    rightans[numQ] = TRA.split(sep=' ')
    result = [f"Вопрос №{question_num}, правильные ответы - {', '.join(answers)};" for question_num, answers in rightans.items()]
    user_question = [f"\nСписок правильных ответов в тесте, на данный момент:\n"]
    for x in result:
        user_question.append(''.join(x))
    user_ranswers = '\n'.join(user_question)
    bot.send_message(message.chat.id, 'Правильные ответы были внесены.' + user_ranswers)
    print(f'Правильный вариант ответа {rightans}')
    my_file = open(userbot + '.py', 'a', encoding="utf-8")
    text_for_file = f"\ndef question{numQ}(message):" \
                    f"\n\tanswers = {answers}" \
                    f"\n\tglobal totalQuestions" \
                    f"\n\ttotalQuestions = {numQ}" \
                    f"\n\tnumQ = {numQ}\n\t" \
                    "result = [f'{key}) {value}' for key, value in answers.items()]" \
                    f"\n\tuser_question = [f'\\n{tQstn}\\n']" \
                    "\n\tfor x in result:" \
                    "\n\t\tuser_question.append(''.join(x))" \
                    "\n\tuser_answers = '\\n'.join(user_question)" \
                    "\n\tbot.send_message(message.chat.id, f'Вопрос №{numQ}:'+user_answers)" \
                    "\n\tbot.send_message(message.chat.id, 'Выберите один или несколько вариантов ответа.')" \
                    f"\n\tbot.register_next_step_handler(message, question{numQ}_useranswer, numQ)" \
                    f"\ndef question{numQ}_useranswer(message, numQ):" \
                    f"\n\tglobal score" \
                    f"\n\trightans = {rightans}" \
                    f"\n\tuAnswer = message.text" \
                    f"\n\tif uAnswer.split() == rightans[numQ]:" \
                    f"\n\t\tscore += 1" \
                    f"\n\telse:" \
                    f"\n\t\tscore += 0"
    my_file.write(text_for_file)
    my_file.close()
    Tcreate(message)


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(1)
            print('Произошла ошибочка!',e)