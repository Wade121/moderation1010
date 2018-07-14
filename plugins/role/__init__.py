#!/usr/bin/python

import __main__

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Roles'
    help_info['description'] = 'Add or remove roles from yourself.'
    return help_info


async def help_section():
    help_info = {}


    cmd_name = 'role'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'make_public'
    help_entry['args'] = 'role_name'
    help_entry['description'] = 'Allow members to add or remove role_name from themselves.'
    help_entry['perm_name'] = 'set_public_roles'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'stop_public'
    help_entry['args'] = 'role_name'
    help_entry['description'] = 'Stop members to adding or removing role_name from themselves.'
    help_entry['perm_name'] = 'set_public_roles'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'list'
    help_entry['args'] = ''
    help_entry['description'] = 'List the roles available to choose from.'
    help_entry['perm_name'] = 'set_own_roles'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add'
    help_entry['args'] = 'role_name, role_name, role_name...'
    help_entry['description'] = 'Add one or more of the available roles to yourself.'
    help_entry['perm_name'] = 'set_own_roles'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'remove'
    help_entry['args'] = 'role_name, role_name, role_name...'
    help_entry['description'] = 'Remove one or more of the available roles from yourself.'
    help_entry['perm_name'] = 'set_own_roles'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'set_public_roles'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')

    this_perm = 'set_own_roles'
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

async def server_connected(server): pass

#===================================================================================================================
#MESSAGE EVENTS

