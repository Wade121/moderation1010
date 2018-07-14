#!/usr/bin/python

import __main__

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'User management'
    help_info['description'] = 'See information about members, log notes and warnings. Kick, banish or put them into timeout.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'set'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'user_log_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Set which channel is used to output logs and notifications about users.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'timeout_add_role'
    help_entry['args'] = 'role_name'
    help_entry['description'] = 'Set which role is applied when a member is placed into timeout. This is reversed when a member is taken out of timeout'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'timeout_remove_role'
    help_entry['args'] = 'role_name'
    help_entry['description'] = 'Set which role is removed when a member is placed into timeout, if set, a member must have this role in order to be placed into timeout. This is reversed when a member is taken back out of timeout.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'info'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'member_name'
    help_entry['description'] = 'View the info record for member_name.'
    help_entry['perm_name'] = 'view_info'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'note'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'list'
    help_entry['args'] = 'member_name'
    help_entry['description'] = 'List the notes associated with member_name.'
    help_entry['perm_name'] = 'list_notes'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add'
    help_entry['args'] = 'member_name note_text'
    help_entry['description'] = 'Create a new note with note_text about member_name.'
    help_entry['perm_name'] = 'log_notes'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'remove'
    help_entry['args'] = 'member_name note_id'
    help_entry['description'] = 'Delete the note with note_id about member_name.'
    help_entry['perm_name'] = 'del_notes'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'warning'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'list'
    help_entry['args'] = 'member_name'
    help_entry['description'] = 'List the warnings associated with member_name.'
    help_entry['perm_name'] = 'list_warnings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add'
    help_entry['args'] = 'member_name note_text'
    help_entry['description'] = 'Create a new warning with note_text about member_name.'
    help_entry['perm_name'] = 'log_warnings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'remove'
    help_entry['args'] = 'member_name note_id'
    help_entry['description'] = 'Delete the warning with note_id about member_name.'
    help_entry['perm_name'] = 'del_warnings'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'ban'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'member_name ban_reason'
    help_entry['description'] = 'Ban member name from the server permanently and log the ban_reason.'
    help_entry['perm_name'] = 'ban_members'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'banpurge'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'member_name ban_reason'
    help_entry['description'] = 'Ban member name from the server permanently, purge all posts they made on the server in the last week and log the ban_reason.'
    help_entry['perm_name'] = 'ban_members'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'unban'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'member_name unban_reason'
    help_entry['description'] = 'Unan member name and log the unban_reason.'
    help_entry['perm_name'] = 'unban_members'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'kick'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'member_name kick_reason'
    help_entry['description'] = 'Kick member name from the server and log the kick_reason.'
    help_entry['perm_name'] = 'kick_members'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'timeout'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = '@someuser'
    help_entry['description'] = 'Puts @someuser into timeout to isolate them from the other channels on the server.'
    help_entry['perm_name'] = 'timeout_members'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'timein'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = '@someuser'
    help_entry['description'] = 'Takes @someuser out of timeout.'
    help_entry['perm_name'] = 'timeout_members'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}
 
    this_perm = 'kick_members'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')
 
    this_perm = 'ban_members'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')
 
    this_perm = 'unban_members'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')
 
    this_perm = 'timeout_members'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')
 
    this_perm = 'log_notes'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')
 
    this_perm = 'list_notes'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')
 
    this_perm = 'del_notes'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')
 
    this_perm = 'log_warnings'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')
 
    this_perm = 'list_warnings'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')
 
    this_perm = 'del_warnings'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')

    this_perm = 'view_info'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')

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


