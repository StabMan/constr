import sqlite3
token = "5392461531:AAGdArPbmztFJv_YbbWU3cDiw5WXrs6EWwQ"  # Your token
chat_id = "-1001572933390"

conn = sqlite3.connect('ledo.db', check_same_thread=False)
#conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def idget(message):
    global userid;
    userid = message.from_user.id
def bd():
    res = cursor.execute('SELECT * FROM login WHERE uid=?', (userid,))
    res = cursor.fetchone()
    return res

#data = "SELECT lname FROM leader"
#got = cursor.execute(data)
#got = cursor.fetchone()
#leader = got[0]