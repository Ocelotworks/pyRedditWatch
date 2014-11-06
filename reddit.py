#!/usr/bin/python
import json
from urllib import FancyURLopener
import urllib
import socket
import time
import ssl
import random
import threading
import os
import unidecode
import ConfigParser

genNick = "pyRedditChecker" + str(random.randint(0, 1000))
confParser = ConfigParser.ConfigParser({
    'server': 'irc.freenode.net',
    'port': 6667,
    'useSSL': False,
    'isZNC': False,
    'nickname': genNick,
    'username': genNick,
    'realName': genNick,
    'password': "",
    'zncPass': ""
})
confParser.read(r'./settings.conf')

#Load options from config file#
server = str(confParser.get('irc', 'server'))
port = int(confParser.get('irc', 'port'))
useSSL = bool(confParser.get('irc', 'ssl'))
isZNC = bool(confParser.get('irc', 'isZNC'))
nickname = str(confParser.get('irc', 'nickname'))
username = str(confParser.get('irc', 'username'))
realName = str(confParser.get('irc', 'realName'))
identPass = str(confParser.get('irc', 'identPass'))
zncPass = str(confParser.get('irc', 'zncPass'))

channels = str(confParser.get('irc', 'channels'))

if server == "":
    print "====No server set. Defaulting to freenode.===="
    server = "irc.freenode.net"
if port == "" or not isinstance(port, int):
    print "====No or invalid port set. Defaulting to 6667.===="
    port = 6667
if useSSL == "":
    print "====SSL not specified. True and False are case sensitive! Defaulting to no.===="
    useSSL = False
if isZNC == "":
    print "====ZNC not specified. True and False are case sensitive! Defaulting to no.===="
    isZNC = False
if nickname == "":
    print "====Nickname not specified. Defaulting to pyRedditChecker followed by a random number.===="
    nickname = "pyRedditChecker" + str(random.randint(0, 1000))
if username == "":
    print "====Username not specified. Defaulting to nickname.===="
    username = nickname
if realName == "":
    print "====Real name not specified. Defaulting to nickname.===="
    realName = nickname
if zncPass == "" and isZNC == True:
    print "WARNING: ====ZNC password not specified!!===="

if useSSL == True:
    ircSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    irc = ssl.wrap_socket(ircSocket)
else:
    irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    irc.connect((server, port))
except Exception as e:
    print "Bad hostname or port: " + server + ":" + str(port)

if isZNC == True:
    irc.write('PASS ' + zncPass + '\r\n')
    irc.write('NICK ' + nickname + '\r\n')
    irc.write('USER ' + username + ' ' + nickname + ' ' + nickname + ' ' + nickname + ':' + realName +'\r\n')
else:
    time.sleep(1)
    irc.send('NICK ' + nickname + '\r\n')
    irc.send('USER ' + username + ' ' + nickname + ' ' + nickname + ' ' + nickname + ':' + realName +'\r\n')

time.sleep(1)
irc.recv(8192)

irc.send("PRIVMSG nickserv :IDENTIFY " + username + " " + identPass)

for chan in channels.split(", "):
    irc.send('JOIN ' + chan + '\r\n')

noColor = "\x03"
checkFile = open('checks.txt', 'r+')
runningChecks = []

colorDict = {
    'white': 0,
    'black': 1,
    'blue': 2,
    'green': 3,
    'red': 4,
    'brown': 5,
    'purple': 6,
    'orange': 7,
    'yellow': 8,
    'light-green': 9,
    'teal': 10,
    'light-cyan': 11,
    'light-blue': 12,
    'pink': 13,
    'gray': 14,
    'light-gray': 15
}

def getTiny(url):
    reqUrl = urllib.urlopen('http://tinyurl.com/api-create.php?' + urllib.urlencode({'url': url}))
    tinyUrl = reqUrl.read()
    return tinyUrl

def listColors():
    colorString = "Available Colors: "
    for color in colorDict.keys():
        colorString += randomColor(color) + color + noColor + ", "
    colorString = colorString.rstrip(", ")
    return colorString

class checkThread(threading.Thread):
    def __init__(self, subreddit, color, delay, channel):
        threading.Thread.__init__(self)
        self.subreddit = subreddit
        self.color = color
        self.delay = delay
        self.channel = channel
        self._stop = threading.Event()

    def run(self):
        checkNewLoop(self.subreddit, self.color, self.delay, self.channel)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

class customOpener(FancyURLopener, object):
    version = "Swagbot/9000.0"

def checkNewLoop(subreddit, color, delay, channel):
    while subreddit in runningChecks:
        checkNew(subreddit, color, delay, channel)
        time.sleep(0.1)