async def user_info(server_obj=None,interact_user=None,post_to=None,head_msg=""):
    if(interact_user != None and post_to != None):

        use_server_id = await __main__.hash_server_id(server_obj.id)
        use_member_id = await __main__.hash_member_id(server_obj.id,interact_user.id)

        icon_url = interact_user.avatar_url
        if(icon_url == None or icon_url == ""): icon_url = interact_user.default_avatar_url

        em = __main__.discord.Embed(title=interact_user.display_name+' member record', description='User ID '+interact_user.id, colour=3447003)
        em.set_author(name=interact_user.display_name, icon_url=icon_url)
        em.set_thumbnail(url=icon_url)

        try:
            user_status = 'Offline'
            if(str(interact_user.status) == "online"): user_status = 'Online'
            if(str(interact_user.status) == "dnd"): user_status = 'Do not disturb'
            if(str(interact_user.status) == "idle"): user_status = 'Idle'
        except: user_status = 'Unknown'

        try:
            mem_roles = ''
            for role in interact_user.roles:
                if(mem_roles != ""): mem_roles = mem_roles+', '
                if(str(role) != "@everyone"):
                    mem_roles = mem_roles+str(role)
        except: mem_roles = ''

        load_udb = __main__.db.cursor()
        load_udb.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
        inv_used = ''
        for row in load_udb:
            if(row['inv_used'] != None and row['inv_used'] != ""):
                dec_inv_used = await __main__.decrypt_data(row['inv_used'])
                if(dec_inv_used != False): inv_used = dec_inv_used
        if(inv_used != "" and inv_used.lower() != "unknown"):
            inv_used = inv_used+" (https://discord.gg/"+inv_used+")"
        else: inv_used = 'Unknown'


        load_notes = __main__.db.cursor()
        load_notes.execute("SELECT * FROM user_notes WHERE user_id=? AND server_id=? AND type != 'warning' ORDER BY datestamp DESC",(use_member_id,use_server_id,))
        load_notes_length = 0
        last_note = ''
        last_note_info = ''
        last_note_author = ''
        last_note_time = ''
        for row in load_notes:
            load_notes_length = load_notes_length + 1;
            if(last_note_info == ""):
                last_note_info = await __main__.decrypt_data(row['note'])
                last_note_author = await __main__.decrypt_data(row['logged_by'])
                last_note_time = await __main__.timestamp_to_date(row['datestamp'])

        if(last_note_info != ""):
            last_note_author = await __main__.find_user(server_obj,'<@'+last_note_author+'>',True)
            last_note = '**'+last_note_author.display_name+' wrote (**'+last_note_time+'**):**\n'+last_note_info


        load_notes = __main__.db.cursor()
        load_notes.execute("SELECT * FROM user_notes WHERE user_id=? AND server_id=? AND type = 'warning' ORDER BY datestamp DESC",(use_member_id,use_server_id,))
        load_warning_length = 0
        last_warning = ''
        last_warning_info = ''
        last_warning_author = ''
        last_warning_time = ''
        for row in load_notes:
            load_warning_length = load_warning_length + 1;
            if(last_warning_info == ""):
                last_warning_info = await __main__.decrypt_data(row['note'])
                last_warning_author = await __main__.decrypt_data(row['logged_by'])
                last_warning_time = await __main__.timestamp_to_date(row['datestamp'])

        if(last_warning_info != ""):
            last_warning_author = await __main__.find_user(server_obj,'<@'+last_warning_author+'>',True)
            last_warning = '**'+last_warning_author.display_name+' wrote (**'+last_warning_time+'**):**\n'+last_warning_info


        load_names = __main__.db.cursor()
        load_names.execute("SELECT * FROM user_names WHERE user_id=? AND server_id=? ORDER BY name ASC",(use_member_id,use_server_id,))
        load_names_length = 0
        name_list = ''
        for row in load_names:
            load_names_length = load_names_length + 1
            this_name = await __main__.decrypt_data(row['name'])
            if(this_name != interact_user.display_name):
                if(name_list != ""): name_list = name_list+', '
                name_list = name_list+this_name


        em.add_field(name="Joined Discord",value=interact_user.created_at.strftime("%a %d %b %Y %H:%M UTC 0"),inline=True)
        try:
            em.add_field(name="Joined server",value=interact_user.joined_at.strftime("%a %d %b %Y %H:%M UTC 0"),inline=True)
        except:
            em.add_field(name="Joined server",value='Not a member',inline=True)
        em.add_field(name="User name",value=interact_user.name+'#'+interact_user.discriminator,inline=True)
        em.add_field(name="Current nick",value=interact_user.display_name,inline=True)
        em.add_field(name="Invite used",value=inv_used,inline=False)
        em.add_field(name="Notes",value=str(load_notes_length),inline=True)
        em.add_field(name="Warnings",value=str(load_warning_length),inline=True)
        if(last_note != ""): em.add_field(name="Latest note",value=last_note,inline=False)
        if(last_warning != ""): em.add_field(name="Latest warning",value=last_warning,inline=False)
        if(name_list != ""): em.add_field(name="AKA",value=name_list,inline=False)
        em.add_field(name="Status",value=user_status,inline=True)
        try:
            em.add_field(name="Playing",value=str(interact_user.game),inline=True)
        except:
            em.add_field(name="Playing",value='Unknown',inline=True)

        if(mem_roles != ""): em.add_field(name="Roles",value=mem_roles,inline=False)


        u_groups = await __main__.get_user_groups(server_obj,interact_user.id)
        list_u_groups = ''
        if(len(u_groups) > 0):
            for ug in u_groups:
                if(list_u_groups != ""): list_u_groups = list_u_groups+', '
                list_u_groups = list_u_groups+ug
        if(list_u_groups == ""): list_u_groups = 'None'
        if(list_u_groups != ""): em.add_field(name="Permission groups",value=list_u_groups,inline=False)


        plugin_contrib = await __main__.trigger_active_plugins(server_obj,'user_info_data',server_obj,interact_user)
        if(plugin_contrib != False):
            for pc in plugin_contrib:
                if(plugin_contrib[pc] != False):
                    for info_data in plugin_contrib[pc]:
                        em.add_field(name=info_data['name'],value=info_data['value'],inline=info_data['inline'])

        return await __main__.client.send_message(post_to,head_msg,embed=em)



