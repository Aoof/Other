import discord
import dotenv
import os

from string import ascii_lowercase

# Chatbot dependencies

import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('chatbot_model.h5')
import json
import random
import requests

dotenv.load_dotenv()

client = discord.Client()


intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)
    return(np.array(bag))

def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words,show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i,r] for i,r in enumerate(res) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def getResponse(ints, intents_json):
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tag):
            response = random.choice(i['responses'])
            break
    return response

def chatbot_response(msg):
    ints = predict_class(msg, model)
    response = getResponse(ints, intents)
    return response

def Story():
    PROFESSION = [1, 2, 3, 4]
    ADJ = [1, 2]
    fp = json.load(open("./filler.json"))
    THEMATRIX = random.choice(fp["Names"])
    SYSTEM = random.choice(fp["Nouns"])
    NEO = random.choice(fp["Names"])
    ENEMY = random.choice(fp["Nouns"])
    PROFESSION = [random.choice(fp["Professions"]), random.choice(
        fp["Professions"]), random.choice(fp["Professions"]), random.choice(fp["Professions"])]
    SAVE = random.choice(fp["Verbs"])
    UNPLUGGED = random.choice(fp["VerbsPP"])
    FIGHT = random.choice(fp["Verbs"])
    INSIDE = random.choice(fp["Prepositions"])
    ADJ = [random.choice(fp["Adjectives"]),
           random.choice(fp["Adjectives"])]

    # Story

    STORY = (f"{THEMATRIX} is a {SYSTEM}, {NEO}. That {SYSTEM} is our {ENEMY}. "
             f"But when you're {INSIDE}, you look around, what do you see? "
             f"{PROFESSION[0]}, {PROFESSION[1]}, {PROFESSION[2]}, {PROFESSION[3]}.The very minds "
             f"of the people we are trying to {SAVE}. But until we do, "
             f"these people are still a part of that {SYSTEM} and that makes "
             f"them our {ENEMY}. You have to understand, most of these people "
             f"are not ready to be {UNPLUGGED}. And many of them are so {ADJ[0]}, "
             f"so hopelessly {ADJ[1]} on the {SYSTEM}, that they will {FIGHT} to protect it.")
    return STORY

def Get_Story():
    enemy = random.choice (["chihuahua", "border collie", "wolf"])
    father = random.choice (["John", "Mr.Pickles", "Hairyface", "Willy Wonka", "Steve", "Bob"])
    enemyadj = ["grimy", "muddy", "awful", "grotesque", "hideous", "adorable", "cute"]
    intro1 = "I was sitting on the edge of the rocky cliff beside my favourite tree."
    intro2 = "Alone in the searing desert, I was wondering why I was leaning against a cactus."
    intro3 = "Staring out my apartment window, I saw my reflection staring back at me."
    char1 = "As I looked out into the distance, I thought about my past and all of the drama in it."
    char2 = "I wondered if this was my destiny- trying to find happiness."
    char3 = "I pulled out the photo of my long lost mother and where on earth she could be."
    prob1 = "Suddenly I was covered from head to toe with darkness. I couldn't breathe or see. Everything went black..."
    prob2 = "All of a sudden a psychopathic " + enemy + " grinned at me,showing all his razor sharp teeth. Suddenly it started to claw at my face. From the loss of blood, I collapsed onto the tough ground..."
    prob3 = "I suddenly felt a sharp needle sink into my flesh. It was a tranquilizer. But before I knew it I started feeling really drowsy. Everything went black..."
    sol1 = "I forced my drowsy eyes open my eyes to see a bright light."
    sol2 = "I forced my drowsy eyes open to find myself on the back of a massive dragon and a man in front of me."
    sol3 = "I forced my drowsy eyes open to the sounds of a " + random.choice(enemyadj) + " " +enemy + " licking my face."
    end1 = "A man came to my side with a knife. It was my father!" + father + "!" "'Go to sleep young one...'"
    end2 = "It was difficult to keep my eyes open as I stuggled to breathe. "
    end3 = "Out of nowhere, a duck wearing a deerstalker looked me in the eye and pointed a gun at me. 'Quack.' And that was the last thing I heard..."

    intros = [intro1, intro2, intro3]
    characters = [char1, char2, char3]
    problems = [prob1, prob2, prob3]
    solutions = [sol1, sol2, sol3]
    endings = [end1, end2, end3]

    text = random.choice(intros) + " " + \
    random.choice(characters) + " " + \
    random.choice(problems) + " " + \
    random.choice(solutions) + " " + \
    random.choice(endings)

    return text


def get_Quote():
    params = {
        'method':'getQuote',
        'lang':'en',
        'format':'json'
    }
    response = requests.get('http://api.forismatic.com/api/1.0/',params)
    jsonText =json.loads(response.text)
    return jsonText["quoteText"],jsonText["quoteAuthor"]


isGameRunning = False
board = []
inAMatch = []
turn = ""

