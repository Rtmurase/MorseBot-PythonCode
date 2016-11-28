from Adafruit_CharLCD import Adafruit_CharLCD
lcd = Adafruit_CharLCD(rs=26, en=19, d4=13, d5=6, d6=5, d7=11, cols=16, lines=2)

from json import load
from urllib2 import urlopen

from pymongo import MongoClient

import RPi.GPIO as GPIO
import time

#from time import sleep

GPIO.setmode(GPIO.BCM)
led = 22 
button = 17
#indicator = 27

restartBut = 27
endMsgBut = 23
nextWordBut = 24
nextCharBut = 25
GPIO.setup(restartBut, GPIO.IN)
GPIO.setup(endMsgBut, GPIO.IN)
GPIO.setup(nextWordBut, GPIO.IN)
GPIO.setup(nextCharBut, GPIO.IN)

GPIO.setup(led, GPIO.OUT)
#GPIO.setup(indicator, GPIO.OUT)
GPIO.setup(button, GPIO.IN)

CODE_reversed = {
    '..-.': 'F', '-..-': 'X', '.--.': 'P', '-': 'T', '..---': '2',
    '....-': '4', '-----': '0', '--...': '7',
    '...-': 'V', '-.-.': 'C', '.': 'E', '.---': 'J',
    '---': 'O', '-.-': 'K', '----.': '9', '..': 'I',
    '.-..': 'L', '.....': '5', '...--': '3', '-.--': 'Y',
    '-....': '6', '.--': 'W', '....': 'H', '-.': 'N', '.-.': 'R',
    '-...': 'B', '---..': '8', '--..': 'Z', '-..': 'D', '--.-': 'Q',
    '--.': 'G', '--': 'M', '..-': 'U', '.-': 'A', '...': 'S', '.----': '1',
    '': ''}
CODE = {'A': '.-',     'B': '-...',   'C': '-.-.', 
        'D': '-..',    'E': '.',      'F': '..-.',
        'G': '--.',    'H': '....',   'I': '..',
        'J': '.---',   'K': '-.-',    'L': '.-..',
        'M': '--',     'N': '-.',     'O': '---',
        'P': '.--.',   'Q': '--.-',   'R': '.-.',
        'S': '...',    'T': '-',      'U': '..-',
        'V': '...-',   'W': '.--',    'X': '-..-',
        'Y': '-.--',   'Z': '--..',

        '0': '-----',  '1': '.----',  '2': '..---',
        '3': '...--',  '4': '....-',  '5': '.....',
        '6': '-....',  '7': '--...',  '8': '---..',
        '9': '----.', ' ': ' ' }



def HomeDisplay():
    lcd.clear()
    lcd.message("1 Recieve 2 Send")
    lcd.set_cursor(0,1)
    lcd.message("3 Options 4 SOS")
    while(True):
        if (GPIO.input(restartBut)):
            #print("recieveMsgMode()")
            recieveMsgMode()
            lcd.clear()
            lcd.message("Message\nComplete")
            time.sleep(1)
            break
        if (GPIO.input(endMsgBut)):
            time.sleep(.5)
            while (True):
                MorseButton()
                break
            time.sleep(.5)
            break
        if (GPIO.input(nextWordBut)):
            PracticeMode()
            break
        if (GPIO.input(nextCharBut)):
            #print("SOSMode()")
            SOSMode()
            break

def MorseButton():
    lcd.clear()
    lcd.message("enter code")
    prev = 0
    prevChar = 1
    prevWord = 1
    buttonPushedTime = 0
    buttonUpTime = 0
    character  = ""
    word = ""
    message = ""
    morseText = ""
    notFirstPress = False
    #print("enter code")
    while True:
        if (GPIO.input(restartBut)):
            character =""
        time.sleep(.01)
        if(GPIO.input(button)):
            if (GPIO.input(button) != prev):
                GPIO.output(led, GPIO.HIGH)
                buttonUpTime=time.time()-buttonPushedTime
                buttonUpTime=time.time()
                notFirstPress = True;
                prev = 1
                prevWord = 0
                prevChar=0
        else:
            if (GPIO.input(nextCharBut) != prevChar):
                if (GPIO.input(nextCharBut)):
                    temp =(CODE_reversed[character])
                    word = word + temp
                    #print(word)
                    lcd.clear()
                    lcd.message(character)
                    lcd.set_cursor(0,1)
                    lcd.message(message + word)
                    i = 0
                    if (len(message+word) > 16):
                        i = len(message + word) - 16
                        while (i >0):
                            lcd.move_left()
                            i = i -1
                    morseText = morseText + character+ ","
                    character = ""
                    prevChar = 1;
            if (GPIO.input(nextWordBut) !=prevWord):
                if (GPIO.input(nextWordBut)):
                    word = word + CODE_reversed[character] + " "
                    word = word.replace("  ", " ")
                    #print(word)
                    message = message +word 
                    lcd.clear()
                    lcd.message(character)
                    lcd.set_cursor(0,1)
                    lcd.message(message)
                    morseText = morseText + character + "/"
                    word = ""
                    character = ""
                    prevWord = 1
            if (GPIO.input(endMsgBut)):
                    word = word + CODE_reversed[character]
                    if (len(message) == 0):
                        message = word
                    else:
                        message = message +word
                    #print(message)
                    lcd.clear()
                    lcd.set_cursor(0,1)
                    lcd.message(message)
                    GPIO.output(led, GPIO.LOW)
                    time.sleep(2)
                    break
            if(GPIO.input(button) != prev):
                GPIO.output(led, GPIO.LOW)
                buttonPushedTime=time.time()-buttonUpTime
                if (buttonPushedTime>0.15):
                    character = character + "-"
                    lcd.clear()
                    lcd.set_cursor(0,1)
                    lcd.message(message + word)
                    lcd.home()
                    lcd.message(character)
                    #print("-")
                else:
                    character = character + "."
                    lcd.clear()
                    lcd.set_cursor(0,1)
                    lcd.message(message + word)
                    lcd.home()
                    lcd.message(character)
                    #print(".")
                buttonPushedTime=time.time()
                prev = 0
    morseText = morseText + "/"
    morseText.replace("//", "/")
    SendMsg(message, morseText);