async def user_del_log(log_type=None,user=None,message=None,del_log=None):
    if(user != None and message != None):

        load_log_type = " != 'warning'"
        if(log_type == "warning"): load_log_type = " = 'warning'"

        use_server_id = await __main__.hash_server_id(message.server.id)
        use_member_id = await __main__.hash_member_id(message.server.id,user.id)

        load_notes = __main__.db.cursor()
        load_notes.execute("SELECT * FROM user_notes WHERE type"+load_log_type+" AND user_id=? AND server_id=? AND id=?",(use_member_id,use_server_id,del_log,))
        load_notes_length = 0
        for row in load_notes:
            load_notes_length = load_notes_length + 1
            note_time = await __main__.timestamp_to_date(row['datestamp'])
            logged_by = await __main__.decrypt_data(row['logged_by'])
            note_author = await __main__.find_user(message.server,'<@'+logged_by+'>',True)
            note_txt = await __main__.decrypt_data(row['note'])
            note_type = row['type']

        if(load_notes_length == 1):
            del_note = __main__.db.cursor()
            del_note.execute("DELETE FROM user_notes WHERE type"+load_log_type+" AND user_id=? AND server_id=? AND id=?",(use_member_id,use_server_id,int(del_log),))
            __main__.db.commit()

            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve deleted that note for you.')
            user_log_channel = await __main__.bot_use_channel(message.server,'users','user_log_channel')
            if(user_log_channel != False):
                await __main__.client.send_message(user_log_channel,message.author.display_name+' has deleted a '+note_type+' note against '+user.display_name+', originally written by '+note_author.display_name+' on '+note_time+' which said:\n\n'+note_txt)
        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a '+log_type+' note with ID "'+del_log+'"')


