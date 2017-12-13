from __future__ import print_function
import time
import json
import re
import urllib2
import csv
from datetime import datetime

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])


def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    print ("intent request -> ")
    print (intent_request)
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "getInfoIntent":
        return getInfo(intent, session)
    elif intent_name == "findMeetingRoomIntent":
        return findMeetingRoomIntent(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------


def get_welcome_response():
    session_attributes = {}
    card_title = "Pal-Assist"

    speech_output = "I am your Paypal assistant, my Name is Pal-Assist. How Can I help you ?"
    reprompt_text = "I did not hear that, please repeat."
    should_end_session = False
    return build_response_without_card(session_attributes, build_speechlet_response_without_card(
        card_title, speech_output, reprompt_text, should_end_session))




def getInfo(intent, session):
    session_attributes = {}
    card_title = "Get info"
   
    print ("intent is -->")
    print(intent)
   
    namelookup = intent['slots']['Info']['value'].lower()
    
 
    
    print ("namelookup is " + namelookup)
    
    name = str(namelookup)
    today = (time.strftime("%m/%d/%Y"))
    url = 'https://raw.githubusercontent.com/nerdanity/ReadCSV2/NonMaster/myMemory.csv'
    response = urllib2.urlopen(url)
    contents = csv.reader(response)
    records=[]
    element = ""
    summary =""
    daysstr=""
    speech_output =""
    reprompt_text=""
    
   #print ("the contents are -> " + contents)
   
    for row in contents:
        for element in row:
            print ("elements are->")
            print (element)
            if name in element.lower():
                title = row[0]
                description = row[1]
                dateTemp = row[2]
                date = dateTemp.strip()
                date_format = "%m/%d/%Y"
                
                print (dateTemp)
                print (date)
                if date == "" :
                    print ("Date was not required - "+ date )
                    summary = str(description)
                else: 
                    print ("Date was required, adding to speech " + date)
                    a = datetime.strptime(date, date_format)
                    print (a)
                    b = datetime.now()
                    print (b)
                    delta = abs(b - a)
                    numdays = delta.days
                    years = numdays/365
                    months = (numdays-365*years)/30
                    weeks = ((numdays-365*years)-(months*30))/7
                    days = (numdays-365*years)-(months*30)-(weeks*7)
                    
                    if days == 1:
                        daysstr=" Yesterday. "
                    elif days == 0 :
                        daysstr = " Today. "
                    else:
                        daysstr = str(days) + " days ago "
                        
                    #print (years + "-" + months + "-" + days )
                    summary = str(description) + " this was updated " + str(daysstr)
                
                records.append(summary)
                print("summary ->")
                print (summary)
              
            else:
                break
            
    temp1 = '. '.join(records)

    print ("records ->")
    print (records)
    
    if (name.lower() == "bye" or name.lower() == "thank you"):
        should_end_session = True
        speech_output = " Have a good Day. "
    else:
        should_end_session = False
        speech_output = str(temp1) + ". . What else do you want to ask ?"
        reprompt_text = "Could you repeat your request"

        

    print ("speech output ->")
    print(speech_output)
    return build_response(session_attributes, build_speechlet_response_without_card(
        card_title, speech_output, reprompt_text, should_end_session))


def findMeetingRoomIntent (intent, session):
    session_attributes = {}
    card_title = "Get Meeting Room"
  
    print ("intent is -->")
    print(intent)
    reprompt_text=""
    namelookup = intent['slots']['Building']['value'].lower()
    timelookup = intent['slots']['MeetTime']['value'].lower()
    
    lookupHour=int(0)
    lookupMin=int(0)
    
    
    if timelookup.isnumeric() :
       lookupHour = int(timelookup) / 100
       lookupMin = int(timelookup) % 100
       print ("i am in if")
    elif timelookup.lower() == "":
        lookupHour=int(time.strftime("%H")) - 8
        lookupMin=int(time.strftime("%M"))
        print ("i am in elif")
    else:
        lookupHour=int(time.strftime("%H")) - 8
        lookupMin=int(time.strftime("%M"))
        print ("i am in else")
        
    if lookupHour <= 5:
        lookupHour = lookupHour + 12
        
    print ("namelookup is " + namelookup)
    print ("timelookup is " + timelookup)
    
    name = str(namelookup)
    url = 'https://raw.githubusercontent.com/nerdanity/ReadCSV2/NonMaster/meetingRoom.csv'
    response = urllib2.urlopen(url)
    contents = csv.reader(response)
    records=[]
    element = ""
    summary =""
    daysstr=""
    speech_output =""
    columnOffset= int(3)
    lookupColumn = int(0)
    roomFound = int(0)
    building = str(namelookup)
    
    
    print ("nowHour is" + str(lookupHour))
    print ("nowMin is" + str(lookupMin))

    if  8 <= lookupHour <= 17:
        if lookupMin <30:
            lookupColumn = columnOffset + 2*(lookupHour-8)
        else:
            lookupColumn = columnOffset + 2*(lookupHour-8) + 1
        
        
        for row in contents:
            for element in row:
                print ("elements are->")
                print (element)
                if building in element.lower():
                    title = row[0]
                    description = row[1]
                    capacity = row[2]
                    availability = row[lookupColumn]
                    
                    if availability == "Y" :
                        #print ("Date was not required - "+ row )
                        summary = str(description) + " in building " + str(building) + " is available at" + str(lookupHour) +" " + str(lookupMin)
                        records.append(summary)
                        roomFound= int(1)
                        break
                
                
                        print("summary ->")
                        print (summary)
              
                else:
                    break
            if roomFound==1:
                break
    else:
        summary = "Most room at this hour should be free. I have data between 9 am to 5 pm"
        records.append(summary) 
        roomFound = int(1)
         
    print (summary)
    
    temp1 = '. '.join(records)
    
    print ("records ->")
    print (records)
    
    if (name.lower()=="bye" or name.lower() == "thank you"):
        should_end_session = True
    else:
        should_end_session = False
        
    speech_output = str(temp1) + ". . What else do you want to ask ?"
    reprompt_text = "Could you repeat your request"
    print ("speech output ->")
    print(speech_output)
    return build_response(session_attributes, build_speechlet_response_without_card(card_title, speech_output, reprompt_text, should_end_session))



def multiple_replace(dict, text):
    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dict[mo.string[mo.start():mo.end()]], text)

def signoff():
    session_attributes = {}
    card_title = "Signing off"
    speech_output = "This is your Pal-Assist signing off"
    should_end_session = True
    reprompt_text = ""
    return build_response(session_attributes, build_speechlet_response_without_card(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    card_title = "Session Ended"
    should_end_session = True
    speech_output = "Thank you for using  Pal-Assist."
    return build_response({}, build_speechlet_response_without_card(
        card_title, speech_output, None, should_end_session))


    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_speechlet_response_without_card(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
       'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
def build_response_without_card(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
