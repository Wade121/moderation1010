#!/usr/bin/python

import __main__

greeting_temp = {}
global gate_lurkers
gate_lurkers = {}

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Greetings and gated servers'
    help_info['description'] = 'Send greeting messages to new users or manage a gated community with approval and rejection commands.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'set'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'greeting_log_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Set the channel where the greeting logs will be displayed'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'greeting_mode'
    help_entry['args'] = 'new_mode'
    help_entry['description'] = 'Set the greeting mode, new_mode can either be "greet", "alert" or "off"'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'greeting_alert_role'
    help_entry['args'] = 'role_name'
    help_entry['description'] = 'Set the role to be alerted when a new member joins, can be either "off" or a role name.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'greeting_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Set the channel where the greeting message will be displayed'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'greeting_message'
    help_entry['args'] = 'new_message'
    help_entry['description'] = 'Set the greeting message content that is sent to new members, you can use [user] where their user name will be.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'set_continued'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'gate_approved_role'
    help_entry['args'] = 'role_name'
    help_entry['description'] = 'If this server is a gated community, set the role which is applied when new members are approved to join, role_name can either be the name of the role or "off".'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'gate_reject_account_age'
    help_entry['args'] = 'time_int time_scale'
    help_entry['description'] = 'If this server is a gated community, auto-rejects accounts which are younger than time_int time_scale from joining.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'gate_reject_lurker_time'
    help_entry['args'] = 'time_int time_scale'
    help_entry['description'] = 'If this server is a gated community, auto-rejects pending accounts which show no activity within time_int time_scale..'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'approved_greeting_mode'
    help_entry['args'] = 'new_mode'
    help_entry['description'] = 'Set the approved greeting mode, new_mode can either be "greet" or "off"'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'approved_greeting_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Set the channel where the approved greeting message will be displayed'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'approved_greeting_message'
    help_entry['args'] = 'new_message'
    help_entry['description'] = 'Set the approved greeting message content that is sent to newly approved members, you can use [user] where their user name will be.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'approve'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'member_name'
    help_entry['description'] = 'If this server is set as a gated community, this command will approve a new user to join by applying the appropriate role to them and logging their entry.'
    help_entry['perm_name'] = 'gatekeeper'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'reject'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'member_name rejection_reason'
    help_entry['description'] = 'If this server is set as a gated community, this command will reject entry of member_name and kick them from the server, then log the rejection_reason.'
    help_entry['perm_name'] = 'gatekeeper'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'change_settings'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')

    this_perm = 'gatekeeper'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('admins')

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

async def user_info_data(server,user):
    ret_data = False
    gate_approved_role = await __main__.get_config('gate_approved_role',server,'greet')
    use_server_id = await __main__.hash_server_id(server.id)
    use_member_id = await __main__.hash_member_id(server.id,user.id)

    if(gate_approved_role != False):
        chk_user = __main__.db.cursor()
        chk_user.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
        authorised = 0
        prev_authorised = 0
        rejected = 0
        found_user = False
        for row in chk_user:
            found_user = True
            if(row['authorised'] != None and row['authorised'] != ""): authorised = int(row['authorised'])
            if(row['prev_authorised'] != None and row['prev_authorised'] != ""): prev_authorised = int(row['prev_authorised'])
            if(row['rejected'] != None and row['rejected'] != ""): prev_authorised = int(row['rejected'])

        if(found_user == True):
            
            if(authorised == 0):
                has_base = await __main__.has_role(user.id,gate_approved_role,server)
                if(has_base == True):
                    authorised = 1
                    prev_authorised = 1
                    rejected = 0
                    upd_user = __main__.db.cursor()
                    upd_user.execute("UPDATE users SET authorised='1', prev_authorised='1', rejected='0' WHERE server_id=? AND user_id=?",(use_server_id,use_member_id,))
                    __main__.db.commit()

            if(authorised == 1):
                mem_status = 'Approved member'
            else:
                if(rejected == 1):
                    mem_status = 'Awaiting approval but has previously been **rejected** from entering the server'
                else:
                    if(prev_authorised == 1):
                        mem_status = 'Awaiting approval and has been an approved member on this server before'
                    else:
                        mem_status = 'New member awaiting approval to join the server'

            ret_data = []
            b_field = {}
            b_field['name'] = 'Membership status'
            b_field['value'] = mem_status
            b_field['inline'] = False
            ret_data.append(b_field)

    return ret_data





