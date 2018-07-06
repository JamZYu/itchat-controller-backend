# -*- coding: UTF-8 -*-
import itchat
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from flask import Flask, make_response, redirect, url_for
import threading
import config

app = Flask(__name__)
learner = ChatBot("this")
working = True
qrSource = ''


def learn():
    learner.set_trainer(ChatterBotCorpusTrainer)


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    if working:
        print(msg)
        response = learner.get_response(msg.text)
        author = itchat.search_friends(nickName=config.ITCHAT_CONFIG['host_user_name'])[0]
        print(author)
        user_name = author['UserName']
        itchat.send_msg(str(response), msg.FromUserName)


def qr_callback(uuid, status, qrcode):
    if status == '0':
        global qrSource
        qrSource = qrcode
    elif status == '200':
        qrSource = 'Logged in!'
    elif status == '201':
        qrSource = 'Confirm'


def start_itchat():
    itchat.auto_login(hotReload=True, qrCallback=qr_callback)
    itchat.run()


@app.route("/start")
def start():
    global working
    learn_t = threading.Thread(target=learn)
    learn_t.daemon = True
    learn_t.start()
    start_itchat_t = threading.Thread(target=start_itchat)
    start_itchat_t.daemon = True
    start_itchat_t.start()
    working = True
    return redirect(url_for('code'))


@app.route("/resume")
def resume():
    global working
    working = True
    return "Resumed!"


@app.route("/pause")
def pause():
    global working
    working = False
    return "paused!"


@app.route("/")
def default():
    global working
    working = False
    return "Hello!"


@app.route("/code")
def code():
    global qrSource
    if len(qrSource) < 100:
        return qrSource
    else:
        response = make_response(qrSource)
        response.headers['Content-Type'] = 'image/jpeg'
        return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