def MorseTyped():
    character  = ""
    word = ""
    morseText = ""
    while(True):
        character = raw_input()
        if (character == " "):
            morseText = morseText + character + "/"
            word = word + " "
        else:
            word = word + CODE_reversed[character]
            word = word.replace("  ", " ")
            #print(word) 
            lcd.clear()
            lcd.message(character)
            lcd.set_cursor(0,1)
            lcd.message(word)
            morseText = morseText + character + ","
        if (len(character) == 0):
            break
        character = ""
    lcd.clear()
    lcd.message(word)
    time.sleep(2)
    morseText = morseText + "/"
    morseText.replace("//", "/")
    SendMsg(word, morseText)
        
def OldMorseTyped():
    morseText = ""
    character  = ""
    word = ""
    msg = ""
    #inputs = raw_input("Type Morse Code (','=next letter)('/' = next word):")
    inputs = ""
    while(True):
        char = raw_input()
        inputs= inputs + char
        morseText = morseText + char + ","
        lcd.clear()
        lcd.message(char)
        if (len(char) == 0):
            break
    inputs = inputs + "/"
    inputs.replace("//", "/")
    for i in inputs:
        if (i == "."):
            character = character + "."
        if (i =="-"):
            character = character + "-"
        if (i == ","):
            word = word + CODE_reversed[character]
            character = ""
        if (i == "/"):
            word = word + CODE_reversed[character]
            character = ""
            if (len(msg) == 0):
                msg=word
            else:
                msg = msg + " " + word
            word = ""
    #print(msg + " "+ word + character)
    print("Look back at the little screen")
    lcd.clear()
    lcd.message(msg + " " +word + character)
    time.sleep(2)
    SendMsg(msg + word + character, inputs)

def EnglishTyped():
    morseText = ""
    #message = raw_input("Type message:")
    message = ""
    while(True):
        char = raw_input()
        message= message + char
        lcd.clear()
        lcd.message(message)
        if (len(char) == 0):
            break
    upperMsg = message.upper()
    for i in upperMsg:
        #print(CODE[i])
        morseText = morseText +"," + CODE[i]
    print("Look back at the little screen")
    lcd.clear()
    lcd.message("Click button 1\nfor Morse Code")
    while(True):
        if (GPIO.input(restartBut)):
            for i in upperMsg:
                lcd.clear()
                lcd.message(CODE[i])
                time.sleep(1)
            break
    morseText = morseText.replace(" ","/") + "/"
    morseText = morseText.replace("/,","/")
    morseText = morseText[1:]
    SendMsg(message, morseText)


def PracticeMode(): #make these available for presentation
    #lcd.clear()
    #lcd.message("1 Enter Morse Cd\nUsing timer")
    #scrollLeft()
    #lcd.clear()
    #lcd.message("2 Enter Morse Cd\nUsing Keyboard")
    #scrollLeft()
    #lcd.clear()
    #lcd.message("3 Enter English\nUsing Keyboard")
    #scrollLeft()
    #lcd.clear()
    #lcd.message("4 Repeat Options")
    #scrollLeft()
    lcd.clear()
    lcd.message("1 timer 2 morsKB\n3 EngKB 4 IP")
    time.sleep(1)
    while(True):
        if (GPIO.input(restartBut)):
            lcd.clear()
            lcd.message("Good Luck")
            break
        if (GPIO.input(endMsgBut)):
            lcd.clear()
            lcd.message("Enter char\nIndividually")
            time.sleep(2)
            lcd.clear()
            lcd.message("Enter space\nfor next word")
            time.sleep(2)
            lcd.clear()
            lcd.message("When finished\nclick 'enter'")
            time.sleep(2)
            lcd.clear()
            lcd.message("Enter Morse\nCode")
            MorseTyped()
            break
        if (GPIO.input(nextWordBut)):
            lcd.clear()
            lcd.message("Enter char\nIndividually")
            time.sleep(2)
            lcd.clear()
            lcd.message("When Finished\nclick 'enter'")
            time.sleep(2)
            lcd.clear()
            lcd.message("Enter English\nmessage")
            EnglishTyped()
            break
        if (GPIO.input(nextCharBut)):
            my_ip = load(urlopen('http://jsonip.com'))['ip']
            lcd.clear()
            lcd.message(my_ip)
            time.sleep(4)
            break
    time.sleep(1)
        
