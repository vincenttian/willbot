from __future__ import print_function
from slacker import Slacker
from markov import Markov
from collections import defaultdict
import pprint

auth_token = "xoxp-8268799495-8274597347-13166505222-f759b7f873"

slack = Slacker(auth_token)
# Send a message to #general channel
# slack.chat.post_message('#general', 'Hello fellow slackers!')

# Get users list
response = slack.users.list()
users = response.body['members']

f = open('will_word_database.txt','r+')
channel_dict = defaultdict(int)

def get_messages(channel_id, ts=None):
    response = slack.channels.history(channel_id, count=1000, latest=ts).body 
    messages = response['messages']
    for message in messages:
        if 'user' in message:
            if message['user'] == "U087X4UQZ": # will's user id
                text = message['text'].encode('ascii', 'ignore')
                print (text, file=f)
                channel_dict[channel_id] += 1
        if 'username' in message:
            if message['username'] == "kimjongwill": # will's user id
                text = message['text'].encode('ascii', 'ignore')
                print (text, file=f)
                channel_dict[channel_id] += 1
    if response['has_more']:
        get_messages(channel_id, ts=message['ts'])

def get_all_channel_messages():
    for channel in slack.channels.list().body.items()[0][1]:
        get_messages(channel['id'])

from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to
import nltk
from nltk import trigrams
from bottle import route, run
import re 
import operator

markov = Markov(f)
triples = markov.triples()
all_trigrams = defaultdict(int)

for triple in triples:
    all_trigrams[' '.join(triple).lower()] += 1

all_trigrams = dict(all_trigrams)
trigram_popuplarity = sorted(all_trigrams.items(), key=operator.itemgetter(1))
for t in trigram_popuplarity:
    if t[1] < 5:
        del all_trigrams[t[0]]

pprint.pprint(all_trigrams)

def main():
    bot = Bot()
    # get_all_channel_messages()
    bot.run()
    port = int(os.environ.get('PORT', 5000))
    run(host='0.0.0.0', port=port, debug=True)

@listen_to('(.*)', re.IGNORECASE)
def respond(message, slack_words):
    string_trigrams = trigrams(slack_words.lower().split(' '))

    for tri in string_trigrams:
        if ' '.join(tri).lower() in all_trigrams:
            message.reply(markov.generate_markov_text_with_words(tri[0], tri[1]))

@listen_to('willbot', re.IGNORECASE)
def respond(message):
    pprint.pprint('called willbot')
    message.reply(markov.generate_markov_text(size=13))

@route('/')
def hello():
    return "Hello World!"

if __name__ == "__main__":
    main()