async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)

    if(message.content.startswith(bot_cmd_char+'set')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)

        if(proc_msg[1] == "greeting_log_channel"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    await __main__.bot_set_channel(message.server,'greet','greeting_log_channel',find_channel.id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will now use that channel for posting new member alerts.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')

        if(proc_msg[1] == "greeting_alert_role"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,2)
                proc_msg_length = len(proc_msg)

                find_role_id = False
                if(proc_msg[2] == "off"):
                    use_role_id = False
                else:
                    find_role = await __main__.find_role_arg(message.server,proc_msg[2])
                    if(find_role != False):
                        find_role_id = True
                        use_role_id = find_role

                if(find_role_id != False):
                    await __main__.set_config('greeting_alert_role',message.server,'greet',use_role_id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the greeting alert role to "'+proc_msg[2]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that is incorrect. You must specify either "off" or a valid role name.')

        if(proc_msg[1] == "greeting_mode"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                if(proc_msg[2] == "greet" or proc_msg[2] == "alert" or proc_msg[2] == "off"):
                    await __main__.set_config('greeting_mode',message.server,'greet',proc_msg[2])
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the greeting mode to '+proc_msg[2]+'.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, the greeting mode must be set to either "greet", "alert" or "off".')

        if(proc_msg[1] == "greeting_channel"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    #await __main__.bot_set_channel(message.server,'users','user_log_channel',find_channel.id)
                    await __main__.set_config('greeting_channel',message.server,'greet',find_channel.id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will now use that channel for posting greeting messages.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')

        if(proc_msg[1] == "greeting_message"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,2)
                proc_msg_length = len(proc_msg)
                if(proc_msg_length == 3):
                    await __main__.set_config('greeting_message',message.server,'greet',proc_msg[2])
                    test_greeting = proc_msg[2].replace('[user]','<@'+message.author.id+'>')
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have updated the greeting message, which will now like like this:')
                    await __main__.client.send_message(message.channel,test_greeting)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a message to send when greeting people.')


        if(proc_msg[1] == "approved_greeting_mode"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                if(proc_msg[2] == "greet" or proc_msg[2] == "off"):
                    await __main__.set_config('approved_greeting_mode',message.server,'greet',proc_msg[2])
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the approved greeting mode to '+proc_msg[2]+'.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, the approved greeting mode must be set to either "greet" or "off".')

        if(proc_msg[1] == "approved_greeting_channel"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    #await __main__.bot_set_channel(message.server,'users','user_log_channel',find_channel.id)
                    await __main__.set_config('approved_greeting_channel',message.server,'greet',find_channel.id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will now use that channel for posting approved greeting messages.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')

        if(proc_msg[1] == "approved_greeting_message"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,2)
                proc_msg_length = len(proc_msg)
                if(proc_msg_length == 3):
                    await __main__.set_config('approved_greeting_message',message.server,'greet',proc_msg[2])
                    test_greeting = proc_msg[2].replace('[user]','<@'+message.author.id+'>')
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have updated the approved greeting message, which will now like like this:')
                    await __main__.client.send_message(message.channel,test_greeting)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a message to send when greeting approved people.')


        if(proc_msg[1] == "gate_approved_role"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,2)
                proc_msg_length = len(proc_msg)

                valid_opt = False
                if(proc_msg[2] == "off"):
                    use_role_id = False
                    valid_opt = True
                else:
                    find_role = await __main__.find_role_arg(message.server,proc_msg[2])
                    if(find_role != False):
                        use_role_id = find_role
                        valid_opt = True

                if(valid_opt == True):
                    await __main__.set_config('gate_approved_role',message.server,'greet',use_role_id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the gate approved role to "'+proc_msg[2]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that is incorrect. You must specify either "off" or a valid role name.')
        
        
        if(proc_msg[1] == "gate_reject_account_age"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 4):
                    if(proc_msg[2] != "off"):
                        add_time = await __main__.cmd_time_args(proc_msg[2],proc_msg[3])
                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will auto-reject new member accounts which are younger than '+str(proc_msg[2])+' '+str(proc_msg[3])+'.')
                    else:
                        add_time = 0
                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will stop checking the age of new member accounts.')
                    await __main__.set_config('gate_reject_account_age',message.server,'greet',add_time)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the length of time which accounts must be older than to not be auto-rejected, or "off" to never auto-reject new accounts.')
        

        if(proc_msg[1] == "gate_reject_lurker_time"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','change_settings',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 4):
                    if(proc_msg[2] != "off"):
                        add_time = await __main__.cmd_time_args(proc_msg[2],proc_msg[3])
                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will auto reject new unapproved members who show no activity within '+str(proc_msg[2])+' '+str(proc_msg[3])+'.')
                    else:
                        add_time = 0
                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will not auto reject any inactive pending members.')
                    await __main__.set_config('gate_reject_lurker_time',message.server,'greet',add_time)
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the length of time to wait before auto-rejecting new members who have shown no activity.')



    if(message.content.startswith(bot_cmd_char+'approve')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','gatekeeper',True)
        if(chk_user_perm == True):
            gate_approved_role = await __main__.get_config('gate_approved_role',message.server,'greet')
            if(gate_approved_role != False):
                proc_msg = await __main__.get_cmd_args(message.content,1)
                proc_msg_length = len(proc_msg)
                if(proc_msg_length == 2):
                    this_user = await __main__.find_user(message.server,proc_msg[1],True)
                    if(this_user != False):
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        use_member_id = await __main__.hash_member_id(message.server.id,this_user.id)

                        chk_user = __main__.db.cursor()
                        chk_user.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                        prev_authorised = 0
                        for row in chk_user:
                            if(row['authorised'] != None and row['authorised'] != ""): prev_authorised = int(row['authorised'])

                        has_base = await __main__.has_role(this_user.id,gate_approved_role,message.server)
                        if(has_base == False and prev_authorised == 1): prev_authorised = 0

                        if(prev_authorised == 0):

                            await __main__.user_add_role(this_user.id,gate_approved_role,message.server)

                            chk_user.execute("UPDATE users SET authorised=?, prev_authorised=?, rejected=? WHERE user_id=? AND server_id=?",(1,1,0,use_member_id,use_server_id,))
                            __main__.db.commit()

                            save_note = 'Approved this user to join the server'
                            await __main__.trigger_active_plugin(message.server,'user_log','users','general',message.server,this_user.id,message.author.id,save_note,None)

                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, approving '+this_user.display_name+' to enter the server.')
                            await del_greeting_temp(message.server,this_user.id)

                            greeting_log_channel = await __main__.bot_use_channel(message.server,'greet','greeting_log_channel')
                            if(greeting_log_channel != False):
                                await __main__.client.send_message(greeting_log_channel,message.author.display_name+' has approved '+this_user.display_name+' ('+this_user.name+'#'+this_user.discriminator+') to join the server.')

                            approved_greeting_mode = await __main__.get_config('approved_greeting_mode',message.server,'greet')
                            if(approved_greeting_mode == "greet"):
                                #send greeting message
                                approved_greeting_channel = await __main__.get_config('approved_greeting_channel',message.server,'greet')
                                if(approved_greeting_channel != False):
                                    greet_channel = await __main__.channel_name_from_id(message.server,approved_greeting_channel,True)
                                    if(greet_channel != False):
                                        approved_greeting_message = await __main__.get_config('approved_greeting_message',message.server,'greet')
                                        if(approved_greeting_message != False):
                                            use_greeting_msg = approved_greeting_message.replace('[user]','<@'+this_user.id+'>')
                                            await __main__.client.send_message(greet_channel,use_greeting_msg)
                                        else:
                                            if(greeting_log_channel != False): await __main__.client.send_message(greeting_log_channel,'**ERROR:** The approved greeting message has not been set.')
                                    else:
                                        if(greeting_log_channel != False): await __main__.client.send_message(greeting_log_channel,'**ERROR:** The set approved greeting channel does not exist.')
                                else:
                                    if(greeting_log_channel != False): await __main__.client.send_message(greeting_log_channel,'**ERROR:** No approved greeting channel has been set.')


                            await __main__.client.delete_message(message)

                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that person is already an approved member.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find anybody called "'+proc_msg[1]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the name of the person you want to approve.')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I can\'t do that because the gate approved role has not been set.')


    if(message.content.startswith(bot_cmd_char+'reject')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'greet','gatekeeper',True)
        if(chk_user_perm == True):
            gate_approved_role = await __main__.get_config('gate_approved_role',message.server,'greet')
            if(gate_approved_role != False):
                proc_msg = await __main__.get_cmd_args(message.content,2)
                proc_msg_length = len(proc_msg)
                if(proc_msg_length >= 2):
                    this_user = await __main__.find_user(message.server,proc_msg[1],True)
                    if(this_user != False):
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        use_member_id = await __main__.hash_member_id(message.server.id,this_user.id)

                        chk_user = __main__.db.cursor()
                        chk_user.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                        prev_authorised = 0
                        for row in chk_user:
                            if(row['authorised'] != None and row['authorised'] != ""): prev_authorised = int(row['authorised'])

                        has_base = await __main__.has_role(this_user.id,gate_approved_role,message.server)
                        if(has_base == False and prev_authorised == 1): prev_authorised = 0

                        if(prev_authorised == 0):

                            chk_user.execute("UPDATE users SET authorised=?, prev_authorised=?, rejected=? WHERE user_id=? AND server_id=?",(0,0,1,use_member_id,use_server_id,))
                            __main__.db.commit()

                            save_note = 'Rejected this user from entering the server'
                            rej_note = '.'
                            if(proc_msg_length == 3): save_note = save_note+' because:\n'+proc_msg[2]
                            if(proc_msg_length == 3): rej_note = ' because:\n'+proc_msg[2]
                            await __main__.trigger_active_plugin(message.server,'user_log','users','general',message.server,this_user.id,message.author.id,save_note,None)

                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, rejecting '+this_user.display_name+' and removing them.')
                            await del_greeting_temp(message.server,this_user.id)

                            greeting_log_channel = await __main__.bot_use_channel(message.server,'greet','greeting_log_channel')
                            if(greeting_log_channel != False):
                                await __main__.client.send_message(greeting_log_channel,message.author.display_name+' has rejected '+this_user.display_name+' ('+this_user.name+'#'+this_user.discriminator+') from joining the server'+rej_note)

                            await __main__.client.kick(this_user)

                            await __main__.client.delete_message(message)

                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that person is already an approved member.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find anybody called "'+proc_msg[1]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the name of the person you want to reject.')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I can\'t do that because the gate approved role has not been set.')


async def message_new(message):
    if(message.server.id in gate_lurkers and message.author.id in gate_lurkers[message.server.id]):
        gate_lurkers[message.server.id][message.author.id] = await __main__.current_timestamp()

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

async def track_greeting_temp(server,user_id,msg_obj):
    if(server.id not in greeting_temp): greeting_temp[server.id] = {}
    if(user_id not in greeting_temp[server.id]): greeting_temp[server.id][user_id] = []
    greeting_temp[server.id][user_id].append(msg_obj)

async def del_greeting_temp(server,user_id):
    found_temps = False
    if(server.id in greeting_temp):
        if(user_id in greeting_temp[server.id]):
            for msg in greeting_temp[server.id][user_id]:
                await __main__.client.delete_message(msg)
                del greeting_temp[server.id][user_id]
                found_temps = True
    return found_temps


async def reject_gate_lurkers(server,member_id):
    if(server.id in gate_lurkers and member_id in gate_lurkers[server.id]):
        gate_reject_lurker_time = await __main__.get_config('gate_reject_lurker_time',server,'greet')
        if(gate_reject_lurker_time != False and gate_reject_lurker_time != None and int(gate_reject_lurker_time) > 0):
            if(gate_lurkers[server.id][member_id] == 0):
                member = await __main__.find_user(server,'<@'+str(member_id)+'>',True)
                if(member != False):
                    gate_approved_role = await __main__.get_config('gate_approved_role',server,'greet')
                    has_base = await __main__.has_role(member.id,gate_approved_role,server)
                    if(has_base == False):
                        use_server_id = await __main__.hash_server_id(server.id)
                        use_member_id = await __main__.hash_member_id(server.id,member.id)

                        chk_user = __main__.db.cursor()
                        chk_user.execute("UPDATE users SET authorised=?, prev_authorised=?, rejected=? WHERE user_id=? AND server_id=?",(0,0,1,use_member_id,use_server_id,))
                        __main__.db.commit()

                        save_note = 'Rejected this user from entering the server because no activity has been detected.'
                        await __main__.trigger_active_plugin(server,'user_log','users','general',server,member.id,__main__.client.user.id,save_note,None)

                        greeting_log_channel = await __main__.bot_use_channel(server,'greet','greeting_log_channel')
                        if(greeting_log_channel != False):
                            await __main__.client.send_message(greeting_log_channel,member.display_name+' ('+member.name+'#'+member.discriminator+' / '+str(member.id)+') was automatically rejected due to no activity.')

                        await __main__.client.kick(member)

        del gate_lurkers[server.id][member_id]


async def member_join(member):
    greeting_mode = await __main__.get_config('greeting_mode',member.server,'greet')
    greeting_log_channel = await __main__.bot_use_channel(member.server,'greet','greeting_log_channel')
    gate_approved_role = await __main__.get_config('gate_approved_role',member.server,'greet')
    gate_reject_account_age = await __main__.get_config('gate_reject_account_age',member.server,'greet')
    gate_reject_lurker_time = await __main__.get_config('gate_reject_lurker_time',member.server,'greet')
    passed_filters = True

    if(gate_approved_role != False):
        #check account age to see if they should be auto rejected
        if(gate_reject_account_age != False and gate_reject_account_age != None and int(gate_reject_account_age) > 0):
            time_now = await __main__.current_timestamp()
            account_time = int(member.created_at.timestamp())
            account_age = time_now - account_time
            if(account_age < int(gate_reject_account_age)):
                passed_filters = False
                use_server_id = await __main__.hash_server_id(member.server.id)
                use_member_id = await __main__.hash_member_id(member.server.id,member.id)

                chk_user = __main__.db.cursor()
                chk_user.execute("UPDATE users SET authorised=?, prev_authorised=?, rejected=? WHERE user_id=? AND server_id=?",(0,0,1,use_member_id,use_server_id,))
                __main__.db.commit()

                save_note = 'Rejected this user from entering the server because their account was not old enough.'
                await __main__.trigger_active_plugin(member.server,'user_log','users','general',member.server,member.id,__main__.client.user.id,save_note,None)

                greeting_log_channel = await __main__.bot_use_channel(member.server,'greet','greeting_log_channel')
                if(greeting_log_channel != False):
                    await __main__.client.send_message(greeting_log_channel,member.display_name+' ('+member.name+'#'+member.discriminator+' / '+str(member.id)+') joined the server but was automatically rejected because their account is not old enough.')

                await __main__.client.kick(member)



    if(passed_filters == True):

        if(greeting_mode == "alert" or greeting_mode == "greet"):
            #create new member alert
            if(greeting_log_channel != False):
                alert_str = ''
                greeting_alert_role = await __main__.get_config('greeting_alert_role',member.server,'greet')
                if(greeting_alert_role != False): alert_str = await __main__.create_alert(member.server,greeting_alert_role,'<@'+member.id+'> has joined the server and needs approving.') 
                info_msg = await __main__.trigger_active_plugin(member.server,'user_info','users',member.server,member,greeting_log_channel,alert_str)
                if(gate_approved_role != False):
                    await track_greeting_temp(member.server,member.id,info_msg)
                    if(gate_reject_lurker_time != False and gate_reject_lurker_time != None and int(gate_reject_lurker_time) > 0):
                        if(member.server.id not in gate_lurkers): gate_lurkers[member.server.id] = {}
                        gate_lurkers[member.server.id][member.id] = 0
                        trig_time = await __main__.current_timestamp()
                        trig_time = trig_time + int(gate_reject_lurker_time)
                        await __main__.add_task(member.server,trig_time,'greet','reject_gate_lurkers',member.id)

        if(greeting_mode == "greet"):
            #send greeting message
            greeting_channel = await __main__.get_config('greeting_channel',member.server,'greet')
            if(greeting_channel != False):
                greet_channel = await __main__.channel_name_from_id(member.server,greeting_channel,True)
                if(greet_channel != False):
                    greeting_message = await __main__.get_config('greeting_message',member.server,'greet')
                    if(greeting_message != False):
                        await __main__.asyncio.sleep(6)

                        use_greeting_msg = greeting_message.replace('[user]','<@'+member.id+'>')
                        sent_greeting = await __main__.client.send_message(greet_channel,use_greeting_msg)

                        #if(get_approved_role != False): await track_greeting_temp(member.server,member.id,sent_greeting)

                    else:
                        if(greeting_log_channel != False): await __main__.client.send_message(greeting_log_channel,'**ERROR:** The greeting message has not been set.')
                else:
                    if(greeting_log_channel != False): await __main__.client.send_message(greeting_log_channel,'**ERROR:** The set greeting channel does not exist.')
            else:
                if(greeting_log_channel != False): await __main__.client.send_message(greeting_log_channel,'**ERROR:** No greeting channel has been set.')



async def member_remove(member):

    if(member.server.id in gate_lurkers and member.id in gate_lurkers[member.server.id]): del gate_lurkers[member.server.id][member.id]

    temps_found = await del_greeting_temp(member.server,member.id)
    if(temps_found == True):
        greeting_log_channel = await __main__.bot_use_channel(member.server,'greet','greeting_log_channel')
        await __main__.client.send_message(greeting_log_channel,member.display_name+' ('+member.name+'#'+member.discriminator+') has left the server and no longer requires approval.')

    gate_approved_role = await __main__.get_config('gate_approved_role',member.server,'greet')
    if(get_approved_role != False):
        use_server_id = await __main__.hash_server_id(member.server.id)
        use_member_id = await __main__.hash_member_id(member.server.id,member.id)
        chk_user = __main__.db.cursor()
        chk_user.execute("UPDATE users SET authorised='0' WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
        __main__.db.commit()


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
