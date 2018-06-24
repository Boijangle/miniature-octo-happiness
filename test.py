import os
import giphypop
import random
import re
import subprocess
import requests
import traceback
import database
from database import *
import spotify
from spotify import post_rand_song
from libs import *
from help import help_text
from os.path import join, dirname
from dotenv import load_dotenv
from flask import Flask
from flask import request
app = Flask(__name__)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


gif = giphypop.Giphy()
admin_sender_id = os.environ.get("ADMIN_SENDER_ID")
access_token = os.environ.get("GROUPME_ACCESS_TOKEN")

@app.route('/callback/get', methods=['GET'])
def get_access_token():
    try:
        print(request.args.get('access_token',''))
        return 'OK'
    except:
        return 'Not OK'

@app.route('/callback/<bot_id>', methods=['POST'])
def parse_messages(bot_id):
    try:

        message = request.get_json()

        if message['sender_type'] != "user":
            return 'OK'

        """ Admin Actions """

        #Ventriloquism
        if message['text'].startswith("/dummy"):
            if message['sender_id'] == admin_sender_id:
                print("Start dummy")
                search = re.search(r"/dummy (\S*)\s?(.*)?$", message['text'])
                (nickname, msg) = search.groups('test post pls ignore')
                if(nickname == 'help'):
                    dummies = show_all_dummy()
                    msg = "All available dummies:\n"
                    for x in dummies:
                        msg += x[0] + "\n"
                    dummy_bot = bot_id
                else:
                    dummy_bot = find_dummy_bot(nickname)[0][0]
                    if not dummy_bot:
                        dummy_bot = bot_id
                        msg = "No group with nickname '" + nickname + "'"
                print("Dummy msg: "+ msg)
                print("Dummy bot: " + dummy_bot)
            else:
                dummy_bot = bot_id
                msg = "No u."
            post_text(msg, dummy_bot)

        #Test posting
        if message['text'].startswith("/test") and message['sender_id'] == admin_sender_id:
            message_info = get_group_info(message['group_id'])
            for x in message_info['members']
                print(x['user_id'])
            post_text("done", bot_id)

        # Silence bot
        if message['text'].startswith("/QUIET") and message['sender_id'] == admin_sender_id:
            post_text(":((", bot_id)
            silence_awaken_bot(bot_id, True)

        if message['text'].startswith("/AWAKEN") and message['sender_id'] == admin_sender_id:
            silence_awaken_bot(bot_id, False)
            post_text("thx bb :)", bot_id)


        """ Actions for all groups """

        # Say hello to anyone that says "Hi"
        if re.search(r"\bhi\b", message['text'].lower()):
            post_text("Hi " + message['name'].split(" ")[0] + "!", bot_id)

        # Help text
        if message['text'].lower().startswith("/help"):
            bot_name = request.args.get('name','')
            msg = "Hi " + message['name'].split(" ")[0] + ", I'm " + bot_name + "! \n" + help_text
            post_text_mention(msg, bot_id, message['sender_id'])

        # Post gif from Giphy
        if message['text'].lower().startswith("/gif"):
            search = re.search(r"/gif (.*?)( \d+)?$", message['text'])
            (gif_search, num) = search.groups('1')
            if int(num) < 20:
                num = min(int(num), 5)
                for i in range(int(num)):
                    post_text(gif.translate(gif_search).media_url, bot_id)
            else:
                post_text_mention("Can you not.", bot_id, message['sender_id'])

        # Clap a bunch
        if message['text'].lower().startswith("/clap"):
            msg = message['text'][5:]
            msg = msg.upper()
            clap = '\U0001F44F'
            if message['sender_id'] == admin_sender_id:
                clap += '\U0001F3FF'
            msg = clap.join(msg.split())
            post_text(msg, bot_id)

        # Hurr Durr
        if message['text'].lower().startswith("/durr"):
            msg_row = find_last_msg(message['group_id'])
            if msg_row:
                msg = msg_row[0] + " "
                sender = msg_row[1].lower()
                lastSenderId = msg_row[2]
                low = (x.lower() for x in msg[0::2])
                upp = (x.upper() for x in msg[1::2])
                msg = ''.join(a + b for a, b in zip(low, upp))
                sender = re.sub(r"\s", "_", sender)
                durr_url = "https://memegen.link/spongebob/hurr_durr_i'm_" + sender + "/and_i_just_want_to_say.jpg?watermark=none&height=600&width=600"
                if lastSenderId != admin_sender_id or message['sender_id'] == admin_sender_id:
                    post_text(durr_url, bot_id)
                    post_text_mention(msg, bot_id, lastSenderId)
                else:
                    post_text_mention("I'm sorry " + message['name'].split(" ")[0] + ", I'm afraid I can't do that.", bot_id, message['sender_id'])

        # Jokes
        if message['text'].lower().startswith("/joke"):
            headers = {'Accept': 'text/plain'}
            joke = requests.get("https://icanhazdadjoke.com", headers=headers)
            joke.raise_for_status()
            post_text(joke.content.decode("UTF-8"), bot_id)

        # Random song
        if message['text'].lower().startswith("/song"):
            post_rand_song(bot_id)

        # Dice
        if message['text'].lower().startswith("/dice"):
            num = int(message['text'][5:])
            rand = random.randint(1, num)
            post_text(u'\U0001F3B2: ' + str(rand), bot_id)


        """ Store Last Message """

        if message['sender_type'] == "user":
            store_last_msg(message['group_id'], message['id'], message['text'], message['name'], message['sender_id'])
            add_person(message['sender_id'], message['name'])
            add_group(message['group_id'], bot_id)


        return 'OK'
    except:
            post_text(u'\U0001F916\u2620: ' + traceback.format_exc(), bot_id)
            return 'Not OK'
