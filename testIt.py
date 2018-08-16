# -*- coding: UTF-8 -*-
import itchat
import requests
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from flask import Flask, make_response, redirect, url_for
import threading
import config
from time import sleep
from itchat.content import *

app = Flask(__name__)
learner = ChatBot("this")
working = True
autoAddFriend = False
auto_reply_dict = {}
qrSource = ''
key = config.ITCHAT_CONFIG['key']
url_turin = 'http://www.tuling123.com/openapi/api'
url_aego = 'http://10.200.55.106:3000/api/messages'
userNameList = []


def learn():
    learner.set_trainer(ChatterBotCorpusTrainer)


def get_chatterbot_text_response(msg):
    response = learner.get_response(msg.text)
    return response


def get_turin_text_response(msg, userid):
    global key
    global url_turin
    data = {
        'key': key,
        'info': msg,
        'userid': userid,
    }
    response = requests.post(url_turin, data=data).json()
    return response.get('text')


def get_aego_response(msg, userid):
    data={
        'message': msg,
        'userid': userid
    }
    response = requests.post(url_aego, data=data).json()
    return response.get('reply')


@itchat.msg_register(TEXT)
def text_reply(msg):
    global working
    global userNameList
    if working:
        if msg.FromUserName in auto_reply_dict.keys():
            if '。' in msg.text:
                itchat.send_msg(auto_reply_dict[msg.FromUserName], msg.FromUserName)
        print(msg.FromUserName)
        if msg.FromUserName in userNameList:
            # response = get_chatterbot_text_response(msg.text)
            if msg.text == 'end':
                userNameList.remove(msg.FromUserName)
                itchat.send_msg("Bot stopped!", msg.FromUserName)
            else:
                response = get_turin_text_response(msg.text, msg.FromUserName)
                author = itchat.search_friends(nickName=config.ITCHAT_CONFIG['host_user_name'])[0]
            print(author)
            user_name = author['UserName']
            itchat.send_msg(str(response), msg.FromUserName)
        elif msg.text == 'start':
            userNameList.append(msg.FromUserName)
            itchat.send_msg("Bot started for you!", msg.FromUserName)


@itchat.msg_register(FRIENDS)
def add(msg):
    if autoAddFriend:
        print("Auto Adding")
        itchat.add_friend(**msg['Text'])
        itchat.send_msg("Welcome to wechat bot")


def qr_callback(uuid, status, qrcode):
    global qrSource
    if status == '0':
        qrSource = qrcode
    elif status == '200':
        qrSource = 'Logged in!'
    elif status == '201':
        qrSource = 'Confirm'


def start_itchat():
    itchat.auto_login(qrCallback=qr_callback)
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
    global qrSource
    while True:
        sleep(0.5)
        if not len(qrSource) < 100:
            response = make_response(qrSource)
            response.headers['Content-Type'] = 'image/jpeg'
            return response


@app.route("/nickname/<nickname>")
def add_nickname_to_list(nickname):
    global userNameList
    author = itchat.search_friends(nickName=nickname)[0]
    user_name = author['UserName']
    userNameList.append(user_name)
    return nickname + "added"


@app.route("/username/<username>")
def add_username_to_list(username):
    global userNameList
    userNameList.append(username)
    return username + "added"


@app.route("/send/<nickname>/<message>/<time>")
def sendto(nickname, message, time):
    author = itchat.search_friends(nickName=nickname)[0]
    user_name = author['UserName']
    for i in range(int(time)):
        itchat.send_msg(str(message), user_name)
    return user_name + "added"


@app.route("/sendgp/<nickname>/<message>/<time>")
def send_to_group(nickname, message, time):
    author = itchat.search_chatrooms(nickname)[0]
    user_name = author['UserName']
    for i in range(int(time)):
        itchat.send_msg(str(message), user_name)
    return user_name + "added"


@app.route("/sendautoreply/<nickname>/<message>")
def send_auto_reply(nickname, message):
    author = itchat.search_friends(nickname)[0]
    user_name = author['UserName']
    auto_reply_dict[user_name] = message
    return user_name + " done for " + message


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


@app.route("/autoadd")
def auto_add():
    global autoAddFriend
    autoAddFriend = True
    return "Start auto adding!"


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


