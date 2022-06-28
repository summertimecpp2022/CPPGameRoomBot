import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

load_dotenv()       # .env is used to hide our bots token

cluster = MongoClient('mongodb+srv://ASilva98:' + os.getenv('mongodb_password') + '@cppgameroom.h5j3d.mongodb.net/test')     # Connection to database
db = cluster['userData']        # The name of our database
collection = db['userData']

print('Current collections in database: ' + str(db.list_collection_names()))        # Print current collections in database

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix = "/", intents = intents)        # The prefix used for commands understood by the bot

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
                    newVals = {"$addToSet": {'games': game_db}}         # Append the user's game list array.
                    userCollection.update_one(filterVals, newVals)  # Update the document.

                    await ctx.send(f'Successfully added {game_db} to your list of games!')
                    invalid = False     # If there is a match, set invalid to false.
                    break               # Break if there is a match.

                else:
                    invalid = True      # If there is no match, set invalid to true and continue loop.

            if invalid == True:         # If there was no match, send the user an error message.
                await ctx.send('You entered an invalid game, try again!')
        return

    except:     # ERROR: The user cannot be found in the database.
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
            game = game.content                 # Assign the content of the message to game.
            game = game.lower()                 # Make the string lowercase.

            userGames = userCollection.find_one({'discord tag': discordTag})        # Query the discord tag of the message author.
            userGames = userGames.pop('games')          # Pop the games field.

            while len(userGames) > 0:                   # Loop until the list is empty.
                poppedGame = userGames.pop()            # Pop the game from the user's list.
                lowerPoppedGame = poppedGame.lower()    # Make the string lowercase.
                if game == lowerPoppedGame:             # If the game the user input is a match, set match to true.
                    match = True
                    break
                else:
                    match = False                       # If the game the user input is not a match, set match to false.

            if match == True:
                await ctx.send("What skill level would you like to add?")

                skill = await bot.wait_for('message', check=lambda message:  # Bot is waiting for a response.
                    message.author == ctx.author and message.channel == ctx.channel)
                skill = skill.content                   # Assign the content of the message to game.
                skill = skill.lower()                   # Make the string lowercase.


                skillCollection = db.skillList                          # Retrieve the skillList database.
                cursor = skillCollection.find({})                       # Query all the documents in the collection.

                for document in cursor:                                 # Loop through the cursor.
                    skill_db = document.pop('skill')                    # Pop the skill from the document.
                    skillLower = skill_db.lower()                       # Make the skill lowercase, and assign to new string to avoid altering original string.

                    if skill == skillLower:                             # If the user inputted skill matches one in the database
                        filterVals = {'discord tag': discordTag}        # Filter through the discord tags in the collection and find a match.
                        newVals = {"$addToSet": {'skill': {poppedGame: skill_db}}}  # Add a new field named 'skill' to the database. Append with the game and skill level.
                        userCollection.update_one(filterVals, newVals)  # Update the document.
                        await ctx.send(f'Successfully added {skill_db} to your list of games!')
                        invalid = False                                 # If false then skill add was a success
                        break

                    else:
                        invalid = True                                  # If true then skill add was a failure

                if invalid == True:     # If there was input error, send the user an error message.
                    await ctx.send('You entered an invalid skill level, try again!')

            else:                       # Send the user an error message.
                await ctx.send("You're trying to add a skill for a game you don't have added!")
            return
        return
    except:                             # ERROR:
        await ctx.send("You aren't registered!")

@bot.command(description = 'Display a list of times availability in the game room')
async def timeList(ctx):
    await ctx.send("Here's the list of time availability in the game room:\n"
                   "Monday (Morning, Afternoon, Evening)\n"
                   "Tuesday (Morning, Afternoon, Evening)\n"
                   "Wednesday (Morning, Afternoon, Evening)\n"
                   "Thursday (Morning, Afternoon, Evening)\n"
                   "Friday (Morning, Afternoon, Evening)\n"
                   "Saturday (Morning, Afternoon, Evening)")

@bot.command(description = 'Allows a user to add a time availability to their account')
async def addTime(ctx):
    userCollection = db.users                   # db.users is the collection where user data will be held.
    discordTag = str(ctx.message.author)        # Store the discord tag of the user.

    try:        # Try and find if the user is already registered
        discordTag_db = userCollection.find_one({'discord tag': discordTag})        # Retrieve the user's data (Document).
        discordTag_db = discordTag_db.pop('discord tag')                            # Pop the discord tag from the document.

        await ctx.send('What day would you like to add availability for?')
        day = await bot.wait_for('message', check=lambda message:  # Bot is waiting for a response.
                message.author == ctx.author and message.channel == ctx.channel)
        day = day.content
        day = day.lower()
        dayFound = False
        timeFound = False

        timeCollection = db.timeList                # Retrieve the timeList database.
        cursor = timeCollection.find({})            # Query all the documents in the collection.

        for document in cursor:                     # Loop through the cursor.
            day_db = document.pop('day')            # Pop the day from the document.
            dayLower = day_db.lower()               # Make the day lowercase, and assign to new string to avoid altering original string.

            if day == dayLower:                     # If the user input matches a day in the database, set to true.
                dayFound = True
                break                               # Exit loop if found

            else:
                dayFound = False                    # If the user input doesn't match a day, continue loop and set to false
        if dayFound == False:                       # If the user input doesn't match, display error and return from command.
            await ctx.send('Your input was invalid! Use the /timeList command to see the day and time availability')
            return

        timeCollection = db.timeList                # Retrieve the timeList database.
        cursor = timeCollection.find({'day': day})            # Query all the documents in the collection.

        await ctx.send('What time would you like to add availability for?')

        time = await bot.wait_for('message', check=lambda message:  # Bot is waiting for a response.
                message.author == ctx.author and message.channel == ctx.channel)
        time = time.content
        time = time.lower()

        for document in cursor:                 # Loop through the cursor and pop the times
            time_db = document.pop('time')

        timeLength = len(time_db)               # Get the length of the time_db list

        try:                                    # Try and pop through the list to find a match
            while timeLength >= 0:              # While timeLength is >= 0, continue to pop.
                if time == time_db.pop():       # If time equals to a pop, set timeFound to True
                    timeFound = True
                    break                       # Break out of loop if found

        except:                                 # ERROR: No more elements to pop, therefore there was an input error.
            await ctx.send('Your input was invalid! Use the /timeList command to see the day and time availability')
            return

        filterVals = {'discord tag': discordTag}                            # Filter through the discord tags in the collection and find a match.
        newVals = {'$addToSet': {'availability': {day: {'time': time}}}}    # Add to the availability array. If it does not exist, create one. Add day and time to the array.
        userCollection.update_one(filterVals, newVals)                      # Update the document.

        await ctx.send(f'Successfully added the {time} to your {day} availability!')


    except:                             # ERROR: The user cannot be found in the database.
        await ctx.send("You aren't registered!")

bot.run(os.getenv('TOKEN'))