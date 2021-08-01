#!/usr/bin/env python3
import logging
from telegram import Update, Animation, TelegramError, ParseMode, MessageEntity, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, PicklePersistence
import re
from youtube_dl import YoutubeDL
import json
import os
from youtubesearchpython import SearchVideos
import shutil
from config import BOT_TOKEN

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

TOKEN = BOT_TOKEN #token

updater = Updater(TOKEN)
dispatcher = updater.dispatcher

# global variable incase we want to delete the song
z = []


def start(update, context):
    update.message.reply_text(
        f'Do /help')

# This function replies with 'Moshi Moshi <user.first_name> kun!!'
def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        f'Moshi Moshi {update.effective_user.first_name} kun!!')

# This function replies with 'Welcome <user.full_name> kun'


def welcome_message(update, context):
    new_members = update.message.new_chat_members
    for member in new_members:
        if member.full_name != 'Ongaku-chan':
            update.message.reply_text(f'Welcome {member.full_name} kun')
        else:
            pass

# gifs


def gif_ok(update, context):
    bot = context.bot
    bot.send_animation(update.effective_chat.id, 'https://tenor.com/0wx8.gif')


def gif_hug(update, context):
    bot = context.bot
    bot.send_animation(update.effective_chat.id, 'https://tenor.com/HXid.gif')


def gif_cringe(update, context):
    bot = context.bot
    bot.send_animation(update.effective_chat.id, 'https://tenor.com/byEpc.gif')

def gif_kawaii(update,context):
    bot=context.bot
    bot.send_animation(update.effective_chat.id, "https://tenor.com/0wx9.gif")


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="unknown command")


def get_single_song(update, context):
    global z

    bot = context.bot
    chat_id = update.effective_chat.id
    message_id = update.effective_message['message_id']
    username = update.effective_chat.username

    logging.log(
        logging.INFO, f'start to query message in chat:{chat_id} from {username}')

    url = update.message.text

    # making a new folder and shifting the path to that path

    # foldername = .temp{message_id}{chat_id}
    os.system(f'mkdir .temp{message_id}{chat_id}')

    # basically cd to .temp{message_id}{chat_id}
    os.chdir(f'./.temp{message_id}{chat_id}')

    # log and send message to client
    logging.log(logging.INFO, f'start downloading')
    _message1 = bot.send_message(chat_id=chat_id, text="Fetching it for you..")

    # search for song
    try:

        search = SearchVideos(url, offset=1, max_results=1)
        test = search.result()
        p = json.loads(test)
        q = p.get("search_result")
    except:
        bot.send_message(
            chat_id=chat_id, text="Song not found(invalid name/url)")
        bot.delete_message(chat_id=update.effective_chat.id,
                           message_id=_message1['message_id'])
        logging.log(
            logging.INFO, f'download interrupted- invalid url/song name')
        return

    try:
        url = q[0]["link"]
        # print('found it')
    except:
        bot.send_message(chat_id=chat_id, text="Song not found")
        bot.delete_message(chat_id=update.effective_chat.id,
                           message_id=_message1['message_id'])
        logging.log(
            logging.INFO, f'download interrupted- invalid url/song name')
        return

    bot.delete_message(chat_id=update.effective_chat.id,
                       message_id=_message1['message_id'])

    type = "audio"
    if type == "audio":
        # format ydl request to download
        # check https://github.com/ytdl-org/youtube-dl/blob/master/README.md#embedding-youtube-dl and
        # https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312
        ydl_opts = {
            "format": "bestaudio",
            "addmetadata": True,
            "key": "FFmpegMetadata",
            "writethumbnail": True,
            "prefer_ffmpeg": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "outtmpl": "%(id)s.mp3",
            "quiet": True,
            "logtostderr": False,
        }
        song = True
    try:
        # download song
        with YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url)
    except:
        pass

    # sending song
    logging.log(logging.INFO, 'sending to client')
    try:
        sent = 0
        _message2 = bot.send_message(
            chat_id=chat_id, text="yayy...got it, now sending to you...")

        os.chdir('./..')  # cd ..
        # return list like files=['.temphsgvs\\hithere.mp3']
        files = [os.path.join(root, f) for root, dir, filenames in os.walk(
            f".temp{message_id}{chat_id}") for f in filenames if os.path.splitext(f)[1] == '.mp3']
        for file in files:
            _audio_deets = bot.send_audio(chat_id=chat_id, audio=open(
                f'./{file}', 'rb'), timeout=1000)
            z.append(_audio_deets)
            sent += 1
    except:
        pass

    # delete folder
    location = os.getcwd()
    dir = f".temp{message_id}{chat_id}"
    path = os.path.join(location, dir)
    shutil.rmtree(path)

    bot.delete_message(chat_id=update.effective_chat.id,
                       message_id=_message2['message_id'])

    if sent == 0:
        bot.send_message(
            chat_id=chat_id, text="It seems there was a problem in sending the song.")
        logging.log(logging.INFO, 'download Failed')
    else:
        logging.log(logging.INFO, 'sent')


def get_help(update, context):
    bot = context.bot
    chat_id = update.effective_chat.id
    help_text = '''Sagiri-chan downloads music from youtube.
Commands: 
          /hello
          /song Syntax: Enter /song [song name] or /song [url]
          /help
          /delete - to delete any song you didnt like (admin privileges required)
Add me in a group with admin privileges to enable me to repond with gifs.
texts i respond to: [my-name] how are you? , [my-name] gimme a hug , [my-name] cringe, [my-name] kawaii
'''

    bot.send_message(chat_id=chat_id, text=help_text)


def delete(update, context):
    bot = context.bot
    chat_id = update.effective_chat.id
    try:
        bot.delete_message(chat_id=update.effective_chat.id,
                       message_id=z[0]['message_id'])
        del z[0]
    except:
        logging.log(logging.INFO, 'nothing to delete')

        pass

# Dispatcher thingy
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('hello', hello))
dispatcher.add_handler(MessageHandler(
    Filters.status_update.new_chat_members, welcome_message))
dispatcher.add_handler(MessageHandler(
    Filters.regex(r'(Ongaku-chan|ongaku-chan) how are you?'), gif_ok))
dispatcher.add_handler(MessageHandler(Filters.regex(
    r'(Ongaku-chan|ongaku-chan) gimme a hug'), gif_hug))
dispatcher.add_handler(MessageHandler(Filters.regex(
    re.compile(r'(Ongaku-chan|ongaku-chan) cringe', re.IGNORECASE)), gif_cringe))
dispatcher.add_handler(MessageHandler(Filters.regex(r'(Ongaku-chan|ongaku-chan) kawaii'), gif_kawaii))
dispatcher.add_handler(CommandHandler("song", get_single_song))
dispatcher.add_handler(CommandHandler("help", get_help))
dispatcher.add_handler(CommandHandler("delete", delete))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

# Connect to Telegram and wait for messages
POLLING_INTERVAL = 0.8
updater.start_polling(poll_interval=POLLING_INTERVAL,
                      drop_pending_updates=True)

# Keep the program running until interrupted
updater.idle()
