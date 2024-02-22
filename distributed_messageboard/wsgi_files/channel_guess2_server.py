## channel.py - a simple message channel
##

from flask import Flask, request, render_template, jsonify
import json
import requests
from bot.bot_guessing2 import GuessingBot2 as GuessingBot
import datetime

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db

HUB_URL = 'https://temporary-server.de/'
HUB_AUTHKEY = 'Crr-K3d-2N'
CHANNEL_AUTHKEY = '22022024'
CHANNEL_NAME = "The 2D Point Guessing Game"
CHANNEL_ENDPOINT = "http://vm146.rz.uni-osnabrueck.de/user058/channel_guess2.wsgi" # don't forget to change it in the bottom of the file
CHANNEL_FILE = 'data/messages_guess2.json'

bot = GuessingBot()

def send_start(): # send a starting message when the channel is restarted.
    messages = read_messages()
    last_message = messages[-1]

    # check if last message is the start message of bot
    if last_message['user'] == False: 
        if bot.is_start(last_message['content']):
            return

    # BOT message append
    messages.append({'content':bot.start_message(), 'sender':bot.name, 'timestamp':datetime.datetime.now().isoformat(), 'user':False})
    save_messages(messages)

@app.cli.command('register')
def register_command():
    global CHANNEL_AUTHKEY, CHANNEL_NAME, CHANNEL_ENDPOINT

    # send a POST request to server /channels
    response = requests.post(HUB_URL + '/channels', headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
                             data=json.dumps({
            "name": CHANNEL_NAME,
            "endpoint": CHANNEL_ENDPOINT,
            "authkey": CHANNEL_AUTHKEY}))

    if response.status_code != 200:
        print("Error creating channel: "+str(response.status_code))
        return

def check_authorization(request):
    global CHANNEL_AUTHKEY
    # check if Authorization header is present
    if 'Authorization' not in request.headers:
        return False
    # check if authorization header is valid
    if request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
        return False
    return True

@app.route('/health', methods=['GET'])
def health_check():
    global CHANNEL_NAME
    if not check_authorization(request):
        return "Invalid authorization", 400
    return jsonify({'name':CHANNEL_NAME}),  200

# GET: Return list of messages
@app.route('/', methods=['GET'])
def home_page():
    if not check_authorization(request):
        return "Invalid authorization", 400
    # fetch channels from server
    return jsonify(read_messages())

# POST: Send a message
@app.route('/', methods=['POST'])
def send_message():
    global bot
    # fetch channels from server
    # check authorization header
    if not check_authorization(request):
        return "Invalid authorization", 400
    # check if message is present
    message = request.json
    if not message:
        return "No message", 400
    if not 'content' in message:
        return "No content", 400
    if not 'sender' in message:
        return "No sender", 400
    if not 'timestamp' in message:
        return "No timestamp", 400
    # add message to messages
    messages = read_messages()
    messages.append({'content':message['content'], 'sender':message['sender'], 'timestamp':message['timestamp'], 'user':True})
    # BOT message append
    answer = bot.apply(message['content'], message['sender'])
    messages.append({'content':answer, 'sender':bot.name, 'timestamp':datetime.datetime.now().isoformat(), 'user':False})
    save_messages(messages)
    return "OK", 200

def read_messages():
    global CHANNEL_FILE
    global bot
    try:
        f = open(CHANNEL_FILE, 'r')
    except FileNotFoundError:
        return [{'content':bot.start_message(), 'sender':bot.name, 'timestamp':datetime.datetime.now().isoformat(), 'user':False}]
    try:
        messages = json.load(f)
    except json.decoder.JSONDecodeError:
        messages = [{'content':bot.start_message(), 'sender':bot.name, 'timestamp':datetime.datetime.now().isoformat(), 'user':False}]
    f.close()
    return messages

def save_messages(messages):
    global CHANNEL_FILE
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f)

send_start()

# Start development web server
if __name__ == '__main__':
    app.run(port=5003, debug=True)