async def user_show_log(log_type=None,user=None,message=None):
    if(log_type != None and user != None and message != None):
        use_server_id = await __main__.hash_server_id(message.server.id)
        use_member_id = await __main__.hash_member_id(message.server.id,user.id)

        load_log_type = " != 'warning'"
        if(log_type == "warning"): load_log_type = " = 'warning'"

        load_notes = __main__.db.cursor()
        load_notes.execute("SELECT * FROM user_notes WHERE type"+load_log_type+" AND user_id=? AND server_id=?",(use_member_id,use_server_id,))
        load_notes_length = 0
        for row in load_notes:
            load_notes_length = load_notes_length + 1

        load_notes_descript = 'Found '+str(load_notes_length)+' '+log_type+' notes.'

        interact_user = await __main__.find_user(message.server,'<@'+user.id+'>',True)
        if(interact_user != False):
            icon_url = interact_user.avatar_url
            if(icon_url == None or icon_url == ""): icon_url = interact_user.default_avatar_url
            title_name = interact_user.display_name
        else:
            icon_url = ''
            title_name = '<@'+user+'>'

        em = __main__.discord.Embed(title='Logged '+log_type+' notes', description=load_notes_descript, colour=3447003)
        em.set_author(name=title_name, icon_url=icon_url)
        if(icon_url != ""): em.set_thumbnail(url=icon_url)

        load_notes = __main__.db.cursor()
        load_notes.execute("SELECT * FROM user_notes WHERE type"+load_log_type+" AND user_id=? AND server_id=? ORDER BY datestamp DESC",(use_member_id,use_server_id,))
        build_note_count = 0
        for row in load_notes:
            note_time = await __main__.timestamp_to_date(row['datestamp'])
            note_text = await __main__.decrypt_data(row['note'])
            logged_by = await __main__.decrypt_data(row['logged_by'])
            note_author = await __main__.find_user(message.server,'<@'+logged_by+'>',True)
            if(note_author != False):
                use_note_author = note_author.display_name
            else: use_note_author = '<@'+row['logged_by']+'>'

            em.add_field(name=str(row['id'])+' - '+use_note_author+' ('+note_time+')',value=note_text,inline=False)
            build_note_count = build_note_count + 1
            if(build_note_count >= 23): break

        await __main__.client.send_message(message.channel,embed=em)


async def user_log(log_type=None,server_obj=None,user_id=None,mod_id=None,note=None,orig_msg=None,no_confirm=False):
    if(note != None and note != ""):
        time_now = await __main__.current_timestamp()

        use_server_id = await __main__.hash_server_id(server_obj.id)
        use_member_id = await __main__.hash_member_id(server_obj.id,user_id)
        save_member_id = await __main__.encrypt_data(user_id)
        save_logged_by = await __main__.encrypt_data(mod_id)
        save_note = await __main__.encrypt_data(note)

        cursor = __main__.db.cursor()
        cursor.execute("INSERT INTO user_notes (user_id,stored_user_id,server_id,logged_by,type,note,datestamp) VALUES (?,?,?,?,?,?,?)",(use_member_id,save_member_id,use_server_id,save_logged_by,log_type,save_note,time_now))
        __main__.db.commit()
        if(orig_msg != None):
            if(no_confirm == False): await __main__.client.send_message(orig_msg.channel,'Okay <@'+mod_id+'>, I\'ve saved that '+log_type+' note about <@'+user_id+'>.')

            user_log_channel = await __main__.bot_use_channel(server_obj,'users','user_log_channel')
            if(user_log_channel != False):
                await __main__.client.send_message(user_log_channel,orig_msg.author.display_name+' has added a new '+log_type+' note against <@'+user_id+'>, which says:\n\n'+note)


async def user_ban(server=None,ban_user=None,mod_user=None,note=None):
    ban_notify = mod_user.display_name+' banned '+ban_user.display_name+' from the server permanently'
    if(note != None and note != ""): ban_notify = ban_notify+' because: '+note

    ban_reason = 'Banned this member from the server permanently'
    if(note != None and note != ""):
        ban_reason = ban_reason+' because: '+note
    await user_log('ban',server,ban_user.id,mod_user.id,ban_reason)

    user_log_channel = await __main__.bot_use_channel(server,'users','user_log_channel')
    if(user_log_channel != False):
        await __main__.client.send_message(user_log_channel,ban_notify)

    await __main__.client.ban(ban_user,0)