def scrollLeft():
    time.sleep(3) #change back to 3 seconds
    for x in range(0, 16):
        lcd.move_left()
        time.sleep(.3) #change back to .1 seconds
    time.sleep(1)

def recieveMsgMode():
    client = MongoClient("ds161475.mlab.com", 61475)
    db = client.qpfallteam3
    db.authenticate("morsebot", "password")
    collection = db.MorseBot.find()
    for document in collection:
        eng = document['english']
        mors = document['morse']
    print (eng)
    print (mors)
    lcd.clear()
    lcd.message("View Message in\n1 Eng 2 Morse")
    while(True):
        if (GPIO.input(restartBut)):
            morseText = ""
            character  = ""
            word = ""
            msg = ""
            inputs = mors
            for i in inputs:
                if (i == "."):
                    character = character + "."
                if (i =="-"):
                    character = character + "-"
                if (i == ","):
                    word = word + CODE_reversed[character]
                    character = ""
                if (i == "/"):
                    word = word + CODE_reversed[character]
                    character = ""
                    if (len(msg) == 0):
                        msg=word
                    else:
                        msg = msg + " " + word
                    lcd.clear()
                    lcd.message(word)
                    time.sleep(1)
                    word = ""
            time.sleep(2)
            break
        if (GPIO.input(endMsgBut)):
            eng = eng.upper()
            for i in eng:
                lcd.clear()
                lcd.message(CODE[i])
                time.sleep(1)
            break

def SendMsg(eng, mors):
    #print(eng)
    #print(mors)
    lcd.clear()
    lcd.message("1 Send Message\n2 Sho Msg 3 Home")
    while (True):
        if (GPIO.input(restartBut)):
            client = MongoClient("ds161475.mlab.com", 61475)
            db = client.qpfallteam3
            db.authenticate("morsebot", "password")
            collection = db.MorseBot
            result = collection.insert_one({"morse":mors, "english":eng})
            lcd.clear()
            lcd.message("Message sent\n")
            break
        if (GPIO.input(endMsgBut)):
            temp = mors.replace(",", " ")
            temp = temp.replace("/", " ")
            lcd.clear()
            lcd.message(temp + "\n" +eng)
            scrollLeft()
            SendMsg(eng, mors)
            break
        if (GPIO.input(nextWordBut)):
            lcd.clear()
            lcd.message("Thanks for\nplaying")
            break
    time.sleep(1)

def SOSMode():
    client = MongoClient("ds161475.mlab.com", 61475)
    db = client.qpfallteam3
    db.authenticate("morsebot", "password")
    collection = db.MorseBot
    result = collection.insert_one({"morse":"...,---,.../", "english":"SOS"})
    lcd.clear()
    lcd.message("SOS HELP!!!")
    while (True):
        dit3(.25)
        if (GPIO.input(endMsgBut) or GPIO.input(restartBut) or GPIO.input(nextWordBut) or GPIO.input(nextCharBut)):
            break
        time.sleep(.25)
        dit3(.75)
        if (GPIO.input(endMsgBut) or GPIO.input(restartBut) or GPIO.input(nextWordBut) or GPIO.input(nextCharBut)):
            break
        time.sleep(.25)
        dit3(.25)
        if (GPIO.input(endMsgBut) or GPIO.input(restartBut) or GPIO.input(nextWordBut) or GPIO.input(nextCharBut)):
            break
        time.sleep(1)
    lcd.clear()
    lcd.message("Everything is\nawesome")
    time.sleep(1)

def dit3(unit):
    GPIO.output(led, GPIO.HIGH)
    time.sleep(unit)
    GPIO.output(led, GPIO.LOW)
    time.sleep(.2)
    GPIO.output(led, GPIO.HIGH)
    time.sleep(unit)
    GPIO.output(led, GPIO.LOW)
    time.sleep(.2)
    GPIO.output(led, GPIO.HIGH)
    time.sleep(unit)
    GPIO.output(led, GPIO.LOW)
    
#runtime
while (True):
    HomeDisplay()
    time.sleep(1)
    
            