async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)
    if(message.content.startswith(bot_cmd_char+'role')):
        proc_msg = await __main__.get_cmd_args(message.content,2)
        proc_msg_length = len(proc_msg)

        if(proc_msg_length >= 3 or proc_msg[1] == "list"):

            public_role_list = await __main__.get_config('public_roles',message.server,'role')
            if(public_role_list == False): public_role_list = []

            if(proc_msg[1] != "list" and proc_msg[1] != "add" and proc_msg[1] != "remove"):
                role_name = proc_msg[2]
                role_id = await __main__.find_role_arg(message.server,role_name)
            else:
                role_id = True

            if(role_id != False):
                if(proc_msg[1] != "list"): role_name = await __main__.role_name_from_id(role_id,message.server)

                if(proc_msg[1] == "make_public"):
                    chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'role','set_public_roles',True)
                    if(chk_user_perm == True):
                        if(role_id in public_role_list):
                            await __main__.client.send_message(message.channel,'That role is already public <@'+message.author.id+'>')
                        else:
                            public_role_list.append(role_id)
                            await __main__.set_config('public_roles',message.server,'role',public_role_list)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, the role "'+role_name+'" is now available for public use.')


                if(proc_msg[1] == "stop_public"):
                    chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'role','set_public_roles',True)
                    if(chk_user_perm == True):
                        if(role_id not in public_role_list):
                            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that role is already not available for public use.')
                        else:
                            public_role_list.remove(role_id)
                            await __main__.set_config('public_roles',message.server,'role',public_role_list)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, the role "'+role_name+'" is no longer available for public use.')


                if(proc_msg[1] == "list"):
                    chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'role','set_own_roles',True)
                    if(chk_user_perm == True):
                        icon_url = message.author.avatar_url
                        if(icon_url == None or icon_url == ""): icon_url = message.author.default_avatar_url

                        embed_description = 'Sorry, there aren\'t any roles available for you to use at the moment.'
                        if(len(public_role_list) > 0):
                            embed_description = 'To add a role run `'+bot_cmd_char+'role add ROLE-NAME`'
                            embed_description = embed_description+'\nTo remove a role run `'+bot_cmd_char+'role remove ROLE-NAME`'
                            embed_description = embed_description+'\n\nYou can also add or remove multiple roles at once by separating them with commas.'
                        em = __main__.discord.Embed(title='Server roles', description=embed_description, colour=3447003)
                        em.set_author(name=message.author.display_name, icon_url=icon_url)
                        em.set_thumbnail(url=icon_url)
                        build_roles_got = ''
                        build_roles_available = ''

                        #for this_role in public_role_list:
                        for serv_role in message.server.roles:
                            if(serv_role.id in public_role_list):
                                this_role = serv_role.id
                                user_has_role = await __main__.has_role(message.author.id,this_role,message.server)
                                role_name = await __main__.role_name_from_id(this_role,message.server)
                                if(user_has_role == True):
                                    build_roles_got = build_roles_got+'**-** '+role_name+'\n'
                                else:
                                    build_roles_available = build_roles_available+'**-** '+role_name+'\n'

                        if(build_roles_got == ""): build_roles_got = 'None'
                        if(build_roles_available == ""): build_roles_available = 'None'
                        em.add_field(name="Roles you have",value=build_roles_got,inline=True)
                        em.add_field(name="Roles available",value=build_roles_available,inline=True)
                        await __main__.client.send_message(message.author, embed=em)

                if(proc_msg[1] == "add"):
                    chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'role','set_own_roles',True)
                    if(chk_user_perm == True):
                        if(len(public_role_list) > 0):
                            use_role_list = proc_msg[2]
                            use_role_list = use_role_list.replace(', ',',')
                            use_role_list = use_role_list.split(',')
                            use_role_list_length = len(use_role_list)

                            if(use_role_list_length > 0):
                                use_role_list_length = use_role_list_length - 1
                                rl_run = 0
                                success_roles = ''
                                failed_roles = ''
                                while(rl_run <= use_role_list_length):
                                    this_role_name = use_role_list[rl_run]
                                    this_role_id = await __main__.find_role_arg(message.server,this_role_name)
                                    if(this_role_id != False and this_role_id in public_role_list):
                                        this_role_name = await __main__.role_name_from_id(this_role_id,message.server)
                                        if(success_roles != ""): success_roles = success_roles+', '
                                        success_roles = success_roles+'"'+this_role_name+'"'
                                        user_has_role = await __main__.has_role(message.author.id,this_role_id,message.server)
                                        await __main__.asyncio.sleep(0.3)
                                        if(user_has_role == False): await __main__.user_add_role(message.author.id,this_role_id,message.server)
                                    else:
                                        if(failed_roles != ""): failed_roles = failed_roles+', '
                                        failed_roles = failed_roles+'"'+this_role_name+'"'

                                    rl_run = rl_run + 1

                                if(success_roles != ""):
                                    if(use_role_list_length >= 1):
                                        role_conf_msg = 'Okay <@'+message.author.id+'>, I\'ve added the roles '+success_roles+' to your profile.'
                                    else: role_conf_msg = 'Okay <@'+message.author.id+'>, I\'ve added the role '+success_roles+' to your profile.'
                                    if(failed_roles != ""): role_conf_msg = role_conf_msg+' But I couldn\'t find the roles '+failed_roles+'.'
                                else:
                                    if(use_role_list_length >= 1):
                                        role_conf_msg = 'Sorry <@'+message.author.id+'>, I couldn\'t find these roles: '+failed_roles+'.'
                                    else: role_conf_msg = 'Sorry <@'+message.author.id+'>, I couldn\'t find the role '+failed_roles+'.'

                                await __main__.client.send_message(message.channel,role_conf_msg)

                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify one or more roles to add.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, there are no roles available for public use.')



                if(proc_msg[1] == "remove"):
                    chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'role','set_own_roles',True)
                    if(chk_user_perm == True):
                        if(len(public_role_list) > 0):
                            use_role_list = proc_msg[2]
                            use_role_list = use_role_list.replace(', ',',')
                            use_role_list = use_role_list.split(',')
                            use_role_list_length = len(use_role_list)

                            if(use_role_list_length > 0):
                                use_role_list_length = use_role_list_length - 1
                                rl_run = 0
                                success_roles = ''
                                failed_roles = ''
                                while(rl_run <= use_role_list_length):
                                    this_role_name = use_role_list[rl_run]
                                    this_role_id = await __main__.find_role_arg(message.server,this_role_name)
                                    if(this_role_id != False and this_role_id in public_role_list):
                                        this_role_name = await __main__.role_name_from_id(this_role_id,message.server)
                                        if(success_roles != ""): success_roles = success_roles+', '
                                        success_roles = success_roles+'"'+this_role_name+'"'
                                        user_has_role = await __main__.has_role(message.author.id,this_role_id,message.server)
                                        await __main__.asyncio.sleep(0.3)
                                        if(user_has_role == True): await __main__.user_remove_role(message.author.id,this_role_id,message.server)
                                    else:
                                        if(failed_roles != ""): failed_roles = failed_roles+', '
                                        failed_roles = failed_roles+'"'+this_role_name+'"'

                                    rl_run = rl_run + 1

                                if(success_roles != ""):
                                    if(use_role_list_length >= 1):
                                        role_conf_msg = 'Okay <@'+message.author.id+'>, I\'ve removed the roles '+success_roles+' from your profile.'
                                    else: role_conf_msg = 'Okay <@'+message.author.id+'>, I\'ve removed the role '+success_roles+' from your profile.'
                                    if(failed_roles != ""): role_conf_msg = role_conf_msg+' But I couldn\'t find the roles '+failed_roles+'.'
                                else:
                                    if(use_role_list_length >= 1):
                                        role_conf_msg = 'Sorry <@'+message.author.id+'>, I couldn\'t find these roles: '+failed_roles+'.'
                                    else: role_conf_msg = 'Sorry <@'+message.author.id+'>, I couldn\'t find the role '+failed_roles+'.'

                                await __main__.client.send_message(message.channel,role_conf_msg)

                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify one or more roles to remove.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, there are no roles available for public use.')

            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a role called "'+role_name+'".')
        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify both an action to take and a role name.')

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

async def role_delete(role):
    public_role_list = await __main__.get_config('public_roles',role.server,'role')
    if(public_role_list == False): public_role_list = []

    if(role.id in public_role_list):
        public_role_list.remove(role_id)
        await __main__.set_config('public_roles',role.server,'role',public_role_list)

async def role_update(before,after): pass

#===================================================================================================================
#EMOJI LIST EVENTS

async def emoji_list_update(before,after): pass

#===================================================================================================================
#GROUP CHAT EVENTS

async def group_join(channel,user): pass

async def group_remove(channel,user): pass
