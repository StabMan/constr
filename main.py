import telebot
import config
from telebot import types  # библиотека для кнопок
import time  # для оптимизации бота
import sqlite3
import os #работа с файлами
import uuid



bot = telebot.TeleBot(config.token)

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
    bot.send_message(message.chat.id, "Здравствуйте, "
                     + message.from_user.first_name
                     + ". Это конструктор телеграмм-ботов. Выберите одну из предложенных команд для начала работы."
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
        # cursor = conn.cursor()
        # cursor.execute("SELECT bottkn FROM users WHERE users.botn=?", (userbot,))
        # tknbot = cursor.fetchone()
        # my_file = open(userbot + '.py', 'w', encoding="utf-8")
        # text_for_file = "import telebot\nfrom telebot import types\n" \
        #                 'token=' + '"' + str(tknbot[0]) + '"\nbot=telebot.TeleBot(token)\n' \
        #                                                   "\n@bot.message_handler(commands=['start'])\ndef start_message(message):\n\tbot.send_message(message.chat.id,'Привет, я " + userbot + "')\n"
        # my_file.write(text_for_file)
        # my_file.close()

    elif call.data == 'Не сохранять информацию о боте':
        bot.send_message(call.message.chat.id, "Бот не создан. Данные о боте не будут занесены в базу данных!"
                                                "\nДля начала работы конструктора воспользуйтесь командой  /start")
        bot.delete_message(call.message.chat.id, call.message.id)

    elif call.data == 'Создать кнопку с текстом':
        msg = bot.send_message(call.message.chat.id,
                               'Вы выбрали создание кнопки с текстом.' + '\nВведите нзавание для кнопки')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_cont)
    elif call.data == 'Создать кнопку с фотографией':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание кнопки с фото.\nВведите название кнопки.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_photo)
    elif call.data == 'Создать кнопку с видео':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание кнопки с видео.\nВведите название кнопки.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_video)
    elif call.data == 'Создать кнопку с интеграцией':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание кнопки с интеграцией.'
                                                     '\nВведите название кнопки.')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_integ_cont)

    elif call.data == 'Текстовка':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание дополнительной кнопки с текстом. ' 
                                                     '\nВведите название для кнопки')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_cont)
    elif call.data == 'Добавить другой функционал':
        message = bot.send_message(call.message.chat.id, 'Вы были перенесены к пункту создания фукнционала у бота.')
        bot.delete_message(call.message.chat.id, call.message.id)
        up_start(message)
    elif call.data == 'Интеграция':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание дополнительной кнопки с интеграцией. '
                                                     '\nВведите название для кнопки')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_integ_cont)
    elif call.data == 'Фотография':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание дополнительной кнопки с фотографией. '
                                                     '\nВведите название для кнопки')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_photo)
    elif call.data == 'Видеозапись':
        msg = bot.send_message(call.message.chat.id, 'Вы выбрали создание дополнительной кнопки с видео. '
                                                     '\nВведите название для кнопки')
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.register_next_step_handler(msg, btn_video)

    elif call.data == 'Вернуться на главный экран':
        message = bot.send_message(call.message.chat.id, 'Вас успешно вернули на главный экран.')
        bot.delete_message(call.message.chat.id, call.message.id)
        send_welcome(message)

    elif call.data == 'Завершить редактирование бота':
        message=bot.send_message(call.message.chat.id, f'Вы завершили редактирование своего бота {str(nameofthebot[0])}.')
        bot.delete_message(call.message.chat.id, call.message.id)
        my_file = open(userbot+'.py', 'a', encoding="utf-8")
        text_for_file = "\nbot.infinity_polling()"
        my_file.write(text_for_file)
        my_file.close()
        with open(userbot+".py", "r", encoding='utf-8') as f:
            bot.send_document(message.chat.id, f)
            f.close()
        send_welcome(message)
    elif call.data == 'Магазин':
        message = bot.send_message(call.message.chat.id, 'Вы выбрали шаблон для бота "Магазин" ')
        bot.delete_message(call.message.chat.id, call.message.id)
        pass
    elif call.data == 'Тестирование':
        message = bot.send_message(call.message.chat.id, 'Coming soon!')
        bot.delete_message(call.message.chat.id, call.message.id)
        send_welcome(message)
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
    #print(name)
    #копирует при нажатии
    #bot.send_message(message.chat.id, 'Простой текст `copy text` ', parse_mode="MARKDOWN")
    my_list = ["\nСписок ботов, которых вы создали:\n"]
    for x in name:
        my_list.append(' | '.join(x))
    my_str = '\n'.join(my_list)
    #print(my_list)
    msg = bot.send_message(message.chat.id, 'Прежде чем начать работу, '
                                      'необходимо выбрать - с каким чат-ботом будет проводиться работа.'
                                      '\nНапишите имя бота, с которым продолжить работу.'+my_str)
    bot.register_next_step_handler(msg, bot_check)


