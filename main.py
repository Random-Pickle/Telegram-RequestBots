import telebot
from flask import Flask,request
from telebot import util
import time
from telebot import types as tp
from pymongo import MongoClient
import os
import json
from ChannelData import runner
from DataOrg import JsonPacker



token = 'token'
ADMIN_CHAT = 'Admin Chat ID'
welcome = ''
about = ''
help_ = ''

url = 'WebHook Url'


bot = telebot.TeleBot(token)

client = MongoClient(os.getenv('MONGODB_URI'))
db = client.AnimeFlix_Database
collections = db.UserID

server = Flask(__name__)

#*--------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['start'])
def start_(message):

    try:
        bot.send_message(message.chat.id,welcome,parse_mode='markdown')
    except Exception:pass

    username = '@'+message.from_user.username.replace('_','\_') if message.from_user.username != None else ""

    info = f'*Name* - {message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name!=None else ""}\n*Username* - {username}\n*ID* - `{message.from_user.id}`'
    try:
        bot.send_message(ADMIN_CHAT,info,parse_mode='markdown')
    except Exception:pass

    db_info = {'_id':message.from_user.id,'name':f'{message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name!=None else ""}','username':message.from_user.username}

    try: collections.insert_one(db_info)
    except Exception as e: print(e)

#*--------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['about'])
def about_(message):

    main = tp.InlineKeyboardMarkup(row_width=2)
    slot1 = tp.InlineKeyboardButton('Slot 1',url='')
    slot2 = tp.InlineKeyboardButton('Slot 2',url='')
    slot3 = tp.InlineKeyboardButton('Slot 3',url='')
    main.add(slot3,slot1,slot2)

    try:
        bot.send_message(message.chat.id,about,parse_mode='markdown',reply_markup=main)
    except Exception:pass

#*--------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['help'])
def help_(message):

    main = tp.InlineKeyboardMarkup(row_width=2)
    slot1 = tp.InlineKeyboardButton('Slot 1',url='')
    slot2 = tp.InlineKeyboardButton('Slot 2',url='')
    slot3 = tp.InlineKeyboardButton('Slot 3',url='')
    main.add(slot3,slot1,slot2)

    try:
        bot.send_message(message.chat.id,help_,parse_mode='markdown',reply_markup=main)
    except Exception:pass


#*-------------------------------------------------------------------------------------------------------------------------------------
#*-------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['update'])
def update_(msg):
    if msg.chat.id == ADMIN_CHAT:
        bot.send_message(msg.chat.id,'Getting Data From Channel...')
        try:
            runner()
        except:
            bot.send_message(msg.chat.id,'Failed To Fetch!')
        time.sleep(3)
        bot.send_message(msg.chat.id,'Packing Data in JSON...')
        try:
            JsonPacker()
        except:
            bot.send_message(msg.chat.id,'Failed To Pack!')
        finally:
            bot.send_message(msg.chat.id,'Done!!')

#*-------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['broadcast'])
def broadcast(message):

    if message.chat.id == ADMIN_CHAT:
        if not message.reply_to_message: bot.send_message(message.chat.id,'Please reply to a text message to send.')

        if message.reply_to_message:
            IDs = collections.distinct('_id')
            sleep_var = 26

            for id_ in IDs:
                if sleep_var%25 == 0:
                    time.sleep(0.6)
                    sleep_var += 1
                else:
                    try:
                        bot.send_message(id_,message.reply_to_message.text)
                        sleep_var += 1
                    except Exception as e:
                        print(e)

#*--------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['block'])
def block(msg):
    if msg.chat.id == ADMIN_CHAT:
        if msg.reply_to_message:
            try:
                bot.send_message(msg.reply_to_message.forward_from.id,'Please Stop Spamming.\nYour requests has been paused for 10 minutes.')
            except: pass

#*--------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(commands=['send'])
def send(message):
    if message.chat.id == ADMIN_CHAT:
        ID = util.extract_arguments(message.text)
        if message.reply_to_message:
            try:
                bot.send_message(ID,message.reply_to_message.text)
            except Exception: bot.send_message(ADMIN_CHAT,'Somethign went wrong...Try Again.')
        elif not message.reply_to_message: bot.send_message(ADMIN_CHAT,'Please reply to a text message to send.')

#*--------------------------------------------------------------------------------------------------------------------------------------

@bot.message_handler(content_types=['text','sticker','photo','video','audio','document'])
def user_to_admin(message):
    if message.chat.id == ADMIN_CHAT:
        if message.reply_to_message:
            try:
                m = message.reply_to_message.forward_from.id
            except Exception: pass
            try: bot.send_message(m,message.text)
            except Exception: pass
            try: bot.send_sticker(m,message.sticker.file_id)
            except Exception: pass
            try: bot.send_photo(m,message.photo.file_id)
            except Exception: pass
            try: bot.send_video(m,message.video.file_id)
            except Exception: pass
            try: bot.send_audio(m,message.audio.file_id)
            except Exception: pass
        else: pass
    else:
        try : bot.forward_message(ADMIN_CHAT,message.chat.id,message.message_id)
        except Exception: pass

#*---------------------------------------------------------------------------------------------------

    if message.content_type=='text' and message.chat.id != ADMIN_CHAT:
        with open('urls.json','r') as f:
            data = json.load(f)
        text = message.text

        def WordFinder(queryWord):
            ignorelist = ['a','an','k','want','your','the','and','on','to','in','are','for','by','you','me','yes','no','of','is','it','I','.','/',',','[',']','?',':',';','-','(',')','!']
            point = []
            sentences = data.keys()
            for sentence in sentences:
                wordPoint = 0
                sentence_ = None
                queryWord = queryWord.lower()
                sentence2 = sentence.lower()

                if sentence2[1:] in queryWord and len(sentence2[1:]) > 3:
                    if not sentence[1:] in ['h','k','b']:
                            wordPoint += 1
                            sentence_  = sentence                  
                if queryWord in sentence2.replace('!','') and len(queryWord) > 3:
                    if not queryWord in ignorelist: 
                        wordPoint += 1
                        sentence_  = sentence 
                for word in sentence2.split(' '):
                    if ' ' in queryWord:
                        words = queryWord.split(' ')
                        for word_ in words:
                            if not word_ in ignorelist:
                                if word_ == word:
                                    wordPoint += 1
                                    sentence_ = sentence
                    elif word == queryWord:
                        if not word in ignorelist:
                            wordPoint += 1
                            sentence_ = sentence
                if sentence_ != None:
                    point.append({wordPoint:sentence_})
            return point
        
        result = WordFinder(text)
        Num = []
        wordcount = 1 if len(text.split(' ')) <= 1 else 2
        for dict_ in result:
            for k,v in dict_.items():
                Num.append(k)

        buttons = []
        for dict_ in result:
            buttons.append([tp.InlineKeyboardButton(text=name[1:],url=data[name]) for num,name in dict_.items() if num >= wordcount])
        main = tp.InlineKeyboardMarkup(row_width=1)
        for button in buttons:
            for b in button:
                main.add(b)

        for button in buttons:
            if button:
                sent = bot.send_message(message.chat.id,'*Are you looking for this?*',reply_markup=main,parse_mode='markdown')
                bot.forward_message(ADMIN_CHAT,message.chat.id,sent.message_id)
                break


@server.route('/' + token, methods=['POST'])
def getMessage():  
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200
@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=url + token)
    return "!", 200
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
