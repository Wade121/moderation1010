#!/usr/bin/python

import __main__

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Announcements'
    help_info['description'] = 'Post server announcements as the bot and set timed repeat announcements.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'set'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'announcement_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Set the announcement channel to channel_name'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'announce'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'list_timed'
    help_entry['args'] = ''
    help_entry['description'] = 'List the timed announcements setup on this server.'
    help_entry['perm_name'] = 'make_announcements'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add_timed'
    help_entry['args'] = 'mode time_int time_scale channel_name announcement_text'
    help_entry['description'] = 'Creates a new timed announcement in channel_name, mode can be either "single" or "repeat". Time_int and time_scale should be a number and a scale such as "6 hours".'
    help_entry['perm_name'] = 'make_announcements'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'del_timed'
    help_entry['args'] = 'announcement_id'
    help_entry['description'] = 'Deletes the timed announcement with ID announcement_id'
    help_entry['perm_name'] = 'make_announcements'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'ping'
    help_entry['args'] = 'announcement_text'
    help_entry['description'] = 'Pings everyone and posts announcement_text into the announcement channel.'
    help_entry['perm_name'] = 'make_announcements'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'no_ping'
    help_entry['args'] = 'announcement_text'
    help_entry['description'] = 'Posts announcement_text into the announcement channel, but does not ping anybody.'
    help_entry['perm_name'] = 'make_announcements'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'make_announcements'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')

    this_perm = 'change_settings'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')

    return perm_info


async def server_setup_wizard():
    return True

#===================================================================================================================
#SERVER EVENTS

async def server_join(server): pass

async def server_remove(server): pass

async def server_update(before,after): pass

async def server_connected(server):
    await load_auto_announcements(server)

#===================================================================================================================
#MESSAGE EVENTS

async def load_auto_announcements(server_obj):
    timed_announce = await __main__.get_config('timed_announce',server_obj,'announcements')
    if(timed_announce == False):
        timed_announce = []
    ta_len = len(timed_announce)

    if(ta_len > 0):
        ta_len = ta_len - 1
        ta_run = 0
        while(ta_run <= ta_len):
            this_ta = timed_announce[ta_run]
            await __main__.add_task(server_obj,int(this_ta['call_time']),"announcements","auto_announce",ta_run)
            if(__main__.verbose_out == True): await __main__.log_entry('Loading timed announcement "'+this_ta['msg']+'"',server_obj)
            ta_run = ta_run + 1


async def auto_announce(server_obj=None,ta_key=None):
    if(server_obj != None and ta_key != None):
        ta_key = int(ta_key)
        timed_announce = await __main__.get_config('timed_announce',server_obj,'announcements')
        if(timed_announce == False):
            timed_announce = []
        ta_len = len(timed_announce)

        if(ta_len > 0):
            ta_len = ta_len - 1
            ta_run = 0
            while(ta_run <= ta_len):
                if(ta_run == ta_key):
                    this_ta = timed_announce[ta_run]
                    find_channel = await __main__.find_channel_arg(server_obj,'<#'+this_ta['channel']+'>',True)
                    server_msg = await __main__.client.send_message(find_channel,this_ta['msg'])

                    if(this_ta['repeat'] == "repeat"):
                        add_time = await __main__.cmd_time_args(this_ta['time_int'],this_ta['time_scale'])
                        time_now = await __main__.current_timestamp()
                        call_time = time_now + add_time
                        this_ta['call_time'] = call_time
                        timed_announce[ta_run] = this_ta
                        await __main__.add_task(server_obj,call_time,"announcements","auto_announce",ta_key)
                        await __main__.set_config('timed_announce',server_msg,'announcements',timed_announce)
                    else: await del_timed_announce(server_msg,ta_key)
                    ta_run = ta_len + 1

                ta_run = ta_run + 1


async def del_timed_announce(server_msg=None,ta_key=None,message=None):
    ta_key = int(ta_key)
    timed_announce = await __main__.get_config('timed_announce',server_msg.server,'announcements')
    if(timed_announce == False):
        timed_announce = []
    ta_len = len(timed_announce)

    if(ta_len > 0):
        ta_len = ta_len - 1
        ta_run = 0
        found_entry = False
        while(ta_run <= ta_len):
            if(ta_run == ta_key):
                found_entry = True
                del timed_announce[ta_run]
                await __main__.set_config('timed_announce',server_msg.server,'announcements',timed_announce)
                ta_run = ta_len + 1
            ta_run = ta_run + 1

        if(message != None):
            if(found_entry == True):
                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have deleted that timed announcement.')
            else:
                ta_key = ta_key + 1
                await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a timed announcement with ID "'+str(ta_key)+'".')


