import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

load_dotenv()       # .env is used to hide our bots token

cluster = MongoClient('mongodb+srv://ASilva98:Grec1998@cppgameroom.h5j3d.mongodb.net/test')     # Connection to database
db = cluster['userData']        # The name of our database
collection = db['userData']

print('Current collections in database: ' + str(db.list_collection_names()))        # Print current collections in database

bot = commands.Bot(command_prefix = "/")        # The prefix used for commands understood by the bot

@bot.event       # Events are how our bot reacts with the server
async def on_ready():       # Displays a message in the terminal when the bot connects to our Discord server
    print(f'{bot.user} has connected to Discord!')

@bot.event       # This event displays a message when a new member joins our Discord server
async def on_member_join(member):       # on_member_join handles actions when a new member joins
    channel = bot.get_channel(988572875873214527)        # Channel ID grabbed from the Discord server
    await channel.send(f'Hi {member.name}, welcome to the CPP Game Room Discord server!')       # Display welcome message
    await channel.send('Be sure to type /help for a list of commands!')       # Display help message

@bot.command(description = 'Gives a list of available commands')
async def register(ctx):
    myCollection = db.users     # db.users is the collection where user data will be held
    discordTag = str(ctx.message.author)        # Store the discord tag of the user
    try:        # Try and find if the user has already been registered in the database
        discordTag_db = myCollection.find_one({'discord tag': discordTag})      # Retrieve the user's data (Dictionary)
        discordTag_db = discordTag_db.pop('discord tag')        # Pop the dictionary from 'discord tag'
        if discordTag == discordTag_db:
            await ctx.send('You have already registered!')
    except:     # If user does not exist then register the user
        await ctx.send('Enter your preferred name!')  # Bot's message

        name = await bot.wait_for('message', check=lambda message:      # Bot is waiting for a response.
        message.author == ctx.author and message.channel == ctx.channel)    # Ensures it is by the same user and in the same channel
        name = name.content     # Assign the content of the message to 'name'

        myCollection.insert_one(
            {'discord tag': discordTag,     # In the collection, create a document and insert their discord tag
             'preferred name': name})   # Also add their preferred name

        await ctx.send(f'Thanks for registering {name}!')   # Bot confirms registration by repeating their name

bot.run(os.getenv('TOKEN'))

