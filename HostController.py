#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class

import speech_recognition as sr
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import argparse
import json
import serial
import csv
import sys
import threading
from queue import Queue
import random
from array import *
import datetime


# Global variables for threads

hasHeardStop = False
startTimeStamp = int(round(time.time()*1000))
stopTimeStamp = int(round(time.time()*1000))

# And one lambda to give random numbers

randomReading = lambda : random.randint(0,181)


# Custom MQTT message callback

def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Function for microphone listening thread to run

def listenForStopThread():
    global hasHeardStop
    global stopTimeStamp
    print()
    r = sr.Recognizer()
    stopSpeechString = ""
    while "stop" not in stopSpeechString:
        print("Say stop when you are finished")
        #time.sleep(1)
        try:
            with sr.Microphone() as source:
                audio = r.listen(source)
                stopSpeechString = r.recognize_google(audio)
                print("Google thinks you said: ")
                print(stopSpeechString)
        except :
            print("Google recognizer had to reset...trying again.")
        
    #after this point, stop has been said
    print("Stop has been heard!")
    stopTimeStamp = int(round(time.time()*1000))
    hasHeardStop = True



if __name__ == '__main__':

    #everything in this if block is guaranteed not to run by other threads

   

    try:
   
        AllowedActions = ['both', 'publish', 'subscribe']

    # Read in command-line parameters
        parser = argparse.ArgumentParser()
        parser.add_argument("-e", "--endpoint", action="store", dest="host", help="Your AWS IoT custom endpoint")
        parser.add_argument("-r", "--rootCA", action="store", dest="rootCAPath", help="Root CA file path")
        parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
        parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
        parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
        parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                        help="Use MQTT over WebSocket")
        parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                        help="Targeted client id")
        parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")
        parser.add_argument("-m", "--mode", action="store", dest="mode", default="publish",
                        help="Operation modes: %s"%str(AllowedActions))
        parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                        help="Message to publish")
                        
        


        #############################################################################
        # Change below items if you have different certificates/public-private keys #
        #############################################################################


        args = parser.parse_args()
        host = "arz1ewrp7tl0d-ats.iot.us-west-2.amazonaws.com"
        rootCAPath = "AmazonRootCA1.pem"
        certificatePath = "a8469447f4-certificate.pem.crt"
        privateKeyPath = "a8469447f4-private.pem.key"
        port = 8883
        useWebsocket = args.useWebsocket
        clientId = "robotArm"
        topic = "$aws/things/robot_arm_thing/shadow/update"

        if args.mode not in AllowedActions:
           parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
           exit(2)

        if args.useWebsocket and args.certificatePath and args.privateKeyPath:
            parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
            exit(2)

    #if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    #    parser.error("Missing credentials for authentication.")
    #    exit(2)

    # Port defaults
        if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
            port = 443
        if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
            port = 8883

    # Configure logging
        logger = logging.getLogger("AWSIoTPythonSDK.core")
        logger.setLevel(logging.DEBUG)
        streamHandler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)

    # Init AWSIoTMQTTClient
        myAWSIoTMQTTClient = None
        if useWebsocket:
            myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
            myAWSIoTMQTTClient.configureEndpoint(host, port)
            myAWSIoTMQTTClient.configureCredentials(rootCAPath)
        else:
            myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
            myAWSIoTMQTTClient.configureEndpoint(host, port)
            myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    # AWSIoTMQTTClient connection configuration
        myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
        myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
        myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
        myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect and subscribe to AWS IoT
        myAWSIoTMQTTClient.connect()
        if args.mode == 'both' or args.mode == 'subscribe':
            myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
            time.sleep(2)



        ###############################################
        # Below is added code (what isn't MQTT stuff) #
        ###############################################


        if args.mode == 'both' or args.mode == 'publish':

    
            usbport = '/dev/cu.usbmodem57033601'

            try:

                ############################################
                # Comment out these lines if not using USB # (for testing)
                ############################################
                try:
                    ser = serial.Serial(usbport, baudrate=115200)
                    ser.flushInput()
                    ser.close()
                    ser.open()
                except:
                    print("Serial Error! Is the USB cord plugged into the right port?")
                # Listen for start

                speechString = ""
                while "start" not in speechString:
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        print("Say start!")
                        try:
                            audio = r.listen(source)
                            speechString = r.recognize_google(audio)
                            print("Google thinks you said: ")
                            print(speechString)
                        except:
                            print("Hmmm...we couldn't quite catch that...")
                            print("Is your microphone working?")
                            time.sleep(1)
                
                # at this point, start has been said
                startTimeStamp = int(round(time.time()*1000))
                
                stopThread = threading.Thread(target = listenForStopThread)
                
                stopThread.start()
                numReadings = 0
                w, h = 5, 0;
                potentiometerReadings = [[0 for x in range(w)] for y in range(h)]
                while hasHeardStop == False:
                
                    ##################################################################
                    # If you're using random values for potentiometer readings,      #
                    # comment out all lines that include 'ser' and uncomment randoms #
                    ##################################################################
                    
                    ser_bytes = str(ser.readline()).replace('b\'','').split(',')
                    pot1 = ser_bytes[0] #clamp
                    pot2 = ser_bytes[1] #base
                    pot3 = ser_bytes[2] #hinge1
                    pot4 = ser_bytes[3] #hinge2
                    
                    #pot1 = randomReading()
                    #pot2 = randomReading()
                    #pot3 = randomReading()
                    #pot4 = randomReading()
                    
                    singleReading = [0 for x in range(w)]
                    singleReading[0] = time.time()*1000
                    singleReading[1] = pot1
                    singleReading[2] = pot2
                    singleReading[3] = pot3
                    singleReading[4] = pot4
                    potentiometerReadings.append(singleReading)
                    
                    numReadings += 1
                    time.sleep(.005)

                 
                
                stopThread.join()
                
                potentiometerDict = {}
                for i in  range(len(potentiometerReadings)):
                    potentiometerDict[i]=potentiometerReadings[i]
                
                now = datetime.datetime.now()
                duration = stopTimeStamp - startTimeStamp
                
                message = {'row': now.strftime("%Y-%m-%d %H:%M"), 'time': duration , 'state':{'reported':{'row': now.strftime("%Y-%m-%d %H:%M"), 'time': duration , 'state': potentiometerDict }}}
                
                
                
                messageJSON = json.dumps(message)
                #print("JSON message made:")
                #print()
                #print(messageJSON)
                
                
                #deleteMessage = {'state':{ 'desired':None, 'reported':None }}
                #deleteMessageJSON = json.dumps(deleteMessage)
                #myAWSIoTMQTTClient.publish(topic, deleteMessageJSON ,1)
                myAWSIoTMQTTClient.publish(topic, messageJSON, 1)
    
        
            except:
                print("Unexpected error:", sys.exc_info()[0])
                print("Unexpected error:", sys.exc_info()[1])
    ############################
    # End added section of IoT #
    ############################
    
    
    
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