def bot_check(message):
    global userbot
    userbot = message.text
    cursor = conn.cursor()
    cursor.execute("SELECT bot_name FROM Bots WHERE Bots.bot_name=?", (userbot,))
    global  nameofthebot
    nameofthebot = cursor.fetchone()
    #print('бот пользователя '+userbot)
    cursor = conn.cursor()
    cursor.execute("SELECT bot_name FROM Bots WHERE Bots.bot_name=?", (userbot,))
    ubot = cursor.fetchone()
    if ubot:
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
            message = bot.send_message(message.chat.id, 'Вы вернулись на главный экран.')
            send_welcome(message)
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка, такого бота нет! Выберите другого '
                                                    'или воспользутесь /return, чтобы вернуться на главный экран.')
            bot.register_next_step_handler(msg, bot_check)


def up_start(message):
    key = types.InlineKeyboardMarkup(row_width=1)
    but_1 = types.InlineKeyboardButton(text="Создать кнопку с текстом",
                                       callback_data="Создать кнопку с текстом")
    but_2 = types.InlineKeyboardButton(text="Создать кнопку с фотографией",
                                       callback_data="Создать кнопку с фотографией")
    but_3 = types.InlineKeyboardButton(text="Создать кнопку с видео",
                                       callback_data="Создать кнопку с видео")
    but_4 = types.InlineKeyboardButton(text="Создать кнопку с интеграцией файла",
                                       callback_data="Создать кнопку с интеграцией")
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
    butn2 = types.InlineKeyboardButton(text="Добавить другой функционал",
                                      callback_data="Добавить другой функционал")
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
    cursor.execute(f"SELECT bot_id FROM Bots WHERE users_id='{usIDc}';")
    res = cursor.fetchone()
    bot_ID = str(res[0])
    print(btn_name, btn_content, bot_ID)


    db_buttons_t(button_name=btn_name, button_txt=btn_content, botID=bot_ID)


    mes_id=message.message_id
    #print(message.message_id)


    my_file = open(userbot + '.py', 'a', encoding="utf-8")
    text_for_file = "\n@bot.message_handler(commands=['"+btn_name+"'])\ndef start_message_"+mes_id+"(message):" \
                    "\n\tbot.send_message(message.chat.id,'"+btn_content+"')\n"
    my_file.write(text_for_file)
    my_file.close()


def btn_photo(message):
    msg = bot.send_message(message.chat.id, 'Отправьте боту фотографию, обязательно нажмите на "Сжать изображение", которую Вы хотите прикрепить к кнопке.')
    global btn_photo_name
    btn_photo_name = message.text
    #print('Имя кнопки с фото-', btn_photo_name)
    bot.register_next_step_handler(msg, get_photo)


