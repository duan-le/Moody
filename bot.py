import json
import discord
import os
import pymongo
from googleapiclient import discovery
from collections import Counter

mongo_client = pymongo.MongoClient(os.getenv("MONGO_DB_KEY"))
my_db = mongo_client["Servers"]

DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
PERSPECTIVE_API_KEY = os.getenv('PERSPECTIVE_API_KEY')
service = discovery.build("commentanalyzer", "v1alpha1", developerKey=PERSPECTIVE_API_KEY)

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

def get_violations_list(my_col):
    string = "```"
    for user in my_col.find():
        string += str(user["username"]) + " - " + str(user["violations"]) + " time(s)\n"
    string += "```"
    return string
    
client = discord.Client()
profane_users = "/"
# Default values are:
#   0.81 for profanity
#   0.87 for severe
#   0.91 for toxic
profanity_index = 0.81
severe_toxicity_index = 0.87
toxicity_index = 0.91

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    for server in client.guilds:
        await server.text_channels[0].send("Moody is online! Type `#commands` to start.")
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    global languages
    global profanity_index
    global severe_toxicity_index
    global toxicity_index
   
    # Check for commands
    if message.content.startswith("#"):
        # Display all available commands
        if message.content.startswith("#commands"):
            reply = (
                "1. To learn more about what I do: " +
                "```#info```" +
                "2. To change the analyzed language: " +
                "```#lang <language>```"
                "3. To view the current list of members who have violations (*admin only*): " +
                "```#rep```"
                "4. To view the current value of profanity allowed: " +
                "```#prof```"
                "5. To view the current value of severe profanity allowed: " +
                "```#sev```"
                "6. To view the current value of toxicity allowed: " +
                "```#tox```"
                "7. To change the current value of profanity allowed (*admin only*): " +
                "```#prof_ch```"
                "8. To change the current value of severe profanity allowed (*admin only*): " +
                "```#sev_ch```"
                "9. To change the current value of toxicity allowed (*admin only*): " +
                "```#tox_ch```"
            )
            await message.channel.send(reply)
        # Displays what the bot do
        elif message.content.startswith("#info"):
            reply = "This bot helps to analyze messages in discord, and take actions if there is presence of toxicity and/or profanity."
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
        elif message.content.startswith("#rep"):
            if message.author.top_role.permissions.administrator:
                my_col = my_db[str(message.guild.id)]
                if my_col.find().count() < 1:
                    reply = "No user is recorded in the profanity list."
                else:
                    reply = "Users and their violation frequencies:\n"
                    reply += get_violations_list(my_db[str(message.guild.id)])
            else:
                reply = "You are not an admin."
            await message.channel.send(reply)
        #DO NOT CHANGE THE ORDER OF THE FOLLOWING
        elif message.content.startswith("#prof_ch"):
            if message.author.top_role.permissions.administrator:
                arr = message.content.split()
                reply = "Invalid use of `#prof_ch` command."
                if len(arr) == 2:
                    new_index = float(arr[1])
                    if new_index >= 0.0 and new_index <= 1.0:
                        profanity_index = new_index
                        reply = "The profanity threshold is: " + "{:.0%}".format(profanity_index)
                    else:
                        reply = "The profanity threshold must be between `0` and `1`."
            else:
                reply = "You are not an admin."
            await message.channel.send(reply)
        elif message.content.startswith("#sev_ch"):
            if message.author.top_role.permissions.administrator:
                arr = message.content.split()
                reply = "Invalid use of `#sev_ch` command."
                if len(arr) == 2:
                    new_index = float(arr[1])
                    if new_index >= 0.0 and new_index <= 1.0:
                        severe_toxicity_index = new_index
                        reply = "The severe toxicity threshold is: " + "{:.0%}".format(severe_toxicity_index)
                    else:
                        reply = "The severe toxicity threshold must be between `0` and `1`."
            else:
                reply = "You are not an admin."
            await message.channel.send(reply)
        elif message.content.startswith("#tox_ch"):
            if message.author.top_role.permissions.administrator:
                arr = message.content.split()
                reply = "Invalid use of `#tox_ch` command."
                if len(arr) == 2:
                    new_index = float(arr[1])
                    if new_index >= 0.0 and new_index <= 1.0:
                        toxicity_index = new_index
                        reply = "The toxicity threshold is: " + "{:.0%}".format(toxicity_index)
                    else:
                        reply = "The toxicity threshold must be between `0` and `1`."
            else:
                reply = "You are not an admin."
            await message.channel.send(reply)
        elif message.content.startswith("#prof"):
            await message.channel.send("The profanity threshold is: " + "{:.0%}".format(profanity_index))
        elif message.content.startswith("#sev"):
            await message.channel.send("The severe toxicity threshold is: " + "{:.0%}".format(severe_toxicity_index))
        elif message.content.startswith("#tox"):
            await message.channel.send("The toxicity threshold is: " + "{:.0%}".format(toxicity_index))
        else:
            reply = "That command does not exist."
            reply += " To view the commands available, type:\n"
            reply += "```#commands```"
            await message.channel.send(reply)
    # Analyze normal messages
    else:
        response = service.comments().analyze(body=create_analyze_request(message.content)).execute()
        reply = ""
        my_col = my_db[str(message.guild.id)]
        if response["attributeScores"]["TOXICITY"]["summaryScore"]["value"] >= toxicity_index or response["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"] >= severe_toxicity_index:
            await message.delete()
            reply += message.author.mention
            reply += ", your last message was removed for being toxic! Please be nicer and be more mindful of others around you."
            if (my_col.find({"userid": message.author.id}).count() > 0):
                my_col.update_one({"userid": message.author.id}, {"$inc": {"violations": 1}})
            else:
                my_col.insert_one({"username": message.author.name, "userid": message.author.id, "violations": 1});
        elif response["attributeScores"]["PROFANITY"]["summaryScore"]["value"] >= profanity_index:
            await message.delete()
            reply += message.author.mention
            reply += ", your last message was removed for being profane! Please tone down the profanity!"
            if (my_col.find({"userid": message.author.id}).count() > 0):
                my_col.update_one({"userid": message.author.id}, {"$inc": {"violations": 1}})
            else:
                my_col.insert_one({"username": message.author.name, "userid": message.author.id, "violations": 1});
        if (reply != ""):
            await message.channel.send(reply)

client.run(DISCORD_BOT_TOKEN)