async def user_unban(server=None,ban_user=None,mod_user=None,note=None):
    ban_notify = mod_user.display_name+' unbanned '+ban_user.display_name+' from the server'
    if(note != None and note != ""): ban_notify = ban_notify+' because: '+note

    ban_reason = 'Unbanned this member from the server'
    if(note != None and note != ""):
        ban_reason = ban_reason+' because: '+note
    await user_log('unban',server,ban_user.id,mod_user.id,ban_reason)

    user_log_channel = await __main__.bot_use_channel(server,'users','user_log_channel')
    if(user_log_channel != False):
        await __main__.client.send_message(user_log_channel,ban_notify)

    await __main__.client.unban(message.server,ban_user)


async def user_banpurge(server=None,ban_user=None,mod_user=None,note=None):
    ban_notify = mod_user.display_name+' banned '+ban_user.display_name+' from the server permanently and purged all posts made within the last week'
    if(note != None and note != ""): ban_notify = ban_notify+' because: '+note

    ban_reason = 'Banned this member from the server permanently and purged all posts made within the last week'
    if(note != None and note != ""):
        ban_reason = ban_reason+' because: '+note
    await user_log('ban',server,ban_user.id,mod_user.id,ban_reason)

    user_log_channel = await __main__.bot_use_channel(server,'users','user_log_channel')
    if(user_log_channel != False):
        await __main__.client.send_message(user_log_channel,ban_notify)

    await __main__.client.ban(ban_user,7)


async def user_kick(server=None,ban_user=None,mod_user=None,note=None):
    ban_notify = mod_user.display_name+' kicked '+ban_user.display_name+' from the server'
    if(note != None and note != ""): ban_notify = ban_notify+' because: '+note

    ban_reason = 'Kicked this member from the server'
    if(note != None and note != ""):
        ban_reason = ban_reason+' because: '+note
    await user_log('kick',server,ban_user.id,mod_user.id,ban_reason)

    user_log_channel = await __main__.bot_use_channel(server,'users','user_log_channel')
    if(user_log_channel != False):
        await __main__.client.send_message(user_log_channel,ban_notify)

    await __main__.client.kick(ban_user)