def btn_photo_end(message):
    key = types.InlineKeyboardMarkup(row_width=1)

    butn = types.InlineKeyboardButton(text="Добавить еще кнопку",
                                      callback_data="Фотография")
    butn2 = types.InlineKeyboardButton(text="Добавить другой функционал",
                                       callback_data="Добавить другой функционал")
    key.add(butn, butn2)
    bot.send_message(message.chat.id, "Кнопка успешно создана! "
                                      "\nПожалуйста, выберите следующее действие", reply_markup=key)

@bot.message_handler(content_types=['photo'])
def get_photo(message):
    if message.content_type == 'photo':
        #document_id = message.photo.file_id
        #print(document_id)
        photo = message.photo
        fileID = message.photo[-1].file_id
        #print(f'id foto {fileID}')
        file_info = bot.get_file(fileID)
        path = file_info.file_path
        #print('Путь файла =', file_info.file_path)
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

            print(btn_photo_name, path, bots_ID)

            db_buttons_f(buttn_name=btn_photo_name, file_path=path, botsID=bots_ID)

            my_file = open(userbot+'.py', 'a', encoding="utf-8")
            text_for_file = "\n@bot.message_handler(commands=['"+btn_photo_name+"'])\ndef start_photo_"+fileID+"(message):"\
            +"\n\tphoto = open('"+path+"', 'rb')"+"\n\tbot.send_photo(chat_id, photo)\n"
            my_file.write(text_for_file)
            my_file.close()
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
    butn2 = types.InlineKeyboardButton(text="Добавить другой функционал",
                                       callback_data="Добавить другой функционал")
    key.add(butn, butn2)
    bot.send_message(message.chat.id, "Кнопка успешно создана! "
                                      "\nПожалуйста, выберите следующее действие", reply_markup=key)


@bot.message_handler(content_types=['video'])
def get_video(message):
    if message.content_type == 'video':
        video = message.video
        #file_name = message.json['video']['file_name']
        #fileID = message.video[-1].file_id
        id_save=message.video.file_id
        print(f'id vidosa {message.video.file_id}')
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

            #print(btn_video_name, file_info.file_path, bots_ID)

            db_buttons_f(buttn_name=btn_video_name, file_path=file_info.file_path, botsID=bots_ID)
            message = bot.send_message(message.chat.id, "Видео сохранено !")
            btn_video_end(message)
            my_file = open(userbot+'.py', 'a', encoding="utf-8")
            text_for_file = "\n@bot.message_handler(commands=['" + btn_video_name + "'])\ndef start_video_"+id_save+"(message):" \
                            + "\n\tvideo = open('" + file_info.file_path + "', 'rb')" \
                            + "\n\tbot.send_video(message.chat.id, video)\n"
            my_file.write(text_for_file)
            my_file.close()

def btn_integ_cont(message):
    msg = bot.send_message(message.chat.id, 'Отправьте боту файл, обязательно с подписью, который Вы хотите прикрепить к кнопке.')
    global integration_name
    integration_name = message.text
    print(integration_name)
    global usIntgName
    usIntgName = message.from_user.id
    bot.register_next_step_handler(msg, btn_integ_mid)

def btn_integ_end(message):
    key = types.InlineKeyboardMarkup(row_width=1)
    butn = types.InlineKeyboardButton(text="Добавить такую же кнопку",
                                      callback_data="Интеграция")
    butn2 = types.InlineKeyboardButton(text="Выбрать другой функционал",
                                       callback_data="Добавить другой функционал")
    key.add(butn, butn2)
    bot.send_message(message.chat.id, "Кнопка успешно создана! "
                                      "\nПожалуйста, выберите следующее действие", reply_markup=key)


