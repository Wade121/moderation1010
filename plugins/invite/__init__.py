#!/usr/bin/python

import __main__

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Invites'
    help_info['description'] = 'Create personal invite links you can share with friends.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'set'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'invite_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Sets the channel which all personal invites will be created for.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'invite_log_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Sets the channel where personal invite creations will be logged.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'invite'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'refresh'
    help_entry['args'] = ''
    help_entry['description'] = 'Forces the bot to refresh its list of active invites, usually run after giving the bot permission to manage server invites.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = ''
    help_entry['description'] = 'Create a new personal invite code you can give to a friend.'
    help_entry['perm_name'] = 'personal_invites'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'list'
    help_entry['args'] = ''
    help_entry['description'] = 'List the personal invites you have created which are still active and unused.'
    help_entry['perm_name'] = 'personal_invites'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'remove'
    help_entry['args'] = 'invite_code'
    help_entry['description'] = 'Delete the invite_code you created.'
    help_entry['perm_name'] = 'personal_invites'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'personal_invites'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('members')

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

async def server_connected(server): pass

#===================================================================================================================
#MESSAGE EVENTS

async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)

    if(message.content.startswith(bot_cmd_char+'set')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)

        if(proc_msg[1] == "invite_log_channel"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'invite','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    await __main__.bot_set_channel(message.server,'invite','invite_log_channel',find_channel.id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will now use that channel for posting when members create personal invites.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')

        if(proc_msg[1] == "invite_channel"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'invite','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    await __main__.set_config('invite_channel',message.server,'invite',find_channel.id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, all personal invites will be created for that channel.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')



    if(message.content.startswith(bot_cmd_char+'invite')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'invite','personal_invites',True)
        if(chk_user_perm == True):

            if(proc_msg_length == 1):
                proc_msg[1] = 'add'
                proc_msg_length = 2

            if(proc_msg[1] == "list"):
                #list all active personal invites
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'invite','personal_invites',True)
                if(chk_user_perm == True):
                    use_server_id = await __main__.hash_server_id(message.server.id)
                    use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)

                    get_list = __main__.db.cursor()
                    get_list.execute("SELECT * FROM invites WHERE server_id=? AND user_id=? AND inv_used=0 ORDER BY id ASC",(use_server_id,use_member_id,))
                    chk_invs_count = 0
                    build_list = ''
                    time_now = await __main__.current_timestamp()
                    for row in get_list:
                        chk_exp = int(row['inv_expiry'])
                        if(chk_exp == 0 or chk_exp > time_now):
                            chk_invs_count = chk_invs_count + 1
                            rem_secs = chk_exp - time_now

                            time_left = ''
                            if(rem_secs >= 3600):
                                rem_hours = str(rem_secs / 3600).split(".")
                                rem_hours = rem_hours[0]
                                time_left = rem_hours+' hour(s) '
                                rem_secs = rem_secs - (int(rem_hours) * 3600)

                            if(rem_secs >= 60):
                                rem_mins = str(rem_secs / 60).split(".")
                                rem_mins = rem_mins[0]
                                time_left = time_left+rem_mins+' min(s)'

                            build_list = build_list+'**'+row['inv_code']+'** (https://discord.gg/'+row['inv_code']+') expires in '+time_left+'.\n\n'

                    icon_url = __main__.client.user.avatar_url
                    if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url

                    if(chk_invs_count == 0):
                        list_descript = 'You do not have any active personal invites at the moment.'
                    else: list_descript = build_list

                    em = __main__.discord.Embed(title=message.author.display_name+'\'s personal invitations', description=list_descript, colour=3447003)
                    em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                    #em.set_thumbnail(url=icon_url)
                    #em.set_image(url)

                    await __main__.client.send_message(message.author, embed=em)


            if(proc_msg[1] == "remove"):
                #create personal invite
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'invite','personal_invites',True)
                if(chk_user_perm == True):
                    if(proc_msg_length == 3):
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)

                        use_inv_code = proc_msg[2]
                        use_inv_code = use_inv_code.replace("https://discord.gg/","")
                        use_inv_code = use_inv_code.replace("http://discord.gg/","")

                        chk_invs = __main__.db.cursor()
                        chk_invs.execute("SELECT * FROM invites WHERE server_id=? AND user_id=? AND inv_code=? AND inv_used='0'",(use_server_id,use_member_id,use_inv_code,))
                        chk_invs_count = 0
                        time_now = await __main__.current_timestamp()
                        for row in chk_invs:
                            chk_exp = int(row['inv_expiry'])
                            if(chk_exp == 0 or chk_exp > time_now):
                                chk_invs_count = chk_invs_count + 1

                        if(chk_invs_count == 1):

                            try:
                                get_invite = await __main__.client.get_invite(use_inv_code)
                            except: get_invite = False

                            if(get_invite != False):

                                try:
                                    await __main__.client.delete_invite(get_invite)
                                    del_invite = True
                                except: del_invite = False

                                if(del_invite == True):

                                    save_inv = __main__.db.cursor()
                                    save_inv.execute("DELETE FROM invites WHERE server_id=? AND user_id=? AND inv_code=? AND inv_used=0",(use_server_id,use_member_id,use_inv_code,))
                                    __main__.db.commit()

                                    await __main__.update_server_invites(message.server)

                                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have revoked that personal invite code.')

                                    inv_log_channel = await __main__.bot_use_channel(message.server,'invite','invite_log_channel')
                                    if(inv_log_channel != False):
                                        await __main__.client.send_message(inv_log_channel,message.author.display_name+' ('+message.author.name+'#'+message.author.discriminator+' / <@'+message.author.id+'>) has revoked their personal invite code '+get_invite.code+'.')

                                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t delete that invite probably because I don\'t have permission to revoke invites on this server.')
                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find an active invite with code "'+use_inv_code+'".')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find an active invite with code "'+use_inv_code+'".')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the invite code you want to remove.')


            if(proc_msg[1] == "add"):
                #create personal invite
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'invite','personal_invites',True)
                if(chk_user_perm == True):
                    invite_chan_id = await __main__.get_config('invite_channel',message.server,'invite')
                    invite_channel = False
                    if(invite_chan_id != False): invite_channel = await __main__.channel_name_from_id(message.server,invite_chan_id,True)
                    if(invite_chan_id != False and invite_channel != False):
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)

                        chk_invs = __main__.db.cursor()
                        chk_invs.execute("SELECT * FROM invites WHERE server_id=? AND user_id=? AND inv_used='0'",(use_server_id,use_member_id,))
                        chk_invs_count = 0
                        time_now = await __main__.current_timestamp()
                        for row in chk_invs:
                            chk_exp = int(row['inv_expiry'])
                            if(chk_exp == 0 or chk_exp > time_now): chk_invs_count = chk_invs_count + 1

                        if(chk_invs_count < 5):

                            max_age = (60 * 60) * 24
                            new_inv_exp = time_now + max_age

                            try:
                                new_invite = await __main__.client.create_invite(invite_channel,max_age=max_age,max_uses=1)
                            except: new_invite = False

                            if(new_invite != False):
                                save_user_id = await __main__.encrypt_data(message.author.id)
                                save_inv_code = new_invite.code

                                save_inv = __main__.db.cursor()
                                save_inv.execute("INSERT INTO invites (server_id,user_id,stored_user_id,inv_code,inv_expiry,inv_created,inv_used) VALUES (?,?,?,?,?,?,0)",(use_server_id,use_member_id,save_user_id,save_inv_code,new_inv_exp,time_now,))
                                __main__.db.commit()

                                await __main__.update_server_invites(message.server)

                                await __main__.client.send_message(message.author,'Okay I have created this new invite for you: **'+new_invite.code+'** (https://discord.gg/'+new_invite.code+').\nIt is valid for 1 use and will expire in 24 hours if it is not used by then.')

                                inv_log_channel = await __main__.bot_use_channel(message.server,'invite','invite_log_channel')
                                if(inv_log_channel != False):
                                    await __main__.client.send_message(inv_log_channel,message.author.display_name+' ('+message.author.name+'#'+message.author.discriminator+' / <@'+message.author.id+'>) has created the personal invite code '+new_invite.code+' which is valid for 1 use and will expire in 24 hours.')


                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, creating that invite failed, it looks like I don\'t have permission to make invites on this server.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I can\'t create another invite for you yet, because you already have 5 active ones waiting to be used. When one or more of those invites is used or expired you can create another one.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I can\'t create you an invite code because my invite channel has not been set up.')

            if(proc_msg[1] == "refresh"):
                #create personal invite
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'invite','change_settings',True)
                if(chk_user_perm == True):
                    upd_invites = await __main__.update_server_invites(message.server)
                    if(upd_invites == True):
                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have refreshed my list of invites currently active on this server.')
                    else:
                        await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t get a list of invites. I don\'t think I have permission to manage invites on this server.')


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

