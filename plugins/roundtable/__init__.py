#!/usr/bin/python

import __main__

global roundtable_queues
roundtable_queues = {}

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Roundtable'
    help_info['description'] = 'Mediates discussion in particular channels.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'set'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'roundtable_inactivity_skip_time'
    help_entry['args'] = 'time_int time_scale'
    help_entry['description'] = 'Sets the time limit for inactivity before the active members turn is skipped.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'roundtable_cooldown_time'
    help_entry['args'] = 'time_int time_scale'
    help_entry['description'] = 'Sets the amount of time cooldown lasts before a member can rejoin a discussion.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)



    cmd_name = 'roundtable'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'on'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Activates roundtable mode on channel_name, if the channel isn\'t specified the current one is used.'
    help_entry['perm_name'] = 'enable_roundtable'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'off'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Deactivates roundtable mode on channel_name, if the channel isn\'t specified the current one is used.'
    help_entry['perm_name'] = 'enable_roundtable'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'skip'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Skips to the next member in the queue in channel_name, if the channel isn\'t specified the current one is used.'
    help_entry['perm_name'] = 'moderate_discussions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'cooldown'
    help_entry['args'] = 'channel_name member_name ejection_reason'
    help_entry['description'] = 'Ejects member_name from the discussion in channel_name and puts them into cooldown.'
    help_entry['perm_name'] = 'moderate_discussions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'eject'
    help_entry['args'] = 'channel_name member_name ejection_reason'
    help_entry['description'] = 'Ejects member_name from the discussion in channel_name.'
    help_entry['perm_name'] = 'moderate_discussions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'interject'
    help_entry['args'] = 'channel_name message_text'
    help_entry['description'] = 'Posts a moderators message into the discussion in channel_name, bypassing the queue.'
    help_entry['perm_name'] = 'moderate_discussions'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'roundtable_continued'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'join'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Joins the discussion in channel_name, if the channel isn\'t specified the current one is used.'
    help_entry['perm_name'] = 'join_discussions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'leave'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Leaves the discussion in channel_name, if the channel isn\'t specified the current one is used.'
    help_entry['perm_name'] = 'join_discussions'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'change_settings'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')

    this_perm = 'enable_roundtable'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')

    this_perm = 'moderate_discussions'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')

    this_perm = 'join_discussions'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('members')

    return perm_info


async def server_setup_wizard():
    return True

#===================================================================================================================
#SERVER EVENTS

async def server_join(server): pass

async def server_remove(server): pass

async def server_update(before,after): pass

async def server_connected(server):
    if(server.id not in roundtable_queues): roundtable_queues[server.id] = {}
    
    roundtable_channels = await __main__.get_config('roundtable_channels',server,'roundtable')
    if(roundtable_channels == False): roundtable_channels = {}
    for key,value in roundtable_channels.items():
        if(key not in roundtable_queues[server.id]):
            roundtable_queues[server.id][key] = {}
            roundtable_queues[server.id][key]['queue'] = []
            roundtable_queues[server.id][key]['cooldown'] = []
            roundtable_queues[server.id][key]['active_user'] = None
            roundtable_queues[server.id][key]['active_on'] = None
            roundtable_queues[server.id][key]['active_user_typing'] = None
            roundtable_queues[server.id][key]['discussion_active'] = False

#===================================================================================================================
#MESSAGE EVENTS

async def check_skip_inactive_user(server_obj,chk_data):
    channel_obj = chk_data['channel']
    if(channel_obj.id in roundtable_queues[server_obj.id]):
        if(roundtable_queues[server_obj.id][channel_obj.id]['active_user'] == chk_data['user_id']):
            if(roundtable_queues[server_obj.id][channel_obj.id]['active_on'] == chk_data['active_on']):
                if(roundtable_queues[server_obj.id][channel_obj.id]['active_user_typing'] == None):
                    await __main__.client.send_message(channel_obj,'Skipping <@'+chk_data['user_id']+'>\'s turn due to inactivity')
                    await skip_to_next_turn(server_obj,channel_obj)


        