def checkNew(subreddit, color, delay, channel):
    time.sleep(delay)
    if subreddit in runningChecks:
        urlopen = customOpener().open
        subJson = urlopen("http://www.reddit.com/r/" + subreddit + "/new.json?sort=new")
        newPosts = json.loads(subJson.read())
        postList = newPosts['data']['children']
        doneIDs = open('doneid.txt', 'a+')
        readPosts = []

        for line in doneIDs:
            if line != "":
                readPosts.append(line.rstrip("\n"))

        for key, post in enumerate(postList):
            id = post['data']['name']
            title = post['data']['title']
            url = post['data']['url']
            domain = post['data']['domain']
            domain = domain.lower()

            if id not in readPosts:
                textColor = randomColor(color)

                doneIDs.write(id + "\n")
                shortID = post['data']['id']

                if domain != "imgur.com" and domain != "i.imgur.com" and domain != "self." + subreddit:
                    shortUrl = " [" + getTiny(url) + "]"
                elif domain == "imgur.com" or domain == "i.imgur.com":
                    shortUrl = " [" + url +"]"
                elif domain == "self." + subreddit:
                    shortUrl = " [self." + subreddit + "]"
                else:
                    shortUrl = "[Tek: url bork]"

                title = unidecode.unidecode(title)
                message = textColor + "/r/" + subreddit + noColor + " - " + title + " (http://redd.it/" + shortID + ")" + shortUrl
                sendMessage(channel, message)

def randomColor(color):
    if color in colorDict:
        colorInt = "\x03" + str(colorDict[color])
    else:
        colorInt = "\x03" + str(color)

    return colorInt

def addCheck(subreddit, color, delay, channel):
    checkFile.write(subreddit + " | " + str(color) + " | " + str(delay) + " | " + channel + "\n")
    thread = checkThread(subreddit, color, delay, channel)
    thread.daemon = True
    thread.name = "Thread-" + subreddit
    runningChecks.append(subreddit)
    thread.start()

def loadChecks():
    for line in checkFile:
        if line != "":
            checkInfo = line.split(" | ")
            addCheck(checkInfo[0], checkInfo[1], float(checkInfo[2]), checkInfo[3].rstrip("\n"))

def sendMessage(channel, message):
    irc.send(("PRIVMSG " + channel + " :" + str(message) + "\r\n"))

def processMessage(chanMessage, userMessage, channel):
    if chanMessage == "!add":
        try:
            subreddit = userMessage.split(' ')[1]
        except:
            subreddit = "error"

        try:
            color = userMessage.split(' ')[2]
        except:
            color = str(random.randint(1, 15))

        if subreddit == "error":
            sendMessage(channel, "Usage: !add [subreddit] (optional: color)")
        else:
            if subreddit not in runningChecks:
                addCheck(subreddit, color, 10, channel)
            else:
                sendMessage(channel, "That subreddit is already being checked!")

    if chanMessage == "!del":
        try:
            subreddit = userMessage.split(' ')[1]
        except:
            subreddit = "error"

        if subreddit == "error":
            sendMessage(channel, "Usage: !del [subreddit]")
        else:
            if subreddit not in runningChecks:
                sendMessage(channel, "Check for that channel not found!")
            else:
                with open('checks.txt') as oldfile, open('checkstemp.txt', 'w') as newfile:
                    for line in oldfile:
                        if not subreddit in line:
                            newfile.write(line)

                os.remove("checks.txt")
                os.rename("checkstemp.txt", "checks.txt")
                runningChecks.remove(subreddit)

    if chanMessage == "!list":
        sendMessage(channel, "Currently Checking:")
        for check in runningChecks:
            sendMessage(channel, "/r/" + check)

    if chanMessage == "!colour":
        try:
            subreddit = userMessage.split(' ')[1]
        except:
            subreddit = "error"

        try:
            color = userMessage.split(' ')[2]
        except:
            color = ""

        if subreddit == "error":
            sendMessage(channel, "Usage: !colour [subreddit] [new color]")
        else:
            if subreddit not in runningChecks:
                sendMessage(channel, "Check not found.")
            else:
                with open('checks.txt') as oldfile, open('checkstemp.txt', 'w') as newfile:
                        for line in oldfile:
                            if subreddit in line:
                                changeColor = line.split(" | ")
                                newfile.write(changeColor[0] + " | " + color + " | " + changeColor[2] + " | " + changeColor[3])
                                runningChecks.remove(subreddit)
                                addCheck(changeColor[0], color, float(changeColor[2]), changeColor[3].rstrip("\n"))
                            else:
                                newfile.write(line)

                        os.remove("checks.txt")
                        os.rename("checkstemp.txt", "checks.txt")
    
    if chanMessage == "!listcolours":
        sendMessage(channel, listColors())

loadChecks()

while True:
    data = irc.recv(8192)
    print data.rstrip("\n")
    if data.find('PING') != -1:
        irc.send('PONG ' +data.split()[1]+'\r\n')
    userMessage = data.split(':')[-1].strip()
    chanMessage = userMessage.split(' ')[0].lower()
    channel = data.split(' ')
    if len(channel) > 2:
        channel = channel[2]
    else:
        channel = ""

    processMessage(chanMessage, userMessage, channel)