async def user_info_data(server,user):
    ret_data = False
    use_server_id = await __main__.hash_server_id(server.id)
    use_member_id = await __main__.hash_member_id(server.id,user.id)

    used_code = __main__.db.cursor()
    used_code.execute("SELECT * FROM users WHERE server_id=? AND user_id=?",(use_server_id,use_member_id,))
    use_inv_code = ''
    for row in used_code:
        use_inv_code = await __main__.decrypt_data(row['inv_used'])

    if(use_inv_code != False and use_inv_code != "" and use_inv_code.lower() != "unknown"):
        chk_invs = __main__.db.cursor()
        chk_invs.execute("SELECT * FROM invites WHERE server_id=? AND inv_code=?",(use_server_id,use_inv_code,))
        chk_invs_count = 0
        code_owner_id = ''
        for row in chk_invs:
            chk_invs_count = chk_invs_count + 1
            code_owner_id = await __main__.decrypt_data(row['stored_user_id'])

        if(chk_invs_count == 1):

            if(code_owner_id != "" and code_owner_id != False):
                code_owner_obj = await __main__.find_user(server,'<@'+code_owner_id+'>',True)
                if(code_owner_obj != False):
                    invite_note = code_owner_obj.display_name+' ('+code_owner_obj.name+'#'+code_owner_obj.discriminator+') created the personal invite code this member used to join.'
                else: invite_note = 'An unknown user with ID '+str(code_owner_id)+' created the personal invite code this member used to join.'

                ret_data = []
                b_field = {}
                b_field['name'] = 'Invited by'
                b_field['value'] = invite_note
                b_field['inline'] = False
                ret_data.append(b_field)

    return ret_data


