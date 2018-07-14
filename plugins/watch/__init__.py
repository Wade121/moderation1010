#!/usr/bin/python

import __main__

watchlist = {}

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Watchlist'
    help_info['description'] = 'Reposts messages made by users being watched into a specific channel.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'set'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'watchlist_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Sets the channel which watchlist messages will be posted to.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'watch_new_users'
    help_entry['args'] = 'time_int time_scale'
    help_entry['description'] = 'Sets how long new members will be automatically added to the watchlist for. Time_int should be a number and time_scale should be a unit, such as "3 days".'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'watch'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'list'
    help_entry['args'] = ''
    help_entry['description'] = 'Lists out which members are currently on the watch list and how long for.'
    help_entry['perm_name'] = 'manage_users'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add'
    help_entry['args'] = 'member_name time_int time_scale'
    help_entry['description'] = 'Adds member_name to the watch list, time_int and time_scale are optional, if not specified the member will be added to the watch list until removed manually. If specified, time_int should be a number and time_scale should be a unit, such as "1 week".'
    help_entry['perm_name'] = 'manage_users'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'remove'
    help_entry['args'] = 'member_name'
    help_entry['description'] = 'Removes member_name from the watch list.'
    help_entry['perm_name'] = 'manage_users'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'manage_users'
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

async def server_join(server):
    await load_watchlist(server)

async def server_remove(server):
    await unload_watchlist(server)

async def server_update(before,after): pass

async def server_connected(server):
    await load_watchlist(server)

#===================================================================================================================
#MESSAGE EVENTS

async def load_watchlist(server_obj=None):
    if(server_obj != None):
        use_server_id = await __main__.hash_server_id(server_obj.id)
        watchlist[server_obj.id] = []
        watchdb = __main__.db.cursor()
        watchdb.execute("SELECT * FROM watchlist WHERE server_id=?",(use_server_id,))
        for user in watchdb:
            dec_user_id = await __main__.decrypt_data(user['stored_user_id'])
            is_on_server = False
            for member in server_obj.members:
                if(str(dec_user_id) == str(member.id)): is_on_server = True

            if(is_on_server == True):
                if(dec_user_id not in watchlist[server_obj.id]):
                    if(__main__.verbose_out == True): await __main__.log_entry("Loading user "+str(dec_user_id)+" onto "+server_obj.name+" watch list",server_obj)
                    watchlist[server_obj.id].append(int(dec_user_id))
                    if(user['until'] != "" and user['until'] != 0):
                        await __main__.add_task(server_obj,int(user['until']),'watch','auto_remove_watchlist',int(dec_user_id))
            else:
                await auto_remove_watchlist(server_obj,dec_user_id,True)


async def unload_watchlist(server_obj=None):
    if(server_obj != None):
        if(server_obj.id in watchlist):
            del watchlist[server_obj.id]
            if(__main__.verbose_out == True): await log_entry('Unloaded '+server_obj.name+' watchlist',server_obj)