async def start_Knots_Crosses(message):
    global isGameRunning, board, inAMatch, turn
    if len(inAMatch):
        inAMatch.append(message.author)
        isGameRunning = True
        board = [[0, 0, 0],
                 [0, 0, 0],
                 [0, 0, 0]]
        turn = random.choice(inAMatch)
        await Knots_Crosses_event(message, True)
    if len(inAMatch) < 2:
        inAMatch.append(message.author)

def CheckComb(combination, i):
    global isGameRunning, board, inAMatch, turn
    l = []
    for comb_x, comb_y in combination:
        if board[comb_y][comb_x] == i:
            l.append([comb_x, comb_y])
    return len(l) == len(combination)

async def Knots_Crosses_event(message, display=False):
    global isGameRunning, board, inAMatch, turn
    if len(inAMatch) == 2 and type(message) != str:
        # Logic here
        if message.content.lower() in ["a1", "a2", "a3", "b1", "b2", "b3", "c1", "c2", "c3"]:
            first, second = list(message.content)
            if len(first) == 1:
                if first.lower() in ascii_lowercase:
                    ltr = first
                    num = second

            if len(second) == 1:
                if second.lower() in ascii_lowercase:
                    ltr = second
                    num = first

            if ltr == "a":
                ltr = 0
            if ltr == "b":
                ltr = 1
            if ltr == "c":
                ltr = 2
            num = int(num) - 1

            if board[num][ltr] == 0 and message.author == turn:
                board[num][ltr] = inAMatch.index(turn) + 1
            else:
                return

            winner = None
            availableSpots = []

            for y, xList in enumerate(board):
                for x, data in enumerate(xList):
                    if data == 0:
                        availableSpots.append([x, y])

            combs = [[[0, 0], [1, 0], [2, 0]],
                     [[0, 1], [1, 1], [2, 1]],
                     [[0, 2], [1, 2], [2, 2]],
                     [[0, 0], [0, 1], [0, 2]],
                     [[1, 0], [1, 1], [1, 2]],
                     [[2, 0], [2, 1], [2, 2]],
                     [[0, 0], [1, 1], [2, 2]],
                     [[2, 0], [1, 1], [0, 2]]]

            for comb in combs:
                if CheckComb(comb, 1):
                    winner = inAMatch[0]
                if CheckComb(comb, 2):
                    winner = inAMatch[1]

            if winner != None:
                await message.channel.send("<@%s> IS THE WINNER. 🎊🎉🎉🎊" % winner.id)
                isGameRunning = False
                inAMatch = []
                return
            elif len(availableSpots) == 0:
                await message.channel.send("The match between <@{0}> & <@{1}> ended up a tie.".format(inAMatch[0].id, inAMatch[1].id))
                isGameRunning = False
                inAMatch = []
                return

            turn = inAMatch[0] if turn == inAMatch[1] else inAMatch[1]

        # Draw board
        embed = discord.Embed(title="*{0} V.S. {1}*".format(inAMatch[0].name, inAMatch[1].name))

        printableBoard = []
        for y, xList in enumerate(board):
            printableBoard.append([])
            for x, data in enumerate(xList):
                if data == 0:
                    printableBoard[-1].append(" ")
                elif data == 1:
                    printableBoard[-1].append("X")
                elif data == 2:
                    printableBoard[-1].append("O")
        embed.add_field(name=f"{turn}'s turn.", value="```     a   b   c \n   ┌───┬───┬───┐ \n 1 │ {0[0]} │ {0[1]} │ {0[2]} │ \n   ├───┼───┼───┤ \n 2 │ {1[0]} │ {1[1]} │ {1[2]} │ \n   ├───┼───┼───┤ \n 3 │ {2[0]} │ {2[1]} │ {2[2]} │ \n   └───┴───┴───┘```".format(printableBoard[0], printableBoard[1], printableBoard[2]))

        await message.channel.send(embed=embed)
    elif len(inAMatch) != 2:
        await message.channel.send("Waiting for other players, Write knots and crosses to join <@%s>'s match." % message.author.id)


# DISCORD CHAT LOGIC STARTS HERE

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    print("isGameRunning: ", isGameRunning, "\nBoard: ", np.array(board), '\nIn A Match: ', inAMatch, '\nTurn: ', turn)
    if message.author == client.user or message.channel.name != "bot-commands" or message.author.bot:
        return
    if not isGameRunning:
        res = chatbot_response(message.content)

        if res == "INSERT_QUOTE_HERE":
            res = "{0[0]} - {0[1]}".format(get_Quote())

        if res == "INSERT_STORY_HERE":
            res = random.choice([Story(), Get_Story()])

        if res in ["Starting Tic Tac Toe...", "Launching Knots and Crosses..."]:
            await message.channel.send(res)
            await start_Knots_Crosses(message)
            return

        await message.channel.send(res)

    if isGameRunning:
        await Knots_Crosses_event(message)



client.run(os.environ.get("DISCORDBOTTOKEN"))
