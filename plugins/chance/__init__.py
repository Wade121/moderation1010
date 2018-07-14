#!/usr/bin/python

import __main__
import random

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Chance'
    help_info['description'] = 'General chance functions. Roll a dice, flip a coin, choose something from a list or ask the magic 8 ball a question.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'coin'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = ''
    help_entry['description'] = 'Flip a coin'
    help_entry['perm_name'] = ''
    help_info[cmd_name].append(help_entry)

    cmd_name = 'dice'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'num_of_sides num_of_rolls'
    help_entry['description'] = 'Roll a dice. If you don\'t specify num_of_sides the default is 6, and if you don\'t specify num_of_rolls them then default is 1.'
    help_entry['perm_name'] = ''
    help_info[cmd_name].append(help_entry)

    cmd_name = 'choose'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'First option, Second option, Third option...'
    help_entry['description'] = 'Choose one option from a list of possibilities. Options can either be separated by commas or they can be single word options separated by spaces.'
    help_entry['perm_name'] = ''
    help_info[cmd_name].append(help_entry)

    cmd_name = '8ball'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'question'
    help_entry['description'] = 'Know the future! Consult with the magic 8 ball.'
    help_entry['perm_name'] = ''
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}
    '''
    this_perm = 'manage_plugins'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')
    '''
    return perm_info


async def server_setup_wizard():
    return True

#===================================================================================================================
#SERVER EVENTS

async def server_join(server): pass

async def server_remove(server): pass

async def server_update(before,after): pass

async def server_connected(server): pass

#===================================================================================================================
#MESSAGE EVENTS

async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)

    if(message.content.startswith(bot_cmd_char+'coin')):
        #Flip a coin
        coin_res = random.randrange(1,11)
        if(coin_res <= 5):
            coin_res = 'Heads'
        else:
            coin_res = 'Tails'
        await __main__.client.send_message(message.channel, 'Coin toss: '+coin_res)

    elif(message.content.startswith(bot_cmd_char+'dice')):
        #Roll dice
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)
        author_id = message.author.id

        use_max = 6;
        if(proc_msg_length >= 2):
            if(proc_msg[1] != None and proc_msg[1] != ""): use_max = int(proc_msg[1])
            if(use_max > 9999): use_max = 9999
            if(use_max < 2): use_max = 2

        num_of_dice = 1
        num_dice_txt = ""
        num_dice_end = ""

        if(proc_msg_length == 3):
            if(proc_msg[2] != None and proc_msg[2] != ""): num_of_dice = int(proc_msg[2])
            if(num_of_dice > 15): num_of_dice = 15

        if(num_of_dice > 1):
            num_dice_txt = str(num_of_dice)+" x "
            num_dice_end = "s"

        dice_results = ""
        dice_run = 1
        dice_total = 0
        while(dice_run <= num_of_dice):
            if(dice_results != ""): dice_results = dice_results+", "
            dice_roll = random.randrange(1,(use_max + 1))
            dice_total = dice_total + dice_roll
            dice_results = dice_results+str(dice_roll)
            dice_run = dice_run + 1

        if(num_of_dice > 1): dice_results = dice_results+" = "+str(dice_total)
        await __main__.client.send_message(message.channel,num_dice_txt+str(use_max)+" sided dice result"+num_dice_end+": **"+dice_results+"**")

    elif(message.content.startswith(bot_cmd_char+'choose')):
        #Choose option from a list
        proc_msg = await __main__.get_cmd_args(message.content,1)
        proc_msg = proc_msg[1]
        if("," in proc_msg):
            proc_msg = proc_msg.replace(", ",",")
            proc_msg = proc_msg.split(",")
        else:
            proc_msg = proc_msg.split(" ")

        proc_msg_length = len(proc_msg)
        if(proc_msg_length >= 2):
            choose_item = random.choice(proc_msg)
            await __main__.client.send_message(message.channel,'**I choose:** '+choose_item)
        else:
            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify two or more things for me to choose from.')

    elif(message.content.startswith(bot_cmd_char+'8ball')):
        #Shake the magic 8 ball
        proc_msg = await __main__.get_cmd_args(message.content,1)
        proc_msg_length = len(proc_msg)
        if(proc_msg_length >= 2):
            ball_results = []
            ball_results.append('It is certain')
            ball_results.append('It is decidedly so')
            ball_results.append('Without a doubt')
            ball_results.append('Yes definitely')
            ball_results.append('You may rely on it')
            ball_results.append('As I see it, yes')
            ball_results.append('Most likely')
            ball_results.append('Outlook good')
            ball_results.append('Yes')
            ball_results.append('Signs point to yes')
            #ball_results.append('Reply hazy, try again')
            #ball_results.append('Ask again later')
            #ball_results.append('I\'d better not tell you now')
            #ball_results.append('Cannot predict now')
            #ball_results.append('Concentrate and ask again')
            ball_results.append('Don\'t count on it')
            ball_results.append('My reply is no')
            ball_results.append('My sources say no')
            ball_results.append('Outlook not so good')
            ball_results.append('Very doubtful')
            choose_item = random.choice(ball_results)
            await __main__.client.send_message(message.channel,'<@'+message.author.id+'> shakes the magic 8 ball and asks "'+proc_msg[1]+'". The answer quickly becomes clear: **'+choose_item+'.**')
        else:
            await __main__.client.send_message(message.channel,'Since no question was asked of it, the magic 8 ball spent the time being shaken to contemplate <@'+message.author.id+'>\'s questionable life choices instead.')

async def message_new(message): pass

async def message_edit(before,after): pass

async def message_delete(message): pass

async def message_typing(channel,user,datestamp): pass

#===================================================================================================================
#MESSAGE REACTION EVENTS

async def reaction_add(reaction,user): pass

async def reaction_remove(reaction,user): pass

#===================================================================================================================
#CHANNEL EVENTS

async def channel_create(channel): pass

async def channel_delete(channel): pass

async def channel_update(before,after): pass

#===================================================================================================================
#MEMBER EVENTS

async def member_join(member): pass

async def member_remove(member): pass

async def member_update(before,after): pass

async def member_voice_update(before,after): pass

async def member_ban(member): pass

async def member_unban(server,user): pass

#===================================================================================================================
#ROLE EVENTS

async def role_create(role): pass

async def role_delete(role): pass

async def role_update(before,after): pass

#===================================================================================================================
#EMOJI LIST EVENTS

async def emoji_list_update(before,after): pass

#===================================================================================================================
#GROUP CHAT EVENTS

async def group_join(channel,user): pass

async def group_remove(channel,user): pass