async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)

    if(message.content.startswith(bot_cmd_char+'set')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)
        if(proc_msg[1] == "announcement_channel"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'announcements','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    await __main__.set_config('announcement_channel',message.server,'announcements',find_channel.id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will now use that channel for general announcements.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')

    
    if(message.content.startswith(bot_cmd_char+'announce')):
        proc_msg = await __main__.get_cmd_args(message.content,2)
        proc_msg_length = len(proc_msg)

        if(proc_msg[1] == "add_timed"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'announcements','make_announcements',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,6)
                proc_msg_length = len(proc_msg)
                if(proc_msg_length == 7):
                    repeat_mode = proc_msg[2]
                    if(repeat_mode == "single" or repeat_mode == "repeat"):
                        time_int = int(proc_msg[3])
                        time_scale = proc_msg[4]
                        add_time = await __main__.cmd_time_args(time_int,time_scale)
                        if(add_time != False):
                            time_now = await __main__.current_timestamp()
                            call_time = time_now + add_time
                            find_channel = await __main__.find_channel_arg(message.server,proc_msg[5],True)
                            if(find_channel != False):
                                timed_announce = await __main__.get_config('timed_announce',message.server,'announcements')
                                if(timed_announce == False): timed_announce = []

                                build_announce = {}
                                build_announce['repeat'] = repeat_mode
                                build_announce['time_int'] = time_int
                                build_announce['time_scale'] = time_scale
                                build_announce['call_time'] = call_time
                                build_announce['channel'] = find_channel.id
                                build_announce['msg'] = proc_msg[6]

                                timed_announce.append(build_announce)
                                ta_key = len(timed_announce) - 1
                                await __main__.add_task(message.server,call_time,"announcements","auto_announce",ta_key)
                                await __main__.set_config('timed_announce',message.server,'announcements',timed_announce)
                                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, that timed announcement has been added.')

                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[5]+'".')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either an integer and a time scale, for example "3 hours".')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either "single" or "repeat" for this timed announcement.')

        if(proc_msg[1] == "del_timed"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'announcements','make_announcements',True)
            if(chk_user_perm == True):
                proc_msg[2] = int(proc_msg[2]) - 1
                await del_timed_announce(message,proc_msg[2],message)


        if(proc_msg[1] == "list_timed"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'announcements','make_announcements',True)
            if(chk_user_perm == True):
                timed_announce = await __main__.get_config('timed_announce',message.server,'announcements')
                if(timed_announce == False):
                    timed_announce = []
                ta_len = len(timed_announce)

                build_ta_list = ''
                if(ta_len > 0):
                    ta_len = ta_len - 1
                    ta_run = 0
                    while(ta_run <= ta_len):
                        this_ta = timed_announce[ta_run]
                        this_ta_id = ta_run + 1
                        find_channel = await __main__.find_channel_arg(message.server,'<#'+this_ta['channel']+'>',True)
                        build_ta_list = build_ta_list+'\n**'+str(this_ta_id)+' - ** "'+this_ta['msg']+'" in #'+find_channel.name
                        ta_run = ta_run + 1
                if(build_ta_list == ""): build_ta_list = 'There are currently no timed announcements.'

                icon_url = __main__.client.user.avatar_url
                if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url

                em = __main__.discord.Embed(title='Timed announcements', description=build_ta_list, colour=3447003)
                em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)

                await __main__.client.send_message(message.channel, embed=em)



        if(proc_msg[1] == "ping" or proc_msg[1] == "no_ping"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'announcements','make_announcements',True)
            if(chk_user_perm == True):

                announcement_channel = await __main__.get_config('announcement_channel',message.server,'announcements')

                if(announcement_channel != False):
                    announce_channel = await __main__.channel_name_from_id(message.server,announcement_channel,True)

                    proc_msg = await __main__.get_cmd_args(message.content,2)
                    proc_msg_length = len(proc_msg)
                    if(proc_msg_length >= 3 and (proc_msg[1] == "ping" or proc_msg[1] == "no_ping")):
                        proc_msg_clean = proc_msg[2]

                        announce_ping = ''
                        if(proc_msg[1] == "ping"):
                            announce_ping = 'Announcement for @everyone'

                        icon_url = message.server.icon_url
                        if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url

                        em = __main__.discord.Embed(title='Announcement', description=proc_msg_clean, colour=3447003)
                        em.set_author(name=message.server.name, icon_url=icon_url)

                        await __main__.client.send_message(announce_channel,announce_ping,embed=em)
                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve posted that announcement for you.')

                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify whether you would like a "ping" or "no_ping", as well as an announcement to make.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I can\'t make an announcement because the announcement channel has not been set.')



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