#Кнопка с файлами
@bot.message_handler(content_types=['document', 'video', 'photo'])
def btn_integ_mid(message):
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        doc_id=message.document.file_id
        #print(message.document.file_id)
        src = '' + message.document.file_name
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = message.json['document']['file_name']
        #print(file_name)
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        #print(message.caption)
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
        print('Yippie')
        print(integration_name, file_info.file_path, desc, bots_ID)

        db_buttons_tf(butn_name=integration_name, files_path=file_info.file_path, butn_txt=desc, boteID=bots_ID)

        btn_integ_end(message)
        my_file = open(userbot + '.py', 'a', encoding="utf-8")
        text_for_file = "\n@bot.message_handler(commands=['" + integration_name + "'])\ndef start_integdoc_"+doc_id+"(message):" \
                        + "\n\tbot.send_photo(message.chat.id," + file_info.file_path + f", caption='{desc}')"
        my_file.write(text_for_file)
        my_file.close()
    # if message.video:
    #     file_info = bot.get_file(message.video.file_id)
    #     src = '' + file_info.file_path
    #     file_name = message.json['video']['file_name']
    #     with open(src, "wb") as f:
    #         file_content = bot.download_file(file_info.file_path)
    #         f.write(file_content)
    #     message = bot.send_message(message.chat.id, "Видео с подписью успешно сохранено!")
    #     btn_video_end(message)
    #     my_file = open(userbot + '.py', 'a', encoding="utf-8")
    #     text_for_file = "\n@bot.message_handler(commands=['" + integration_name + "'])\ndef start_video(message):" \
    #                         + "\n\t\n\tvideo = open('" + file_info.file_path + "', 'rb')" \
    #                         + "\n\tbot.send_video(message.chat.id, video,"+f", caption='{message.caption}')\n"
    #     my_file.write(text_for_file)
    #     my_file.close()
    if message.video:
        video = message.video
        #file_name = message.json['video']['file_name']
        file_info = bot.get_file(message.video.file_id)
        src = '' + file_info.file_path
        id2_save = message.video.file_id
        #print(f'id vidosa {message.video.file_id}')
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

            # print(btn_video_name, file_info.file_path, bots_ID)

            db_buttons_tf(butn_name=integration_name, files_path=file_info.file_path, butn_txt=descr,
                          boteID=bots_ID)

            btn_integ_end(message)
            my_file = open(userbot+'.py', 'a', encoding="utf-8")
            text_for_file = "\n@bot.message_handler(commands=['" + integration_name + "'])\ndef start_integvid_"+id2_save+"(message):" \
                                         + "\n\t\n\tvideo = open('" + file_info.file_path + "', 'rb')" \
                                     + "\n\tbot.send_video(message.chat.id, video,"+f", caption='{descr}')\n"
            my_file.write(text_for_file)
            my_file.close()
    if message.photo:
        photo = message.photo
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        path = file_info.file_path
        print('Путь файла =', file_info.file_path)
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

            # print(btn_video_name, file_info.file_path, bots_ID)

            db_buttons_tf(butn_name=integration_name, files_path=file_info.file_path, butn_txt=descript,
                          boteID=bots_ID)

            btn_integ_end(message)
            my_file = open(userbot + '.py', 'a', encoding="utf-8")
            text_for_file = "\n@bot.message_handler(commands=['" + integration_name + "'])\ndef start_integphoto_"+fileID+"(message):" \
                            + "\n\tphoto = open('" + path + "', 'rb')" + "" \
                                                                         "\n\tbot.send_photo(chat_id, photo," + f", caption='{descript}')\n"
            my_file.write(text_for_file)
            my_file.close()

        # photo = message.photo
        # fileID = message.photo[-1].file_id
        # file_info = bot.get_file(fileID)
        # path = file_info.file_path
        # print('Путь файла =', file_info.file_path)
        # downloaded_file = bot.download_file(file_info.file_path)
        # src = '' + file_info.file_path
        # file_name = message.json['photo']['file_name']
        # with open(src, 'wb') as new_file:
        #     new_file.write(downloaded_file)
        # if photo:
        #     message = bot.send_message(message.chat.id, "Фотография с подписью успешно сохранена!")
        #     btn_integ_end(message)
        #     my_file = open(userbot + '.py', 'a', encoding="utf-8")
        #     text_for_file = "\n@bot.message_handler(commands=['" + integration_name + "'])\ndef start_integphoto(message):" \
        #                         + "\n\tphoto = open('" + path + "', 'rb')" + "" \
        #                         "\n\tbot.send_photo(chat_id, photo,"+f", caption='{message.caption}')\n"
        #     my_file.write(text_for_file)
        #     my_file.close()




