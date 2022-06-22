import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

load_dotenv()       # .env is used to hide our bots token

cluster = MongoClient('mongodb+srv://ASilva98:EeF8bKFxMkBmSWLh@cppgameroom.h5j3d.mongodb.net/test')     # Connection to database
db = cluster['userData']        # The name of our database
collection = db['userData']

print('Current collections in database: ' + str(db.list_collection_names()))        # Print current collections in database

bot = commands.Bot(command_prefix = "/")        # The prefix used for commands understood by the bot

@bot.event                  # Events are how our bot reacts with the server
async def on_ready():       # Displays a message in the terminal when the bot connects to our Discord server
    print(f'{bot.user} has connected to Discord!')

@bot.event       # This event displays a message when a new member joins our Discord server
async def on_member_join(member):                       # on_member_join handles actions when a new member joins
    channel = bot.get_channel(988572875873214527)       # Channel ID grabbed from the Discord server
    await channel.send(f'Hi {member.name}, welcome to the CPP Game Room Discord server!')       # Display welcome message
    await channel.send('Be sure to type /help for a list of commands!')                         # Display help message

@bot.command(description = 'Register a users preferred name')       # This command will register a user's preferred name
async def register(ctx):                        # Command is /register
    myCollection = db.users                     # db.users is the collection where user data will be held
    discordTag = str(ctx.message.author)        # Store the discord tag of the user

    try:        # Try and find if the user has already been registered in the database
        discordTag_db = myCollection.find_one({'discord tag': discordTag})      # Retrieve the user's data (Dictionary)
        discordTag_db = discordTag_db.pop('discord tag')                        # Pop the dictionary from 'discord tag'
        if discordTag == discordTag_db:
            await ctx.send('You have already registered!')

    except:     # If user does not exist then register the user
        await ctx.send('Enter your preferred name!')                        # Bot's message

        name = await bot.wait_for('message', check=lambda message:          # Bot is waiting for a response.
            message.author == ctx.author and message.channel == ctx.channel)    # Ensures it is by the same user and in the same channel
        name = name.content     # Assign the content of the message to 'name'.

        myCollection.insert_one(
            {'discord tag': discordTag,     # In the collection, create a document and insert their discord tag.
             'preferred name': name,
             'games': []})       # Also add their preferred name.

        await ctx.send(f'Thanks for registering {name}!')               # Bot confirms registration by repeating their name.

@bot.command(description = 'Display a list of games available')         # This command will display a list of games.
async def gameList(ctx):        # Command is /gameList
    await ctx.send("Here's our list of games:\n")

    gameCollection = db.gameList          # db.gameList is the collection where the game list is held.
    cursor = gameCollection.find({})      # Querying multiple documents returns a cursor that points to multiple documents

    for document in cursor:             # Loop through the document.
        game = document.pop('game')     # Pop the game field of each document.
        await ctx.send(game)            # Display the game.

@bot.command(description = 'Add a game to a users game list')       # This command will add a game to a user's game list.
async def addGame(ctx):                         # Command is /addGame.
    userCollection = db.users                   # db.users is the collection where user data will be held.
    discordTag = str(ctx.message.author)        # Store the discord tag of the user.

    try:        # Try and find if the user is already registered
        discordTag_db = userCollection.find_one({'discord tag': discordTag})        # Retrieve the user's data (Document).
        discordTag_db = discordTag_db.pop('discord tag')                            # Pop the discord tag from the document.
        if discordTag == discordTag_db:         # If the message author's discord tag matches one in the database.
            await ctx.send('What game would you like to add?')

            game = await bot.wait_for('message', check=lambda message:  # Bot is waiting for a response.
                message.author == ctx.author and message.channel == ctx.channel)
            game = game.content     # Assign the content of the message to game.
            game = game.lower()     # Make the string lowercase.

            gameCollection = db.gameList            # Retrieve the gameList database.
            cursor = gameCollection.find({})        # Query all the documents in the collection.

            for document in cursor:                 # Loop through the cursor.
                game_db = document.pop('game')      # Pop the game from the document.
                gameLower = game_db.lower()         # Make the game lowercase, and assign to new string to avoid altering original string.

                if game == gameLower:               # If the user inputted game matches one in the database
                    filterVals = {'discord tag': discordTag}        # Filter through the discord tags in the collection and find a match.
                    newVals = {"$push": {'games': game_db}}         # Append the user's game list array.
                    userCollection.update_one(filterVals, newVals)  # Update the document.

                    await ctx.send(f'Successfully added {game_db}, to your list of games!')
                    invalid = False     # If there is a match, set invalid to false.
                    break               # Break if there is a match.

                else:
                    invalid = True      # If there is no match, set invalid to true and continue loop.

            if invalid == True:         # If there was no match, send the user an error message.
                await ctx.send('You entered an invalid game, try again!')
        return

    except:     # If the user is not registered, send the user an error message.
        await ctx.send("You aren't registered!")

@bot.command(description = 'Display a list of skill levels available')
async def skillList(ctx):
    await ctx.send("Here's the list of skill levels:\n"
                   "Casual\n"
                   "Beginner\n"
                   "Intermediate\n"
                   "Expert")

@bot.command(description = 'Allows a user to add a skill to a game in their list')
async def addSkill(ctx):
    userCollection = db.users                   # db.users is the collection where user data will be held.
    discordTag = str(ctx.message.author)        # Store the discord tag of the user.

    try:        # Try and find if the user is already registered
        discordTag_db = userCollection.find_one({'discord tag': discordTag})        # Retrieve the user's data (Document).
        discordTag_db = discordTag_db.pop('discord tag')                            # Pop the discord tag from the document.
        if discordTag == discordTag_db:         # If the message author's discord tag matches one in the database.
            await ctx.send('What game would you like to add your skill to?')
            game = await bot.wait_for('message', check=lambda message:  # Bot is waiting for a response.
                    message.author == ctx.author and message.channel == ctx.channel)
            game = game.content  # Assign the content of the message to game.
            game = game.lower()  # Make the string lowercase.

            userGames = userCollection.find_one({'discord tag': discordTag})        # Query the discord tag of the message author.
            userGames = userGames.pop('games')          # Pop the games field.
            while len(userGames) > 0:                   # Loop until the list is empty.
                poppedGame = userGames.pop()            # Pop the game from the user's list.
                lowerPoppedGame = poppedGame.lower()    # Make the string lowercase.
                if game == lowerPoppedGame:             # If the game the user input is a match, set match to true.
                    match = True
                else:
                    match = False                       # If the game the user input is not a match, set match to false.

            if match == True:
                await ctx.send("Test Pass")
            else:       # Send the user an error message.
                await ctx.send("You're trying to add a skill for a game you don't have added!")

        return
    except:     # If the user is not registered, send the user an error message.
        await ctx.send("You aren't registered!")

bot.run(os.getenv('TOKEN'))
