# coding: UTF-8
from bottle import route, run, template, request, redirect, static_file
from contextlib import contextmanager
from psycopg2 import pool, extras
import os
from chatbot import Chatbot

# 接続プール
_conn_pool = pool.SimpleConnectionPool(minconn=1, maxconn=10, dsn=os.environ.get("DATABASE_URL"))

# BOT-ID
_bot_id = 1

@route("/")
def index():
    with get_cursor() as cur:
        bot = get_bot(cur, _bot_id)
        list = get_log_list(cur, _bot_id)
    return template("index", bot=bot["bot_name"], list=list)

@route("/submit", method="POST")
def add():
    with get_cursor() as cur:
        bot = get_bot(cur, _bot_id)
        chatbot = Chatbot(bot["bot_name"], bot["dictionary"])
        response = chatbot.response(request.forms.getunicode("txt_message"))
        upd_bot(cur, _bot_id, chatbot.name, chatbot.json)
        add_log(cur, _bot_id, request.forms.getunicode("txt_name"), request.forms.getunicode("txt_message"), response)
    return redirect("/")

@route("/<filename:path>")
def static(filename):
    return static_file(filename, root="./static")

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

# LOG一覧取得
def get_log_list(cur, bot_id):
    cur.execute("select name, message, response, to_char(date, 'yyyy/mm/dd hh24:mi') date from t_log where bot_id = %s order by log_no desc limit 20", (bot_id,))
    return cur.fetchall()

# LOG情報追加
def add_log(cur, bot_id, name, message, response):
    cur.execute("insert into t_log (bot_id, name, message, response) values (%s, %s, %s, %s)", (bot_id, name, message, response,))
    return

if __name__ == "__main__":
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