@bot.message_handler(commands=['about'])
def about(message):
   bot.send_message(message.chat.id, "Данный конструктор телгерамм-ботов позволяет любому пользователю создавать своих чат-ботов для телгерамма."
                                     "Созданные боты пишутся на языке программирования Python с поддержкой SQL."
                                     "Для лучшей работы конструктора некоторые данные пользователя (имя пользователя, идентификатор) сохраняются, "
                                     "чтобы привязывать созданные пользователем ботов к нему.")
   bot.send_message(message.chat.id,
                    "Для начала работы, прежде всего, необходимо обладать токеном (уникальным идентафикатором бота, получаемый ТОЛЬКО у @BotFather), затем выбрать одну из команд конструктора.")
   bot.send_message(message.chat.id,
                    "Конструктор на данный момент поддерживает следующий список команд: "
                    "\n /createbot - создает бота в конструкторе с дальнейшей возможностью его изменять;"
                    "\n /addbuttons - выводит список Ваших ботов в конструкторе с возможностью изменить их;"
                    "\n /deletebot - выводит список Ваших ботов в конструкторе, которых можно из него удалить;"
                    "\n /templates - позволяет выбрать настраевамый шаблон для Ваших ботов в конструкторе;"
                    "\n /about - описание работы конструктора конструктора, сейчас Вы находитесь тут!")
   key = types.InlineKeyboardMarkup(row_width=1)
   butonr = types.InlineKeyboardButton(text="Вернуться на главный экран",
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
    #print(name)
    #копирует при нажатии
    #bot.send_message(message.chat.id, 'Простой текст `copy text` ', parse_mode="MARKDOWN")
    my_list = ["\nСписок ботов, которых вы создали:\n"]
    for x in name:
        my_list.append(' | '.join(x))
    my_str = '\n'.join(my_list)
    #print(my_list)
    msg = bot.send_message(message.chat.id, 'Прежде чем выбрать шаблон, '
                                      'необходимо выбрать - с каким чат-ботом будет проводиться работа.'
                                      '\nНапишите имя бота, с которым продолжить работу.'+my_str)
    bot.register_next_step_handler(msg, bot_check_temp)


def bot_check_temp(message):
    global userbot
    userbot = message.text
    cursor = conn.cursor()
    cursor.execute("SELECT bot_name FROM Bots WHERE Bots.bot_name=?", (userbot,))
    global  nameofthebot
    nameofthebot = cursor.fetchone()
    #print('бот пользователя '+userbot)
    cursor = conn.cursor()
    cursor.execute("SELECT bot_name FROM Bots WHERE Bots.bot_name=?", (userbot,))
    ubot = cursor.fetchone()
    if ubot:
        with open(userbot + '.py', 'r', encoding="utf-8") as f:
            old_data = f.read()
            new_data = old_data.replace('\nbot.infinity_polling()', '')
            f.close()
        with open(userbot + '.py', 'w', encoding="utf-8") as f:
            f.write(new_data)
            f.close()
        message = bot.send_message(message.chat.id, f'Вы выбрали бота {userbot}.')

        template(message)
    elif ubot is None:
        if userbot == '/return':
            message = bot.send_message(message.chat.id, 'Вы вернулись на главный экран.')
            send_welcome(message)
        else:
            msg = bot.send_message(message.chat.id, 'Ошибка, такого бота нет! Выберите другого '
                                                    'или воспользутесь /return, чтобы вернуться на главный экран.')
            bot.register_next_step_handler(msg, bot_check_temp)

def template(message):
    key = types.InlineKeyboardMarkup(row_width=1)
    butons = types.InlineKeyboardButton(text="Шаблон: Магазин товаров и услуг",
                                        callback_data="Магазин")
    butond = types.InlineKeyboardButton(text='Шаблон: Тестирование',
                                        callback_data='Тестирование')
    key.add(butons, butond)
    bot.send_message(message.chat.id, f"Вы перешли к выбору шаблона для бота.", reply_markup=key)

all_messages = {}
#счетчик
count_urls = [0]
@bot.message_handler(commands=["test"])
def start(message):
    global text_user
    text_user = message.text
    #print("введено "+text_user)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    button1 = types.KeyboardButton('Да')
    button2 = types.KeyboardButton('Нет')
    keyboard.add(button1, button2)
    if count_urls[0] == 0:
        msg = bot.send_message(message.chat.id, 'Хотите добавить товар в каталог ?', reply_markup=keyboard)
        bot.register_next_step_handler(msg, solution)
    elif count_urls[0] > 0:
        all_messages[len(all_messages) + 1] = (message.text).split(sep=' ')
        global listLimit
        listLimit = message.text
        print('limit ', listLimit)
        db_tempShoplist(sList_name = listName, sList_price = listPrice, sList_Limit = listLimit)
        msg = bot.send_message(message.chat.id, 'Товар добавлен\n'
                                                'Вы хотите добавить еще один?', reply_markup=keyboard)
        bot.register_next_step_handler(msg, solution)
    else:
        msg = bot.send_message(message.chat.id, 'Добавить товар ?', reply_markup=keyboard)
        bot.register_next_step_handler(msg, solution)

def solution(message):
    if message.text == 'Да':
        count_urls[0] += 1
        msg = bot.send_message(message.chat.id, 'Введите название товара.')
        #print(message.text)
        bot.register_next_step_handler(msg, solution2)
    else:
        bot.send_message(message.chat.id, 'Товар более не добавляется.')


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
    bot.register_next_step_handler(msg, start)


#слева переменная для записи/справа переменная из функции
#db_users(userID=user_ID, userName=user_Name)
def db_tempShoplist(sList_name: str, sList_price: str, sList_Limit:int, ):
    cursor.execute('INSERT INTO tsList (tsList_name, tsList_price, tsList_Limit) VALUES (?, ?, ?)', (sList_name, sList_price, sList_Limit, ))
    conn.commit()

def db_tempShopcart(bottoken: str, botname: str, usersID: int,):
    cursor.execute('INSERT INTO Bots (bot_id, bot_name, users_id) VALUES (?, ?, ?)', (bottoken, botname, usersID, ))
    conn.commit()

# @bot.message_handler(commands=["catalogue"])
# def cart(message):
#     bot.send_message(message.chat.id, 'Вот список товаров:\n')
#     cursor = conn.cursor()
#     cursor.execute("SELECT 'Товар: ' || tsList_name || '.', 'Цена: ' || tsList_price || ' рублей,', 'в количестве '||  tsList_limit || '.' FROM tsList")
#     rows = cursor.fetchall()
#     my_list = ["\nТовары и цена:"]
#     for x in rows:
#         my_list.append(' '.join(map (str, (x))))
#     my_str = '\n'.join(map(str, my_list))
#     bot.send_message(message.chat.id, my_str)

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
    msg = bot.send_message(message.chat.id, 'Напишите имя бота, из предложенного списка, которого Вы хотите удалить.'
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
            message = bot.send_message(message.chat.id, 'Вы вернулись на главный экран.')
            send_welcome(message)
        else:
            msg = bot.send_message(message.chat.id, 'Такого бота нет в списке, выберите другого '
                                                    'или воспользутесь командой /return, чтобы вернуться на главный экран.')
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

bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            time.sleep(1)
            print('Ошибочка!',e)

