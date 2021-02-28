import json
import discord
import os
from googleapiclient import discovery

service = discovery.build("commentanalyzer", "v1alpha1", developerKey=PRESCRIPTIVE_API_KEY)

languages_dict = {
    "en": "english",
    # "es": "spanish",
    # "fr": "french",
    "de": "german",
    "pt": "portuguese",
    "it": "italian",
    "ru": "russian"
}
languages = ["en"]

def dict_to_string(my_dict):
    string = ""
    for key in my_dict:
        string += key + ": " + my_dict[key].capitalize() + "\n"
    return string

def create_analyze_request(message):
    global languages
    return {
        "comment": { 
            "text": message,
            "type": "PLAIN_TEXT"    
        },
        "requestedAttributes": {
            "TOXICITY": {},
            "SEVERE_TOXICITY": {},
            # "IDENTITY_ATTACK": {},
            # "INSULT": {},
            "PROFANITY": {},
            # "THREAT": {},
            # "SEXUALLY_EXPLICIT": {}
        },
        "languages": languages
    }

client = discord.Client()

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    global languages
   
    # Commands
    if message.content.startswith("#"):
        # Display all available commands
        if message.content.startswith("#help"):
            reply = (
            "1. To change the analyzed language: " +
            "```#lang <language>```"
            )
            await message.channel.send(reply)
        # Analysis language selection command 
        elif message.content.startswith("#lang"):
            arr = message.content.split()
            reply = "Invalid use of `#lang` command."
            if len(arr) == 2:
                lang = arr[1].lower()
                if lang in languages_dict:
                    languages = [lang]
                    reply = "Language is set to " + "`" + languages_dict[lang].capitalize() + "`."
                else:
                    languages_string = dict_to_string(languages_dict)
                    reply = "The language specified is not compatible. Please select from " + "```" + languages_string + "```"
            await message.channel.send(reply)
        else:
            reply = "That command does not exist."
            await message.channel.send(reply)
    # Analyze normal messages
    # else:
    #     response = service.comments().analyze(body=create_analyze_request(message.content)).execute()
    #     reply = "NLP RESULT\n```"
    #     for attribute in response["attributeScores"]:
    #         reply += attribute + ": " + str(response["attributeScores"][attribute]["summaryScore"]["value"]) + "\n"
    #     reply += "```"
    #     await message.channel.send(reply)

client.run(DISCORD_BOT_TOKEN)