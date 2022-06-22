import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

load_dotenv()       # .env is used to hide our bots token

cluster = MongoClient('mongodb+srv://ASilva98:Grec1998@cppgameroom.h5j3d.mongodb.net/test')     # Connection to database
db = cluster['userData']
collection = db['userData']

bot = commands.Bot(command_prefix = "/")


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
    await ctx.respond('Enter your preferred name!')
    name = await bot.wait_for('message')
    await ctx.send(f'Thanks for registering {name}!')

bot.run(os.getenv('TOKEN'))