async def check_active_seen_typing(server_obj,channel_obj,user_id):
    if(channel_obj.id in roundtable_queues[server_obj.id]):
        if(roundtable_queues[server_obj.id][channel_obj.id]['active_user'] == user_id):
            roundtable_queues[server_obj.id][channel_obj.id]['active_user_typing'] = await __main__.current_timestamp()

async def next_user_in_queue(current_user_id,queue_list):
    next_user_id = None
    found_this_user = False
    for user_entry in queue_list:
        if(user_entry == current_user_id):
            found_this_user = True
        else:
            if(found_this_user == True):
                next_user_id = user_entry
                break
    if(found_this_user == True and next_user_id == None and len(queue_list) > 1): next_user_id = queue_list[0]
    if(next_user_id == current_user_id): next_user_id = None
    return next_user_id


async def set_active_turn(server_obj,channel_obj,user_id):
    set_active_on = await __main__.current_timestamp()
    roundtable_queues[server_obj.id][channel_obj.id]['active_user'] = user_id
    roundtable_queues[server_obj.id][channel_obj.id]['active_on'] = set_active_on
    roundtable_queues[server_obj.id][channel_obj.id]['active_user_typing'] = None
    roundtable_queues[server_obj.id][channel_obj.id]['discussion_active'] = True
    next_user_id = await next_user_in_queue(user_id,roundtable_queues[server_obj.id][channel_obj.id]['queue'])

    announce_turn_text = 'It is now <@'+str(user_id)+'>\'s turn to speak'
    if(next_user_id != None):
        announce_turn_text = announce_turn_text+', it will be <@'+str(next_user_id)+'>\'s turn next.'
    else: announce_turn_text = announce_turn_text+'.'
    await __main__.client.send_message(channel_obj,announce_turn_text)

    inactivity_time = await __main__.get_config('roundtable_inactivity_skip_time',server_obj,'roundtable')
    if(inactivity_time == False): inactivity_time = 120
    trig_time = await __main__.current_timestamp() + inactivity_time
    trig_args = {}
    trig_args['user_id'] = user_id
    trig_args['active_on'] = set_active_on
    trig_args['channel'] = channel_obj
    await __main__.add_task(server_obj,trig_time,'roundtable','check_skip_inactive_user',trig_args)


async def skip_to_next_turn(server_obj,channel_obj):
    next_user_id = None
    if(channel_obj.id in roundtable_queues[server_obj.id]):
        current_user_id = roundtable_queues[server_obj.id][channel_obj.id]['active_user']

        if(current_user_id != None):
            next_user_id = await next_user_in_queue(current_user_id,roundtable_queues[server_obj.id][channel_obj.id]['queue'])
        else:
            if(len(roundtable_queues[server_obj.id][channel_obj.id]['queue']) == 1 and roundtable_queues[server_obj.id][channel_obj.id]['queue'][0] != current_user_id):
                next_user_id = roundtable_queues[server_obj.id][channel_obj.id]['queue'][0]

        if(next_user_id != None): await set_active_turn(server_obj,channel_obj,next_user_id)
    return next_user_id

    