async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)
    proc_msg = await __main__.get_cmd_args(message.content)
    proc_msg_length = len(proc_msg)

    if(message.content.startswith(bot_cmd_char+'set')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)

        if(proc_msg[1] == "user_log_channel"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    await __main__.bot_set_channel(message.server,'users','user_log_channel',find_channel.id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will now use that channel for posting user management messages.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')

        if(proc_msg[1] == "timeout_add_role"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_role_arg(message.server,proc_msg[2])
                if(find_channel != False):
                    await __main__.set_config('timeout_add_role',message.server,'users',find_channel)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will add that role to people in order to put them into timeout.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a role called "'+proc_msg[2]+'"')

        if(proc_msg[1] == "timeout_remove_role"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_role_arg(message.server,proc_msg[2])
                if(find_channel != False):
                    await __main__.set_config('timeout_remove_role',message.server,'users',find_channel)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will remove that role from people when putting them into timeout.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a role called "'+proc_msg[2]+'"')


    if(message.content.startswith(bot_cmd_char+'timeout')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','timeout_members',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content,2)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 2):
                interact_user = await __main__.find_user(message.server,proc_msg[1],True)
                if(interact_user != False):
                    to_role = await __main__.get_config('timeout_add_role',message.server,'users')
                    if(to_role != False):
                        timeout_okay = True
                        to_rem_role = await __main__.get_config('timeout_remove_role',message.server,'users')
                        if(to_rem_role != False): timeout_okay = await __main__.has_role(interact_user.id,to_rem_role,message.server)

                        if(timeout_okay == True):
                            if(to_rem_role != False):
                                await __main__.user_remove_role(interact_user.id,to_rem_role,message.server)
                                await __main__.asyncio.sleep(0.5)
                            await __main__.user_add_role(interact_user.id,to_role,message.server)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve put '+interact_user.display_name+' into timeout.')

                            user_log_channel = await __main__.bot_use_channel(message.server,'users','user_log_channel')
                            if(user_log_channel != False):
                                await __main__.client.send_message(user_log_channel,message.author.display_name+' has put <@'+interact_user.id+'> into timeout.')

                            add_note = 'Put this member into timeout'
                            if(proc_msg_length == 3 and proc_msg[2] != ""): add_note = add_note+' because: '+proc_msg[2]
                            await user_log('general',message.server,interact_user.id,message.author.id,add_note,message,True)
                            
                            await __main__.client.delete_message(message)

                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I can\'t put that member into timeout because they do not have the required role to remove.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I can\'t put any members into timeout because my timeout role has not been set.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[1]+'"')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a member to put into timeout.')

    
    if(message.content.startswith(bot_cmd_char+'timein')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','timeout_members',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content,1)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 2):
                interact_user = await __main__.find_user(message.server,proc_msg[1],True)
                if(interact_user != False):
                    to_role = await __main__.get_config('timeout_add_role',message.server,'users')
                    if(to_role != False):

                        to_rem_role = await __main__.get_config('timeout_remove_role',message.server,'users')
                        if(to_rem_role != False):
                            await __main__.user_add_role(interact_user.id,to_rem_role,message.server)
                            await __main__.asyncio.sleep(0.5)
                        await __main__.user_remove_role(interact_user.id,to_role,message.server)
                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve taken '+interact_user.display_name+' out of timeout.')

                        user_log_channel = await __main__.bot_use_channel(message.server,'users','user_log_channel')
                        if(user_log_channel != False):
                            await __main__.client.send_message(user_log_channel,message.author.display_name+' has taken <@'+interact_user.id+'> out of timeout.')

                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I can\'t remove any members from timeout because my timeout role has not been set.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[1]+'"')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a member to take out of timeout.')


    if(message.content.startswith(bot_cmd_char+'ban')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','ban_members',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content,2)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 2):
                interact_user = await __main__.find_user(message.server,proc_msg[1],True)
                if(interact_user != False):
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, banning <@'+interact_user.id+'> permanently.')
                    use_note = ''
                    if(proc_msg_length >= 3): use_note = proc_msg[2]
                    await user_ban(message.server,interact_user,message.author,use_note)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[1]+'"')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a member to ban and also optionally a reason for doing so.')


    if(message.content.startswith(bot_cmd_char+'unban')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','unban_members',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content,2)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 2):
                interact_user = await __main__.find_user(message.server,proc_msg[1],True)
                if(interact_user != False):
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have unbanned <@'+interact_user.id+'>.')
                    use_note = ''
                    if(proc_msg_length >= 3): use_note = proc_msg[2]
                    await user_unban(message.server,interact_user,message.author,use_note)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[1]+'"')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a member to unban and also optionally a reason for doing so.')


    if(message.content.startswith(bot_cmd_char+'banpurge')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','ban_members',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content,2)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 2):
                interact_user = await __main__.find_user(message.server,proc_msg[1],True)
                if(interact_user != False):
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, banning <@'+interact_user.id+'> permanently and purging all posts made within the last week.')
                    use_note = ''
                    if(proc_msg_length >= 3): use_note = proc_msg[2]
                    await user_banpurge(message.server,interact_user,message.author,use_note)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[1]+'"')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a member to ban and also optionally a reason for doing so.')


    if(message.content.startswith(bot_cmd_char+'kick')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','kick_members',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content,2)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 2):
                interact_user = await __main__.find_user(message.server,proc_msg[1],True)
                if(interact_user != False):
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, kicking <@'+interact_user.id+'> from the server.')
                    use_note = ''
                    if(proc_msg_length >= 3): use_note = proc_msg[2]
                    await user_kick(message.server,interact_user,message.author,use_note)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[1]+'"')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a member to kick and also optionally a reason for doing so.')






    if(message.content.startswith(bot_cmd_char+'info')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','view_info',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 2):
                interact_user = await __main__.find_user(message.server,proc_msg[1],True)
                if(interact_user != False):
                    await user_info(message.server,interact_user,message.channel)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[1]+'"')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a member to look up.')


    if(message.content.startswith(bot_cmd_char+'note')):
        proc_msg = await __main__.get_cmd_args(message.content,3)
        proc_msg_length = len(proc_msg)

        chk_user_perm = False
        if(proc_msg[1] == "list"): chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','list_notes',True)
        if(proc_msg[1] == "add"): chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','log_notes',True)
        if(proc_msg[1] == "remove"): chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','del_notes',True)

        if(chk_user_perm == True):
            if(proc_msg_length >= 2):
                interact_user = await __main__.find_user(message.server,proc_msg[2],True)
                if(interact_user != False):

                    if(proc_msg[1] == "list"):
                        await user_show_log('general',interact_user,message)

                    if(proc_msg[1] == "add"):
                        if(proc_msg_length == 4):
                            await user_log('general',message.server,interact_user.id,message.author.id,proc_msg[3],message)
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must provide a note to add.')

                    if(proc_msg[1] == "remove"):
                        if(proc_msg_length == 4):
                            await user_del_log('general',interact_user,message,proc_msg[3])
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must provide the ID of the note you want to remove.')

                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[2]+'"')


    if(message.content.startswith(bot_cmd_char+'warning')):
        proc_msg = await __main__.get_cmd_args(message.content,3)
        proc_msg_length = len(proc_msg)

        chk_user_perm = False
        if(proc_msg[1] == "list"): chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','list_warnings',True)
        if(proc_msg[1] == "add"): chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','log_warnings',True)
        if(proc_msg[1] == "remove"): chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'users','del_warnings',True)

        if(chk_user_perm == True):
            if(proc_msg_length >= 2):
                interact_user = await __main__.find_user(message.server,proc_msg[2],True)
                if(interact_user != False):

                    if(proc_msg[1] == "list"):
                        await user_show_log('warning',interact_user,message)

                    if(proc_msg[1] == "add"):
                        if(proc_msg_length == 4):
                            await user_log('warning',message.server,interact_user.id,message.author.id,proc_msg[3],message)
                            await __main__.client.send_message(interact_user,'**You have been warned on '+message.server.name+'**\n'+proc_msg[3])
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must provide a warning to add.')

                    if(proc_msg[1] == "remove"):
                        if(proc_msg_length == 4):
                            await user_del_log('warning',interact_user,message,proc_msg[3])
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must provide the ID of the warning you want to remove.')

                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[2]+'"')







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

async def member_join(member):
    user_log_channel = await __main__.bot_use_channel(member.server,'users','user_log_channel')
    if(user_log_channel != False):
        await __main__.client.send_message(user_log_channel,member.display_name+' ('+member.name+'#'+member.discriminator+') has joined the server.')

async def member_remove(member):
    user_log_channel = await __main__.bot_use_channel(member.server,'users','user_log_channel')
    if(user_log_channel != False):
        await __main__.client.send_message(user_log_channel,member.display_name+' ('+member.name+'#'+member.discriminator+') has left the server.')

async def member_update(before,after): pass

async def member_voice_update(before,after): pass

async def member_ban(member):
    user_log_channel = await __main__.bot_use_channel(member.server,'users','user_log_channel')
    if(user_log_channel != False):
        await __main__.client.send_message(user_log_channel,member.display_name+' ('+member.name+'#'+member.discriminator+') has been banned.')

async def member_unban(server,user):
    user_log_channel = await __main__.bot_use_channel(server,'users','user_log_channel')
    if(user_log_channel != False):
        await __main__.client.send_message(user_log_channel,user.name+'#'+member.discriminator+' has been unbanned.')

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
