#!/usr/bin/python

import __main__

global pay_cooldown
pay_cool_log = {}

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Credits'
    help_info['description'] = 'Spend and earn credits on this server, which in the real world are worth less than nothing.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'credits'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'user_balance'
    help_entry['args'] = '@someuser'
    help_entry['description'] = 'See how many credits @someuser has.'
    help_entry['perm_name'] = 'award'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'award'
    help_entry['args'] = '@someuser amount'
    help_entry['description'] = 'Award @someuser amount of credits.'
    help_entry['perm_name'] = 'award'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'take'
    help_entry['args'] = '@someuser amount'
    help_entry['description'] = 'Remove amount of credits from @someuser.'
    help_entry['perm_name'] = 'award'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = ''
    help_entry['description'] = 'See how many credits you have.'
    help_entry['perm_name'] = 'use_own_credits'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'pay'
    help_entry['args'] = '@someuser amount'
    help_entry['description'] = 'Pay @someuser amount of credits'
    help_entry['perm_name'] = 'use_own_credits'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'charge'
    help_entry['args'] = '@someuser amount'
    help_entry['description'] = 'Charge @someuser amount of credits, they will be asked to confirm the payment.'
    help_entry['perm_name'] = 'use_own_credits'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'award'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')

    this_perm = 'use_own_credits'
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
    if(message.content.startswith(bot_cmd_char+'credits')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)
        if(proc_msg_length == 1): proc_msg[1] = 'balance'

        if(proc_msg[1] == "balance"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'credits','use_own_credits',True)
            if(chk_user_perm == True):
                use_server_id = await __main__.hash_server_id(message.server.id)
                use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)

                user_creds = __main__.db.cursor()
                user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                found_balance = 0
                for row in user_creds:
                    if(row['credits'] != None and row['credits'] != ""):
                        dec_balance = await __main__.decrypt_data(row['credits'])
                        if(dec_balance != False): found_balance = int(dec_balance)

                await __main__.client.send_message(message.author,'<@'+message.author.id+'>, your balance is '+str(found_balance)+' credits.')
                await __main__.client.delete_message(message)


        if(proc_msg[1] == "user_balance"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'credits','award',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 3):
                    pay_user = await __main__.find_user(message.server,proc_msg[2],True)
                    if(pay_user != False):
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        use_member_id = await __main__.hash_member_id(message.server.id,pay_user.id)

                        user_creds = __main__.db.cursor()
                        user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                        found_balance = 0
                        for row in user_creds:
                            if(row['credits'] != None and row['credits'] != ""):
                                dec_balance = await __main__.decrypt_data(row['credits'])
                                if(dec_balance != False): found_balance = int(dec_balance)

                        await __main__.client.send_message(message.channel,pay_user.display_name+'\'s balance is '+str(found_balance)+' credit(s).')

                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find someone called "'+proc_msg[2]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must whose balance you want to see.')


        if(proc_msg[1] == "award"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'credits','award',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 4):
                    pay_user = await __main__.find_user(message.server,proc_msg[2],True)
                    if(pay_user != False):
                        pay_amount = int(proc_msg[3])
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        use_member_id = await __main__.hash_member_id(message.server.id,pay_user.id)

                        user_creds = __main__.db.cursor()
                        user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                        found_balance = 0
                        for row in user_creds:
                            if(row['credits'] != None and row['credits'] != ""):
                                dec_balance = await __main__.decrypt_data(row['credits'])
                                if(dec_balance != False): found_balance = int(dec_balance)

                        new_balance = found_balance + pay_amount
                        save_balance = await __main__.encrypt_data(str(new_balance))
                        user_creds.execute("UPDATE users SET credits=? WHERE user_id=? AND server_id=?",(save_balance,use_member_id,use_server_id,))
                        __main__.db.commit()

                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, awarding '+pay_user.display_name+' '+str(pay_amount)+' credit(s).')
                        await __main__.client.send_message(pay_user,'You have been awarded '+str(pay_amount)+' credit(s) on '+message.server.name+'. Your new balance is '+str(new_balance)+' credits.')

                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find someone called "'+proc_msg[2]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify who to award and how many credits.')


        if(proc_msg[1] == "take"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'credits','award',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 4):
                    pay_user = await __main__.find_user(message.server,proc_msg[2],True)
                    if(pay_user != False):
                        pay_amount = int(proc_msg[3])
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        use_member_id = await __main__.hash_member_id(message.server.id,pay_user.id)

                        user_creds = __main__.db.cursor()
                        user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                        found_balance = 0
                        for row in user_creds:
                            if(row['credits'] != None and row['credits'] != ""):
                                dec_balance = await __main__.decrypt_data(row['credits'])
                                if(dec_balance != False): found_balance = int(dec_balance)

                        new_balance = found_balance - pay_amount
                        save_balance = await __main__.encrypt_data(str(new_balance))
                        user_creds.execute("UPDATE users SET credits=? WHERE user_id=? AND server_id=?",(save_balance,use_member_id,use_server_id,))
                        __main__.db.commit()

                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, taking '+str(pay_amount)+' credit(s) off  '+pay_user.display_name+'.')
                        await __main__.client.send_message(pay_user,'You have had '+str(pay_amount)+' credit(s) taken from you on '+message.server.name+'. Your new balance is '+str(new_balance)+' credits.')

                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find someone called "'+proc_msg[2]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify who to take credits from and how many.')


        if(proc_msg[1] == "pay"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'credits','use_own_credits',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 4):
                    pay_user = await __main__.find_user(message.server,proc_msg[2],True)
                    if(pay_user != False):
                        pay_amount = int(proc_msg[3])
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)

                        user_creds = __main__.db.cursor()
                        user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                        found_balance = 0
                        for row in user_creds:
                            if(row['credits'] != None and row['credits'] != ""):
                                dec_balance = await __main__.decrypt_data(row['credits'])
                                if(dec_balance != False): found_balance = int(dec_balance)

                        if(found_balance >= pay_amount):

                            new_balance = found_balance - pay_amount
                            save_balance = await __main__.encrypt_data(str(new_balance))
                            user_creds.execute("UPDATE users SET credits=? WHERE user_id=? AND server_id=?",(save_balance,use_member_id,use_server_id,))
                            __main__.db.commit()

                            use_member_id = await __main__.hash_member_id(message.server.id,pay_user.id)

                            user_creds = __main__.db.cursor()
                            user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                            found_balance = 0
                            for row in user_creds:
                                if(row['credits'] != None and row['credits'] != ""):
                                    dec_balance = await __main__.decrypt_data(row['credits'])
                                    if(dec_balance != False): found_balance = int(dec_balance)

                            new_balance = found_balance + pay_amount
                            save_balance = await __main__.encrypt_data(str(new_balance))
                            user_creds.execute("UPDATE users SET credits=? WHERE user_id=? AND server_id=?",(save_balance,use_member_id,use_server_id,))
                            __main__.db.commit()

                            await __main__.client.send_message(message.channel,'Cha-ching! <@'+message.author.id+'> paid '+str(pay_amount)+' credit(s) to <@'+pay_user.id+'>.')
                            await __main__.client.delete_message(message)

                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you don\'t have enough credits to pay that amount.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find someone called "'+proc_msg[2]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify who to pay and how much.')


        if(proc_msg[1] == "charge"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'credits','use_own_credits',True)
            if(chk_user_perm == True):
                if(proc_msg_length == 4):
                    pay_user = await __main__.find_user(message.server,proc_msg[2],True)
                    if(pay_user != False):
                        pay_amount = int(proc_msg[3])
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        use_member_id = await __main__.hash_member_id(message.server.id,pay_user.id)

                        user_creds = __main__.db.cursor()
                        user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                        found_balance = 0
                        for row in user_creds:
                            if(row['credits'] != None and row['credits'] != ""):
                                dec_balance = await __main__.decrypt_data(row['credits'])
                                if(dec_balance != False): found_balance = int(dec_balance)

                        if(found_balance >= pay_amount):

                            conf_msg = await __main__.client.send_message(message.channel,'<@'+pay_user.id+'>, <@'+message.author.id+'> has requested payment of '+str(pay_amount)+' credit(s). Do you confirm? Please say "yes" or "no" within the next 60 seconds.')
                            get_conf = await __main__.client.wait_for_message(timeout=60.0,author=pay_user,channel=message.channel)
                            if(get_conf != None and get_conf.content.lower() == "yes"):
                                await __main__.client.delete_message(conf_msg)
                                await __main__.client.delete_message(get_conf)

                                new_balance = found_balance - pay_amount
                                save_balance = await __main__.encrypt_data(str(new_balance))
                                user_creds.execute("UPDATE users SET credits=? WHERE user_id=? AND server_id=?",(save_balance,use_member_id,use_server_id,))
                                __main__.db.commit()

                                use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)

                                user_creds = __main__.db.cursor()
                                user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
                                found_balance = 0
                                for row in user_creds:
                                    if(row['credits'] != None and row['credits'] != ""):
                                        dec_balance = await __main__.decrypt_data(row['credits'])
                                        if(dec_balance != False): found_balance = int(dec_balance)

                                new_balance = found_balance + pay_amount
                                save_balance = await __main__.encrypt_data(str(new_balance))
                                user_creds.execute("UPDATE users SET credits=? WHERE user_id=? AND server_id=?",(save_balance,use_member_id,use_server_id,))
                                __main__.db.commit()

                                await __main__.client.send_message(message.channel,'Cha-ching! <@'+pay_user.id+'> paid '+str(pay_amount)+' credit(s) to <@'+message.author.id+'>.')
                                await __main__.client.delete_message(message)

                            else:
                                await __main__.client.delete_message(message)
                                await __main__.client.delete_message(conf_msg)
                                await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, <@'+pay_user.id+'> declined your payment request.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, <@'+pay_user.id+'> doesn\'t have enough credits to pay that amount.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find someone called "'+proc_msg[2]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify who to charge and how much.')




async def message_new(message):
    if(message.channel.is_private == False and message.author.id != __main__.client.user.id and message.author.bot == False):
        pay_amount = 1
        pay_cooldown = 20

        time_now = await __main__.current_timestamp()
        if(message.server.id not in pay_cool_log): pay_cool_log[message.server.id] = {}
        if(message.author.id in pay_cool_log[message.server.id]):
            time_diff = time_now - pay_cool_log[message.server.id][message.author.id]
        else: time_diff = pay_cooldown

        if(time_diff >= pay_cooldown):
            use_server_id = await __main__.hash_server_id(message.server.id)
            use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)

            user_creds = __main__.db.cursor()
            user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
            found_balance = 0
            for row in user_creds:
                if(row['credits'] != None and row['credits'] != ""):
                    dec_balance = await __main__.decrypt_data(row['credits'])
                    if(dec_balance != False): found_balance = int(dec_balance)

            new_balance = found_balance + pay_amount
            save_balance = await __main__.encrypt_data(str(new_balance))
            user_creds.execute("UPDATE users SET credits=? WHERE user_id=? AND server_id=?",(save_balance,use_member_id,use_server_id,))
            __main__.db.commit()

            pay_cool_log[message.server.id][message.author.id] = time_now

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
