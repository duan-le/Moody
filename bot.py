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
   
    # Check for commands
    if message.content.startswith("#"):
        # Display all available commands
        if message.content.startswith("#commands"):
            reply = (
                "1. To learn more about what I do: " +
                "```#info```" +
                "2. To change the analyzed language: " +
                "```#lang <language>```"
            )
            await message.channel.send(reply)
        # Displays what the bot do
        elif message.content.startswith("#info"):
            reply = (
                "This bot helps to analyze text that is typed in discord, and notifies admins of any toxicity and/or profanity. When a user types anything toxic and/or profane, a message will be sent to the admins if it exceeds a toxicity rating of X%. If the user consistently types toxic and/or profane comments X times, there will be a message that appears in the chat visible to all." +
                "Settings that you can change for this bot include the language being analyzed, the level of toxicity that you want to be notified for, and the number of times a user is toxic before a message is sent to the public chat."
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
    else:
        response = service.comments().analyze(body=create_analyze_request(message.content)).execute()
        reply = "NLP RESULT\n"
        if response["attributeScores"]["TOXICITY"]["summaryScore"]["value"] >= 0.92 or response["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"] >= 0.87:
            reply += "I see the level of toxicity is getting to a staggeringly high point! Please be more mindful of others around you."
        elif response["attributeScores"]["PROFANITY"]["summaryScore"]["value"] >= 0.81:
            reply += "It looks like you are swearing just a bit too much! Please tone down the profanity!"
        reply += "```"
        for attribute in response["attributeScores"]:
            reply += attribute + ": " + str(response["attributeScores"][attribute]["summaryScore"]["value"]) + "\n"
        reply += "```"
        await message.channel.send(reply)

    # 0.81 for profanity
    # 0.87 for severe
    # 0.91 for toxic

client.run(DISCORD_BOT_TOKEN)