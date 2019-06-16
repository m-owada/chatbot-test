# coding: UTF-8
import sys
import os
from contextlib import contextmanager
from psycopg2 import pool, extras
from chatbot import Chatbot

"""

Chatbot学習ツール
python3 learning.py [フォルダパス]

"""

# 接続プール
_conn_pool = pool.SimpleConnectionPool(minconn=1, maxconn=10, dsn=os.environ.get("DATABASE_URL"))

# BOT-ID
_bot_id = 1

# 学習
def learning(path):
    bot = read(_bot_id)
    chatbot = Chatbot(bot["bot_name"], bot["dictionary"])
    for dirpath, dirnames, filenames in os.walk(path):
        for file in filenames:
            print(file)
            if file.endswith(".txt"):
                with open(os.path.join(dirpath, file)) as f:
                    for line in f.readlines():
                        response = chatbot.response(line.strip())
    update(_bot_id, chatbot.name, chatbot.json)
    print("正常に終了しました。")
    return

# DB読込
def read(bot_id):
    with get_cursor() as cur:
        bot = get_bot(cur, bot_id)
    return bot

# DB書込
def update(bot_id, name, json):
    with get_cursor() as cur:
        upd_bot(cur, bot_id, name, json)
    return

@contextmanager
def get_cursor():
    conn = _conn_pool.getconn()
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=extras.DictCursor)
    try:
        yield cur
    finally:
        cur.close()
        _conn_pool.putconn(conn)

# BOT情報取得
def get_bot(cur, bot_id):
    cur.execute("select bot_name, dictionary from t_bot where bot_id = %s", (bot_id,))
    return cur.fetchone()

# BOT情報更新
def upd_bot(cur, bot_id, bot_name, dictionary):
    cur.execute("update t_bot set bot_name = %s, dictionary = %s, date = now() where bot_id = %s", (bot_name, dictionary, bot_id,))
    return

if __name__ == "__main__":
    if len(sys.argv) == 2:
        learning(sys.argv[1])
    else:
        print("引数の数が一致していません。")
