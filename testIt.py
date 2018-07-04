# -*- coding: UTF-8 -*-
import itchat
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from flask import Flask
import config

app = Flask(__name__)
learner = ChatBot("this")
working = True


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


def start_itchat():
    global working
    learn()
    working = True
    itchat.auto_login(hotReload=True)
    itchat.run()


@app.route("/start")
def start():
    start_itchat()
    return "Started"


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


if __name__ == '__main__':
    app.run(port=int("80"), debug=True)