# recognize speech using Google Cloud Speech
#GOOGLE_CLOUD_SPEECH_CREDENTIALS = r"""INSERT THE CONTENTS OF THE GOOGLE CLOUD SPEECH JSON CREDENTIALS FILE HERE"""
#try:
#    print("Google Cloud Speech thinks you said " + r.recognize_google_cloud(audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS))
#except sr.UnknownValueError:
#    print("Google Cloud Speech could not understand audio")
#except sr.RequestError as e:
#    print("Could not request results from Google Cloud Speech service; {0}".format(e))

# recognize speech using Wit.ai
#WIT_AI_KEY = "INSERT WIT.AI API KEY HERE"  # Wit.ai keys are 32-character uppercase alphanumeric strings
#try:
#    print("Wit.ai thinks you said " + r.recognize_wit(audio, key=WIT_AI_KEY))
#except sr.UnknownValueError:
#    print("Wit.ai could not understand audio")
#except sr.RequestError as e:
#    print("Could not request results from Wit.ai service; {0}".format(e))

# recognize speech using Microsoft Bing Voice Recognition
#BING_KEY = "INSERT BING API KEY HERE"  # Microsoft Bing Voice Recognition API keys 32-character lowercase hexadecimal strings
#try:
#    print("Microsoft Bing Voice Recognition thinks you said " + r.recognize_bing(audio, key=BING_KEY))
#except sr.UnknownValueError:
#    print("Microsoft Bing Voice Recognition could not understand audio")
#except sr.RequestError as e:
#    print("Could not request results from Microsoft Bing Voice Recognition service; {0}".format(e))

# recognize speech using Microsoft Azure Speech
#AZURE_SPEECH_KEY = "INSERT AZURE SPEECH API KEY HERE"  # Microsoft Speech API keys 32-character lowercase hexadecimal strings
#try:
#    print("Microsoft Azure Speech thinks you said " + r.recognize_azure(audio, key=AZURE_SPEECH_KEY))
#except sr.UnknownValueError:
#    print("Microsoft Azure Speech could not understand audio")
#except sr.RequestError as e:
#    print("Could not request results from Microsoft Azure Speech service; {0}".format(e))

# recognize speech using Houndify
#HOUNDIFY_CLIENT_ID = "INSERT HOUNDIFY CLIENT ID HERE"  # Houndify client IDs are Base64-encoded strings
#HOUNDIFY_CLIENT_KEY = "INSERT HOUNDIFY CLIENT KEY HERE"  # Houndify client keys are Base64-encoded strings
#try:
#    print("Houndify thinks you said " + r.recognize_houndify(audio, client_id=HOUNDIFY_CLIENT_ID, client_key=HOUNDIFY_CLIENT_KEY))
#except sr.UnknownValueError:
#    print("Houndify could not understand audio")
#except sr.RequestError as e:
#    print("Could not request results from Houndify service; {0}".format(e))

# recognize speech using IBM Speech to Text
#IBM_USERNAME = "INSERT IBM SPEECH TO TEXT USERNAME HERE"  # IBM Speech to Text usernames are strings of the form XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
#IBM_PASSWORD = "INSERT IBM SPEECH TO TEXT PASSWORD HERE"  # IBM Speech to Text passwords are mixed-case alphanumeric strings
#try:
#    print("IBM Speech to Text thinks you said " + r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD))
#except sr.UnknownValueError:
#    print("IBM Speech to Text could not understand audio")
#except sr.RequestError as e:
#    print("Could not request results from IBM Speech to Text service; {0}".format(e))
