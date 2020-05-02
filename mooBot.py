import discord
import time
import logging
import random
from bs4 import BeautifulSoup
from discord.utils import get
import urllib.request
import asyncio

logging.basicConfig(level=logging.INFO)

TOKEN = ''

client = discord.Client()

delimiter = ' '


def parse(string, delim):
    try:
        quoteString = string.split("\"")
        if quoteString[len(quoteString)-1] == '':
            del(quoteString[len(quoteString)-1])

        for i in range(1, len(quoteString)):
            if i%2 != 0:
                quoteString[i] = "\"" + quoteString[i]
                quoteString[i] += "\""

        #print(quoteString)

        splitString = []
        for i in range(0, len(quoteString)):
            if "\"" in quoteString[i]:
                splitString.append(quoteString[i])
            else:
                temp = quoteString[i].split(delim)
                for element in temp:
                    if element != '':
                        splitString.append(element)

        return splitString

    except ValueError as e:
        print("Caught empty delim exception, resetting to space")
        delimiter = ' '
        return parse(string, delimiter)


def mooCheck(string):
    if string[0].lower() == "moobot,":
        return string[1:]
    return False

##############################
# The actually important bit #
##############################

@client.event
async def on_message(message):
    global delimiter
    userRoleName = "botUser"
    adminRoleName = "botMaster"
    muteRoleName = "Sshhh"
    userRole = get(message.channel.guild.roles, name=userRoleName)
    adminRole = get(message.channel.guild.roles, name=adminRoleName)
    muteRole = get(message.channel.guild.roles, name=muteRoleName)

    msg = parse(message.content.lower(), delimiter)
    parsedMessage = mooCheck(msg)

    if message.author == client.user or not parsedMessage:  # checks if message is valid for response
        return
    else:
        # print("Got message")
        # print(parsedMessage[0])

        ########################
        #                      #
        # Admin-level commands #
        #                      #
        ########################

        if adminRole in message.author.roles:
            #print("botmaster message")  # Admin-level commands

            if parsedMessage[0] == "ban":  # obvious
                await message.channel.send("This command isn't implemented yet")
                print("Banned")
                return

            elif parsedMessage[0] == "unban":  # obvious
                await client.unban(message.server, parsedMessage[1])
                print("Unbanned")
                return

            elif parsedMessage[0] == "kick":  # obvious
                await client.kick(get(message.server.members, nick=parsedMessage[1]))
                print("Kicked")
                return

            elif parsedMessage[0] == "arise":  # Just for fun
                await message.channel.send("I LIVE!")
                return

            elif parsedMessage[0] == "sleep":
                await message.channel.send("Goodnight!")
                quit()

            elif parsedMessage[0] == "parse":
                print(parsedMessage)
                return

            elif parsedMessage[0] == "mute":
                #print(parsedMessage)
                for member in message.channel.guild.members: #iterates through all members, checking the string against usernames
                    if str(parsedMessage[1]).lower() in str(member.name).lower():
                        await member.add_roles(muteRole)
                        await message.channel.send(member.mention + ", you have been muted.")
                        return

                for member in message.channel.guild.members: #iterates through all members, checking the string against nicknames
                    if str(parsedMessage[1]).lower() in str(member.nick).lower():
                        await member.add_roles(muteRole)
                        await message.channel.send(member.mention + ", you have been muted.")
                        return

                await message.channel.send("invalid member!")
                return

            elif parsedMessage[0] == "unmute":
                for member in message.channel.guild.members:
                    #print(member.nick)
                    if str(parsedMessage[1]).lower() in str(member.name).lower():
                        await member.remove_roles(muteRole)
                        await message.channel.send(member.mention + ", you have been unmuted.")
                        return

                for member in message.server.members:
                    if str(parsedMessage[1]).lower() in str(member.nick).lower():
                        await member.remove_roles(muteRole)
                        await message.channel.send(member.mention + ", you have been unmuted.")
                        return

                await message.channel.send("invalid member!")
                return

                #await message.channel.send(get(message.server.members, nick=parsedMessage[1]) + ", you have been unmuted.")
                return

            elif parsedMessage[0] == "purge":
                if len(parsedMessage) > 1:
                    deleted = await message.channel.purge(limit=int(parsedMessage[1]), before=message.created_at)
                    await message.delete()
                    print("Deleted {} messages").format(len(deleted)+1)
                else:
                    def check(msg):
                        return msg.content == "Y" and msg.channel == message.channel

                    await message.channel.send("Are you sure you want to purge this *entire* channel of all messages?" +
                                               "(This action is irreversible!) (Y/N)")

                    try:
                        checkmsg = await client.wait_for('message', check=check, timeout=10)
                    except asyncio.TimeoutError:
                        await message.channel.send("Purge cancelled")
                    else:
                        deleted = await message.channel.purge(limit=None, before=message)
                        print("Deleted {} messages".format(len(deleted)))
                return

            ######################################################
            # Commands with multiple possibilities go below here #
            ######################################################

            elif parsedMessage[0] == "give":
                if parsedMessage[1] == "role":  # SYNTAX: Give role <role> <Nickname>
                    await client.add_roles(get(message.server.members, nick=parsedMessage[3]),
                                           get(message.server.roles, name=parsedMessage[2]))

                    print("Gave role " + str(get(message.server.roles, name=parsedMessage[2])) + " to " + str(
                        get(message.server.members, nick=parsedMessage[3])))

                    return

            elif parsedMessage[0] == "change":
                #print("got change command")
                if parsedMessage[1] == "delimiter":
                    await message.channel.send("Delimiter changed, use " + parsedMessage[
                        2] + " instead of " + delimiter + " now")
                    delimiter = parsedMessage[2]
                    return

        #####################################
        #                                   #
        # commands for anyone go below here #
        #                                   #
        #####################################

        if userRole in message.author.roles or adminRole in message.author.roles:
            print("botUser message")
            if parsedMessage[0] == "hello":
                await message.channel.send("Hello, " + message.author.mention)
                print("said hello")
                return

            elif parsedMessage[0] == "say":
                # print("Saying " + ' '.join(parsedMessage[1:]))
                await message.channel.send(' '.join(parsedMessage[1:]))
                print("said something")
                return

            ######################################################
            # commands with multiple possibilities go below here #
            ######################################################

            elif parsedMessage[0] == "get":
                print("Get request")
                if get(message.server.roles, name="botMaster") in message.author.roles:  # checks for botmaster commands
                    pass

                if parsedMessage[1] == "xkcd":
                    if len(parsedMessage) < 2:
                        num = random.randint(1, 2000)
                        parsedMessage.append(str(num))
                    print("getting xkcd " + parsedMessage[2])
                    page = urllib.request.urlopen("https://xkcd.com/" + parsedMessage[2])
                    xkcdSoup = BeautifulSoup(page, 'html.parser')
                    comic = parse(str(xkcdSoup.find(id='comic')), ' ')
                    print(comic)

                    embed = discord.Embed(title=comic[12])
                    embed.set_image(url="https:" + comic[10][1:][:-1])
                    print("https:" + comic[10])
                    embed.set_footer(text=comic[8])
                    await message.channel.send(embed=embed)
                    return

            elif parsedMessage[0] == "set":  # Syntax: set color 0xrrggbb name
                if parsedMessage[1] == "color":
                    colour = parsedMessage[2]
                    colorName = parsedMessage[2]
                    if(len(parsedMessage) == 4):
                        colorName = parsedMessage[3]
                    newRole = await client.create_role(message.server, name=colorName, colour=discord.Color(value=int(colour, 16)), mentionable=True)
                    await client.move_role(message.server, newRole, int(adminRole.position-6))
                    await client.add_roles(message.author, newRole)
                    await message.channel.send("Created new color")
                return

            else:  # Filter for unknown commands
                print("got unknown command")
                await message.channel.send("I don't know what that means!")
                return

        #############################
        #                           #
        # Auto-assigns botuser role #
        #                           #
        #############################

        else:
            print("other message")
            await client.add_roles(message.author, userRole)
            print("Gave role")
            await on_message(message)
            return


@client.event
async def on_ready():
    print("Logged in as " + client.user.name)
    print(client.user.id)
    print("----------")


client.run(TOKEN)