async def member_join(member):
    use_server_id = await __main__.hash_server_id(member.server.id)
    use_member_id = await __main__.hash_member_id(member.server.id,member.id)

    used_code = __main__.db.cursor()
    used_code.execute("SELECT * FROM users WHERE server_id=? AND user_id=?",(use_server_id,use_member_id,))
    use_inv_code = ''
    for row in used_code:
        use_inv_code = await __main__.decrypt_data(row['inv_used'])

    if(use_inv_code != False and use_inv_code != "" and use_inv_code.lower() != "unknown"):
        chk_invs = __main__.db.cursor()
        chk_invs.execute("SELECT * FROM invites WHERE server_id=? AND inv_code=? AND inv_used='0'",(use_server_id,use_inv_code,))
        chk_invs_count = 0
        code_owner_id = ''
        for row in chk_invs:
            chk_invs_count = chk_invs_count + 1
            code_owner_id = await __main__.decrypt_data(row['stored_user_id'])

        if(chk_invs_count == 1):
            save_inv = __main__.db.cursor()
            save_inv.execute("UPDATE invites SET inv_used='1' WHERE server_id=? AND inv_code=? AND inv_used=0",(use_server_id,use_inv_code,))
            __main__.db.commit()

            if(code_owner_id != "" and code_owner_id != False):
                code_owner_obj = await __main__.find_user(member.server,'<@'+code_owner_id+'>',True)
                if(code_owner_obj != False):
                    try:
                        await __main__.client.send_message(code_owner_obj,'Your friend '+member.display_name+' just connected to '+member.server.name+'.')
                        alerted_member = True
                    except: alerted_member = False


async def member_remove(member):
    use_server_id = await __main__.hash_server_id(member.server.id)
    use_member_id = await __main__.hash_member_id(member.server.id,member.id)

    chk_invs = __main__.db.cursor()
    chk_invs.execute("SELECT * FROM invites WHERE server_id=? AND user_id=? AND inv_used='0'",(use_server_id,use_member_id,))
    chk_invs_count = 0
    time_now = await __main__.current_timestamp()
    active_invs = False
    for row in chk_invs:
        chk_exp = int(row['inv_expiry'])
        if(chk_exp == 0 or chk_exp > time_now):
            chk_invs_count = chk_invs_count + 1
            active_invs = True
            use_inv_code = row['inv_code']

            try:
                get_invite = await __main__.client.get_invite(use_inv_code)
            except: get_invite = False

            if(get_invite != False):
                try:
                    await __main__.client.delete_invite(get_invite)
                    del_invite = True
                except: del_invite = False

            save_inv = __main__.db.cursor()
            save_inv.execute("DELETE FROM invites WHERE server_id=? AND user_id=? AND inv_code=? AND inv_used=0",(use_server_id,use_member_id,use_inv_code,))
            __main__.db.commit()

    if(active_invs == True):
        await __main__.update_server_invites(message.server)
        inv_log_channel = await __main__.bot_use_channel(member.server,'invite','invite_log_channel')
        if(inv_log_channel != False):
            await __main__.client.send_message(inv_log_channel,'I have revoked all ('+str(chk_invs_count)+') of '+member.display_name+'\'s ('+member.name+'#'+member.discriminator+') active personal invite codes because they are no longer on the server.')


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