async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)
    if(message.content.startswith(bot_cmd_char+'set')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)


        if(proc_msg[1] == "roundtable_cooldown_time"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','change_settings',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 4):
                    add_time = await __main__.cmd_time_args(proc_msg[2],proc_msg[3])
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, the round table cooldown time has been set to '+str(proc_msg[2])+' '+str(proc_msg[3])+'.')
                    await __main__.set_config('roundtable_cooldown_time',message.server,'roundtable',add_time)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the length of time people are in cooldown for.')


        if(proc_msg[1] == "roundtable_inactivity_skip_time"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','change_settings',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 4):
                    add_time = await __main__.cmd_time_args(proc_msg[2],proc_msg[3])
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, the round table inactivity skip time has been set to '+str(proc_msg[2])+' '+str(proc_msg[3])+'.')
                    await __main__.set_config('roundtable_inactivity_skip_time',message.server,'roundtable',add_time)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the length of time to wait for someone to start typing before they are skipped in the queue.')



    if(message.content.startswith(bot_cmd_char+'roundtable')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)


        if(proc_msg[1] == "on"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','enable_roundtable',True)
            if(chk_user_perm == True):

                if(proc_msg_length == 2):
                    get_channel_arg = '<#'+str(message.channel.id)+'>'
                else: get_channel_arg = proc_msg[2]
                on_channel = await __main__.find_channel_arg(message.server,get_channel_arg,True)
                if(on_channel != False):

                    roundtable_channels = await __main__.get_config('roundtable_channels',message.server,'roundtable')
                    if(roundtable_channels == False): roundtable_channels = {}
                    if(on_channel.id not in roundtable_channels):
                        roundtable_details = {}

                        activation_msg = await __main__.client.send_message(on_channel,'**Round table mode has been activated on this channel.**\n\nIn order to join in this discussion, you must run the command `'+bot_cmd_char+'roundtable join` in here to join the queue. Everybody in the queue gets to post 1 message per turn, anything posted when it isn\'t your turn will be immediately deleted.\n\nIf you keep trying to post when it isn\'t your turn you will be ejected and put into cooldown.')
                        roundtable_details['activation_msg'] = activation_msg.id
                        #await __main__.client.pin_message(activation_msg)

                        if(message.channel.id != on_channel.id): await __main__.client.send_message(message.channel,'Okay <@'+str(message.author.id)+'>, roundtable mode has been activated in '+on_channel.name+'.')

                        roundtable_channels[on_channel.id] = roundtable_details
                        await __main__.set_config('roundtable_channels',message.server,'roundtable',roundtable_channels)

                        roundtable_queues[message.server.id][on_channel.id] = {}
                        roundtable_queues[message.server.id][on_channel.id]['active_user'] = None
                        roundtable_queues[message.server.id][on_channel.id]['active_on'] = None
                        roundtable_queues[message.server.id][on_channel.id]['active_user_typing'] = None
                        roundtable_queues[message.server.id][on_channel.id]['queue'] = []
                        roundtable_queues[message.server.id][on_channel.id]['cooldown'] = []
                        roundtable_queues[message.server.id][on_channel.id]['discussion_active'] = False
                        
                        if(on_channel.id == message.channel.id): await __main__.client.delete_message(message)

                    else: await __main__.client.send_message(message.channel,'Sorry <@'+str(message.author.id)+'>, roundtable mode is already enabled in '+on_channel.name+'.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a channel called '+get_channel_arg)


        if(proc_msg[1] == "off"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','enable_roundtable',True)
            if(chk_user_perm == True):

                if(proc_msg_length == 2):
                    get_channel_arg = '<#'+str(message.channel.id)+'>'
                else: get_channel_arg = proc_msg[2]
                on_channel = await __main__.find_channel_arg(message.server,get_channel_arg,True)
                if(on_channel != False):

                    roundtable_channels = await __main__.get_config('roundtable_channels',message.server,'roundtable')
                    if(roundtable_channels == False): roundtable_channels = {}
                    if(on_channel.id in roundtable_channels):
                        roundtable_details = roundtable_channels[on_channel.id]
                        #await __main__.client.unpin_message(roundtable_details['activation_msg'])

                        del roundtable_channels[on_channel.id]
                        await __main__.set_config('roundtable_channels',message.server,'roundtable',roundtable_channels)
                        del roundtable_queues[message.server.id][on_channel.id]

                        await __main__.client.send_message(on_channel,'**Round table mode has been deactivated on this channel.**\n\nYou can now post whenever you want.')

                        if(message.channel.id != on_channel.id): await __main__.client.send_message(message.channel,'Okay <@'+str(message.author.id)+'>, roundtable mode has been deactivated in '+on_channel.name+'.')

                    else: await __main__.client.send_message(message.channel,'Sorry <@'+str(message.author.id)+'>, roundtable mode is already disabled in '+on_channel.name+'.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a channel called '+get_channel_arg)


        if(proc_msg[1] == "join"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','join_discussions',True)
            if(chk_user_perm == True):

                if(proc_msg_length == 2):
                    get_channel_arg = '<#'+str(message.channel.id)+'>'
                else: get_channel_arg = proc_msg[2]
                on_channel = await __main__.find_channel_arg(message.server,get_channel_arg,True)
                if(on_channel != False):

                    if(on_channel.id in roundtable_queues[message.server.id]):
                        if(message.author.id not in roundtable_queues[message.server.id][on_channel.id]['queue']):

                            time_now = await __main__.current_timestamp()
                            cooldown_remaining = 0
                            for user_entry in roundtable_queues[message.server.id][on_channel.id]['cooldown']:
                                if(user_entry['user_id'] == message.author.id):
                                    time_diff = user_entry['until'] - time_now
                                    if(time_diff > 0): cooldown_remaining = time_diff

                            if(cooldown_remaining > 0):
                                time_diff_human = await __main__.convert_seconds_to_time_string(time_diff) 
                                await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, you are currently in cooldown and cannot rejoin the discussion in '+on_channel.name+' for another '+time_diff_human+'.')
                            else:
                                roundtable_queues[message.server.id][on_channel.id]['queue'].append(message.author.id)
                                await __main__.client.send_message(on_channel,'<@'+str(message.author.id)+'> has joined the discussion.')

                                if(roundtable_queues[message.server.id][on_channel.id]['discussion_active'] == False):
                                    if(len(roundtable_queues[message.server.id][on_channel.id]['queue']) == 1):
                                        await __main__.client.send_message(on_channel,'Waiting on at least 1 more person to join the discussion to begin.')
                                    else:
                                        await set_active_turn(message.server,on_channel,roundtable_queues[message.server.id][on_channel.id]['queue'][0])

                            if(on_channel.id == message.channel.id): await __main__.client.delete_message(message)

                        else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, you are already in the queue for the discussion in '+on_channel.name+'.')
                    else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, there is no active discussion to join in '+on_channel.name+'.')
                else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a channel called '+get_channel_arg)


        if(proc_msg[1] == "leave"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','join_discussions',True)
            if(chk_user_perm == True):

                if(proc_msg_length == 2):
                    get_channel_arg = '<#'+str(message.channel.id)+'>'
                else: get_channel_arg = proc_msg[2]
                on_channel = await __main__.find_channel_arg(message.server,get_channel_arg,True)
                if(on_channel != False):

                    if(on_channel.id in roundtable_queues[message.server.id]):
                        if(message.author.id in roundtable_queues[message.server.id][on_channel.id]['queue']):

                            await __main__.client.send_message(on_channel,'<@'+str(message.author.id)+'> has left the discussion.')

                            use_queue = roundtable_queues[message.server.id][on_channel.id]['queue']
                            if(len(use_queue) > 2):
                                if(roundtable_queues[message.server.id][on_channel.id]['active_user'] == message.author.id):
                                    next_user = await next_user_in_queue(roundtable_queues[message.server.id][on_channel.id]['active_user'],use_queue)
                                    await set_active_turn(message.server,on_channel,next_user)
                            else:
                                roundtable_queues[message.server.id][on_channel.id]['active_user'] = None
                                roundtable_queues[message.server.id][on_channel.id]['active_on'] = None
                                roundtable_queues[message.server.id][on_channel.id]['active_user_typing'] = None
                                roundtable_queues[message.server.id][on_channel.id]['discussion_active'] = False
                                await __main__.client.send_message(on_channel,'Waiting on at least 1 more person to join to continue the discussion.')
                            roundtable_queues[message.server.id][on_channel.id]['queue'].remove(message.author.id)

                            if(on_channel.id == message.channel.id): await __main__.client.delete_message(message)

                        else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, you are already not in the queue for the discussion in '+on_channel.name+'.')
                    else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, there is no active discussion to join in '+on_channel.name+'.')
                else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a channel called '+get_channel_arg)


        if(proc_msg[1] == "interject"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','moderate_discussions',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,3)
                proc_msg_length = len(proc_msg)
                if(proc_msg_length == 4):

                    get_channel_arg = proc_msg[2]
                    on_channel = await __main__.find_channel_arg(message.server,get_channel_arg,True)
                    if(on_channel != False):
                        if(on_channel.id in roundtable_queues[message.server.id]):

                            await __main__.client.send_message(on_channel,proc_msg[3])
                            if(on_channel.id == message.channel.id): await __main__.client.delete_message(message)

                        else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, there is no active discussion to join in '+on_channel.name+'.')
                    else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a channel called '+get_channel_arg)
                else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, you must specify some text which you wan to post into that discussion.')


        if(proc_msg[1] == "skip"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','moderate_discussions',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,3)

                if(proc_msg_length == 2):
                    get_channel_arg = '<#'+str(message.channel.id)+'>'
                else: get_channel_arg = proc_msg[2]
                on_channel = await __main__.find_channel_arg(message.server,get_channel_arg,True)
                if(on_channel != False):
                    if(on_channel.id in roundtable_queues[message.server.id]):

                        skip_to_user = await skip_to_next_turn(message.server,on_channel)
                        if(skip_to_user == None): await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, there is not another valid queued user in '+on_channel.name+' to skip to.')
                        if(on_channel.id == message.channel.id): await __main__.client.delete_message(message)

                    else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, there is no active discussion in '+on_channel.name+'.')
                else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a channel called '+get_channel_arg)


        if(proc_msg[1] == "eject"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','moderate_discussions',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,4)
                proc_msg_length = len(proc_msg)

                get_channel_arg = proc_msg[2]
                on_channel = await __main__.find_channel_arg(message.server,get_channel_arg,True)
                if(on_channel != False):
                    if(on_channel.id in roundtable_queues[message.server.id]):

                        get_user_arg = proc_msg[3]
                        on_user = await __main__.find_user(message.server,get_user_arg,True)
                        if(on_user != False):

                            if(on_user.id in roundtable_queues[message.server.id][on_channel.id]['queue']):

                                if(proc_msg_length == 5):
                                    ejection_reason = ' because: '+proc_msg[4]
                                else: ejection_reason = ''
                                await __main__.client.send_message(on_channel,'<@'+str(on_user.id)+'> has been ejected from the discussion queue'+ejection_reason+'.')
                                await __main__.client.send_message(on_user,'You have been ejected from the discussion queue in '+on_channel.name+ejection_reason+'.')

                                use_queue = roundtable_queues[message.server.id][on_channel.id]['queue']
                                if(len(use_queue) > 2):
                                    if(roundtable_queues[message.server.id][on_channel.id]['active_user'] == on_user.id):
                                        next_user = await next_user_in_queue(roundtable_queues[message.server.id][on_channel.id]['active_user'],use_queue)
                                        await set_active_turn(message.server,on_channel,next_user)
                                else:
                                    roundtable_queues[message.server.id][on_channel.id]['active_user'] = None
                                    roundtable_queues[message.server.id][on_channel.id]['active_on'] = None
                                    roundtable_queues[message.server.id][on_channel.id]['active_user_typing'] = None
                                    roundtable_queues[message.server.id][on_channel.id]['discussion_active'] = False
                                    await __main__.client.send_message(on_channel,'Waiting on at least 1 more person to join to continue the discussion.')
                                roundtable_queues[message.server.id][on_channel.id]['queue'].remove(on_user.id)

                                if(on_channel.id == message.channel.id): await __main__.client.delete_message(message)

                            else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, that user is already not in the queue for the discussion in '+on_channel.name+'.')

                        else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a user called "'+get_user_arg+'".')
                    else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, there is no active discussion to join in '+on_channel.name+'.')
                else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a channel called '+get_channel_arg)


        if(proc_msg[1] == "cooldown"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'roundtable','moderate_discussions',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,4)
                proc_msg_length = len(proc_msg)

                get_channel_arg = proc_msg[2]
                on_channel = await __main__.find_channel_arg(message.server,get_channel_arg,True)
                if(on_channel != False):
                    if(on_channel.id in roundtable_queues[message.server.id]):

                        get_user_arg = proc_msg[3]
                        on_user = await __main__.find_user(message.server,get_user_arg,True)
                        if(on_user != False):

                            if(on_user.id in roundtable_queues[message.server.id][on_channel.id]['queue']):

                                if(proc_msg_length == 5):
                                    ejection_reason = ' because: '+proc_msg[4]
                                else: ejection_reason = ''
                                await __main__.client.send_message(on_channel,'<@'+str(on_user.id)+'> has been ejected from the discussion queue and put into cooldown'+ejection_reason+'.')
                                await __main__.client.send_message(on_user,'You have been ejected from the discussion queue in '+on_channel.name+' and put into cooldown'+ejection_reason+'.')
                                use_queue = roundtable_queues[message.server.id][on_channel.id]['queue']
                                if(len(use_queue) > 2):
                                    if(roundtable_queues[message.server.id][on_channel.id]['active_user'] == on_user.id):
                                        next_user = await next_user_in_queue(roundtable_queues[message.server.id][on_channel.id]['active_user'],use_queue)
                                        await set_active_turn(message.server,on_channel,next_user)
                                else:
                                    roundtable_queues[message.server.id][on_channel.id]['active_user'] = None
                                    roundtable_queues[message.server.id][on_channel.id]['active_on'] = None
                                    roundtable_queues[message.server.id][on_channel.id]['active_user_typing'] = None
                                    roundtable_queues[message.server.id][on_channel.id]['discussion_active'] = False
                                    await __main__.client.send_message(on_channel,'Waiting on at least 1 more person to join to continue the discussion.')
                                roundtable_queues[message.server.id][on_channel.id]['queue'].remove(on_user.id)

                                cooldown_time = await __main__.get_config('roundtable_cooldown_time',message.server,'roundtable')
                                if(cooldown_time == False): cooldown_time = 1800
                                cooldown_until = await __main__.current_timestamp() + cooldown_time
                                cd_run = 0
                                found_existing = False
                                while(cd_run < len(roundtable_queues[message.server.id][on_channel.id]['cooldown'])):
                                    if(roundtable_queues[message.server.id][on_channel.id]['cooldown'][cd_run]['user_id'] == on_user.id):
                                        found_existing = True
                                        roundtable_queues[message.server.id][on_channel.id]['cooldown'][cd_run]['until'] = cooldown_until
                                        break
                                    cd_run = cd_run + 1
                                if(found_existing == False):
                                    new_cooldown = {}
                                    new_cooldown['user_id'] = on_user.id
                                    new_cooldown['until'] = cooldown_until
                                    roundtable_queues[message.server.id][on_channel.id]['cooldown'].append(new_cooldown)

                                if(on_channel.id == message.channel.id): await __main__.client.delete_message(message)

                            else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, that user is already not in the queue for the discussion in '+on_channel.name+'.')

                        else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a user called "'+get_user_arg+'".')
                    else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, there is no active discussion to join in '+on_channel.name+'.')
                else: await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, I couldn\'t find a channel called '+get_channel_arg)





async def message_new(message):
    if(message.author.id != __main__.client.user.id):
        if(message.channel.id in roundtable_queues[message.server.id]):
            bot_cmd_char = await __main__.get_cmd_char(message.server)
            this_roundtable = roundtable_queues[message.server.id][message.channel.id]

            if(this_roundtable['active_user'] == message.author.id):
                await skip_to_next_turn(message.server,message.channel)
            else:
                if(message.content.startswith(bot_cmd_char+'roundtable') == False):
                    if(message.author.id in this_roundtable['queue']):
                        await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, your post in '+message.channel.name+' has been deleted because it is not your turn to speak. Please wait patiently, you will be pinged when it is your turn.')
                    else:
                        await __main__.client.send_message(message.author,'Sorry <@'+str(message.author.id)+'>, you are not allowed to post in '+message.channel.name+' because you are not in the discussion queue.\n\nTo join in this discussion you can either run the command `'+bot_cmd_char+'roundtable join` in that channel, or you can run the command `'+bot_cmd_char+'roundtable join '+message.channel.name+'` in here or any other channel. You will then be pinged when it is your turn to post.')

                if(message.content.startswith(bot_cmd_char+'roundtable') == False): await __main__.client.delete_message(message)


async def message_edit(before,after): pass

async def message_delete(message): pass

async def message_typing(channel,user,datestamp):
    await check_active_seen_typing(channel.server,channel,user.id)

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