async def auto_remove_watchlist(server_obj=None,rem_user_id=None,force_remove=False):
    rem_user_id = int(rem_user_id)
    if(rem_user_id in watchlist[server_obj.id] or force_remove == True):
        use_server_id = await __main__.hash_server_id(server_obj.id)
        use_member_id = await __main__.hash_member_id(server_obj.id,rem_user_id)
        this_user = await __main__.find_user(server_obj,'<@'+str(rem_user_id)+'>',True)

        get_list = __main__.db.cursor()
        get_list.execute("SELECT * FROM watchlist WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
        get_list_date = 0
        for row in get_list:
            get_list_date = row['until']

        time_now = await __main__.current_timestamp()
        if((get_list_date != 0 and time_now >= int(get_list_date)) or force_remove == True):
            if(__main__.verbose_out == True): await __main__.log_entry("Auto removing "+str(rem_user_id)+" from "+server_obj.name+" watch list",server_obj)
            del_list = __main__.db.cursor()
            del_list.execute("DELETE FROM watchlist WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
            __main__.db.commit()
            if(rem_user_id in watchlist[server_obj.id]): watchlist[server_obj.id].remove(rem_user_id)

            watchlist_channel = await __main__.bot_use_channel(server_obj,'watch','watchlist_channel')
            if(watchlist_channel != False):
                if(this_user != False):
                    await __main__.client.send_message(watchlist_channel,'<@'+__main__.client.user.id+'> has removed '+this_user.display_name+' ('+this_user.name+'#'+this_user.discriminator+') from the watch list.')
                else:
                    await __main__.client.send_message(watchlist_channel,'<@'+__main__.client.user.id+'> has removed <@'+str(rem_user_id)+'> from the watch list.')


async def auto_add_watchlist(user,server_obj):
    watch_new_users = await __main__.get_config('watch_new_users',server_obj,'watch')
    if(watch_new_users != False and int(watch_new_users) > 0):
        if(int(user.id) not in watchlist[server_obj.id]):
            use_server_id = await __main__.hash_server_id(server_obj.id)
            use_member_id = await __main__.hash_member_id(server_obj.id,user.id)
            save_user_id = await __main__.encrypt_data(user.id)

            if(__main__.verbose_out == True): await __main__.log_entry("Auto adding new member "+user.display_name+" ("+str(user.id)+") to "+server_obj.name+" watch list")
            time_now = await __main__.current_timestamp()
            watch_until = time_now + int(watch_new_users)
            add_list = __main__.db.cursor()
            add_list.execute("INSERT INTO watchlist (user_id,stored_user_id,datestamp,until,server_id) VALUES (?,?,?,?,?)",(use_member_id,save_user_id,time_now,watch_until,use_server_id,))
            __main__.db.commit()
            watchlist[server_obj.id].append(int(user.id))
            await __main__.add_task(server_obj,watch_until,'watch','auto_remove_watchlist',int(user.id))
            
            watchlist_channel = await __main__.bot_use_channel(server_obj,'watch','watchlist_channel')
            if(watchlist_channel != False):
                await __main__.client.send_message(watchlist_channel,'<@'+__main__.client.user.id+'> has added '+user.display_name+' ('+user.name+'#'+user.discriminator+') to the watch list.')
            

async def watchlist_msg(message=None):
    if(message != None and message.channel.is_private == False and message.server.id in watchlist):
        if(int(message.author.id) in watchlist[message.server.id]):
            watchlist_channel = await __main__.bot_use_channel(message.server,'watch','watchlist_channel')
            if(watchlist_channel != False):
                icon_url = message.author.avatar_url
                if(icon_url == None or icon_url == ""): icon_url = message.author.default_avatar_url

                repost_title = 'Posted in #'+message.channel.name+':'

                em = __main__.discord.Embed(title=repost_title, description=message.content, colour=3447003)
                em.set_author(name=message.author.display_name, icon_url=icon_url)
                #em.set_thumbnail(url=icon_url)

                #em.add_field(name="Roles you have",value=build_roles_got,inline=True)

                attach_length = len(message.attachments)
                if(attach_length > 0):
                    file_type = await __main__.attachment_file_type(message.attachments[0])
                    if(file_type == "image"):
                        em.set_image(url=message.attachments[0]['url'])
                    else:
                        attached_file_name = message.attachments[0]['filename']
                        attached_file_url = message.attachments[0]['url']
                        em.add_field(name="Attached file: "+attached_file_name,value=attached_file_url,inline=False)

                msg_time = str(message.timestamp).split(".")
                msg_time = msg_time[0]
                em.set_footer(text=msg_time)
                await __main__.client.send_message(watchlist_channel, embed=em)

                if(attach_length > 1):
                    attach_run = 1
                    attach_length = attach_length - 1
                    while(attach_run <= attach_length):
                        
                        fem = __main__.discord.Embed(title=repost_title, description='', colour=3447003)
                        fem.set_author(name=message.author.display_name, icon_url=icon_url)
                        file_type = await __main__.attachment_file_type(message.attachments[attach_run])
                        if(file_type == "image"):
                            fem.set_image(url=message.attachments[attach_run]['url'])
                        else:
                            attached_file_name = message.attachments[attach_run]['filename']
                            attached_file_url = message.attachments[attach_run]['url']
                            fem.add_field(name="Attached file: "+attached_file_name,value=attached_file_url,inline=False)
                        fem.set_footer(text=msg_time)
                        await __main__.client.send_message(watchlist_channel, embed=fem)

                        attach_run = attach_run + 1



async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)

    if(message.content.startswith(bot_cmd_char+'set')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)

        if(proc_msg[1] == "watchlist_channel"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'watch','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    await __main__.bot_set_channel(message.server,'watch','watchlist_channel',find_channel.id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will now use that channel for posting watchlist messages.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')

        if(proc_msg[1] == "watch_new_users"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'watch','change_settings',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 4):
                    add_time = await __main__.cmd_time_args(proc_msg[2],proc_msg[3])
                    await __main__.set_config('watch_new_users',message.server,'watch',add_time)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will add new users to the watch list for '+str(proc_msg[2])+' '+str(proc_msg[3])+'.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a length of time to watch new users for.')




    if(message.content.startswith(bot_cmd_char+'watch')):

        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)
        if(proc_msg_length >= 2):
            use_server_id = await __main__.hash_server_id(message.server.id)


            if(proc_msg[1] == "list"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'watch','manage_users',True)
                if(chk_user_perm == True):
                    list_sent = 0
                    icon_url = __main__.client.user.avatar_url
                    if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url

                    get_list = __main__.db.cursor()
                    get_list.execute("SELECT * FROM watchlist WHERE server_id=? ORDER BY datestamp DESC",(use_server_id,))
                    get_list_count = 0
                    build_users = ''
                    listed_already = []
                    for row in get_list:
                        get_list_count = get_list_count + 1
                        dec_user_id = await __main__.decrypt_data(row['stored_user_id'])
                        this_user = await __main__.find_user(message.server,'<@'+str(dec_user_id)+'>',True)
                        if(this_user != False):
                            watched_since = await __main__.timestamp_to_date(row['datestamp'],True)
                            if(row['until'] != "" and row['until'] != 0):
                                until_date = await __main__.timestamp_to_date(int(row['until']),True)
                            else: until_date = 'told otherwise'

                            if(dec_user_id not in listed_already):
                                build_users = build_users+'**'+this_user.display_name+' ('+this_user.name+'#'+this_user.discriminator+')**\nuntil '+until_date+'\n\n'
                                listed_already.append(dec_user_id)

                            if(len(build_users) >= 1600):
                                list_sent = list_sent + 1
                                if(list_sent >= 2):
                                    list_app_title = ' (page '+str(list_sent)+')'
                                else: list_app_title = ''
                                em = __main__.discord.Embed(title='Watch list'+list_app_title, description=build_users, colour=3447003)
                                build_users = ''
                                em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                                await __main__.client.send_message(message.channel, embed=em)


                    if(len(build_users) > 0):
                        list_sent = list_sent + 1
                        if(list_sent >= 2):
                            list_app_title = ' (page '+str(list_sent)+')'
                        else: list_app_title = ''
                        em = __main__.discord.Embed(title='Watch list'+list_app_title, description=build_users, colour=3447003)
                        em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                        await __main__.client.send_message(message.channel, embed=em)
                        build_users = ''

                    if(get_list_count == 0):
                        list_descript = 'There are no users on the watch list at the moment.'
                        em = __main__.discord.Embed(title='Watch list', description=list_descript, colour=3447003)
                        em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                        #em.set_thumbnail(url=icon_url)
                        #em.set_image(url)
                        await __main__.client.send_message(message.channel, embed=em)



            if(proc_msg[1] == "add"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'watch','manage_users',True)
                if(chk_user_perm == True):
                    if(proc_msg_length >= 3):
                        this_user = await __main__.find_user(message.server,proc_msg[2],True)
                        if(this_user != False):
                            if(this_user.id not in watchlist[message.server.id]):
                                
                                use_server_id = await __main__.hash_server_id(message.server.id)
                                use_member_id = await __main__.hash_member_id(message.server.id,this_user.id)
                                save_user_id = await __main__.encrypt_data(this_user.id)
                                
                                time_now = await __main__.current_timestamp()
                                if(proc_msg_length == 5):
                                    timefor = await __main__.cmd_time_args(proc_msg[3],proc_msg[4])
                                    timefor_txt = ' for '+proc_msg[3]+' '+proc_msg[4]
                                else:
                                    timefor = 0
                                    timefor_txt = ' until removed'
                                
                                if(timefor > 0):
                                    until_time = time_now + timefor
                                else: until_time = 0

                                add_list = __main__.db.cursor()
                                add_list.execute("INSERT INTO watchlist (user_id,stored_user_id,server_id,datestamp,until) VALUES (?,?,?,?,?)",(use_member_id,save_user_id,use_server_id,time_now,until_time,))
                                __main__.db.commit()
                                watchlist[message.server.id].append(int(this_user.id))
                                if(timefor > 0): await __main__.add_task(message.server,until_time,'watch','auto_remove_watchlist',int(this_user.id))
                                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve added '+this_user.display_name+' to the watch list'+timefor_txt+'.')
                                if(__main__.verbose_out == True): await __main__.log_entry("Loading user "+str(this_user.id)+" onto "+message.server.name+" watch list"+timefor_txt,message.server)
                                
                                watchlist_channel = await __main__.bot_use_channel(message.server,'watch','watchlist_channel')
                                if(watchlist_channel != False):
                                    await __main__.client.send_message(watchlist_channel,message.author.display_name+' has added <@'+this_user.id+'> to the watch list'+timefor_txt+'.')
                                    
                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that user is already on the watch list.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find the user "'+proc_msg[2]+'".')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a user to add to the watch list.')



            if(proc_msg[1] == "remove"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'watch','manage_users',True)
                if(chk_user_perm == True):
                    if(proc_msg_length >= 3):
                        this_user = await __main__.find_user(message.server,proc_msg[2],True)
                        if(this_user != False):
                            use_server_id = await __main__.hash_server_id(message.server.id)
                            use_member_id = await __main__.hash_member_id(message.server.id,this_user.id)

                            find_list = __main__.db.cursor()
                            find_list.execute("SELECT * FROM watchlist WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                            find_list_count = 0
                            for row in find_list:
                                find_list_count = find_list_count + 1

                            if(find_list_count > 0):
                                del_list = __main__.db.cursor()
                                del_list.execute("DELETE FROM watchlist WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                                __main__.db.commit()
                                watchlist[message.server.id].remove(int(this_user.id))
                                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve removed '+this_user.display_name+' from the watch list.')
                                if(__main__.verbose_out == True): await __main__.log_entry("Removing user "+str(this_user.id)+" from "+message.server.name+" watch list",message.server)

                                watchlist_channel = await __main__.bot_use_channel(message.server,'watch','watchlist_channel')
                                if(watchlist_channel != False):
                                    await __main__.client.send_message(watchlist_channel,message.author.display_name+' has removed <@'+this_user.id+'> from the watch list.')

                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that user is already not on the watch list.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find the user "'+proc_msg[1]+'".')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a user to remove from the watch list.')


async def message_new(message):
    await watchlist_msg(message)

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

async def member_join(member):
    await auto_add_watchlist(member,member.server)

async def member_remove(member): 
    await auto_remove_watchlist(member.server,member.id,True)

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
