#!/usr/bin/python

import __main__

#===================================================================================================================
#CUSTOM FUNCTIONS

global alert_users
alert_users = {}

async def switch_on_alertme(user,server,save_state=True):
    hashed_server_id = await __main__.hash_server_id(server.id)
    hashed_user_id = await __main__.hash_member_id(server.id,user.id)
    if(server.id not in alert_users): alert_users[server.id] = []

    found_user = None
    fu_run = 0
    while(fu_run < len(alert_users[server.id])):
        if(alert_users[server.id][fu_run]['user_id'] == user.id):
            found_user = fu_run
            break
        fu_run = fu_run + 1

    if(found_user == None):
        new_alert_user = {}
        new_alert_user['user_id'] = user.id
        new_alert_user['alerts'] = {}
        new_alert_user['channels'] = {}
        new_alert_user['cooldown'] = 60

        cooldown_cursor = __main__.db.cursor()
        cooldown_cursor.execute("SELECT alertme_cooldown FROM users WHERE user_id=?",(hashed_user_id,))
        for row in cooldown_cursor:
            if(row['alertme_cooldown'] != None and row['alertme_cooldown'] != ""): new_alert_user['cooldown'] = int(row['alertme_cooldown'])

        new_alert_user['words'] = []
        word_cursor = __main__.db.cursor()
        word_cursor.execute("SELECT word FROM alertme_words WHERE user=? AND server=?",(hashed_user_id,hashed_server_id,))
        for row in word_cursor:
            decrypt_word = await __main__.decrypt_data(row['word'])
            if(decrypt_word != None and decrypt_word != False): new_alert_user['words'].append(decrypt_word)

        new_alert_user['blacklist'] = {}
        new_alert_user['blacklist']['user'] = []
        new_alert_user['blacklist']['channel'] = []
        bl_cursor = __main__.db.cursor()
        bl_cursor.execute("SELECT type,value FROM alertme_blacklist WHERE user=? AND server=?",(hashed_user_id,hashed_server_id,))
        for row in bl_cursor:
            decrypt_word = await __main__.decrypt_data(row['value'])
            if(decrypt_word != None and decrypt_word != False): new_alert_user['blacklist'][row['type']].append(decrypt_word)

        alert_users[server.id].append(new_alert_user)
        if(save_state == True):
            cursor = __main__.db.cursor()
            cursor.execute("UPDATE users SET alertme='1' WHERE user_id=?",(hashed_user_id,))
            __main__.db.commit()

        return True
    else: return False
    

async def switch_off_alertme(user,server,save_state=True):
    hashed_server_id = await __main__.hash_server_id(server.id)
    if(server.id not in alert_users): alert_users[server.id] = []

    found_user = None
    fu_run = 0
    while(fu_run < len(alert_users[server.id])):
        if(alert_users[server.id][fu_run]['user_id'] == user.id):
            found_user = fu_run
            break
        fu_run = fu_run + 1

    if(found_user != None):
        del alert_users[server.id][found_user]

        if(save_state == True):
            hashed_user_id = await __main__.hash_member_id(server.id,user.id)
            cursor = __main__.db.cursor()
            cursor.execute("UPDATE users SET alertme='0' WHERE user_id=?",(hashed_user_id,))
            __main__.db.commit()

        return True
    else: return False


async def set_alertme_cooldown(user,server,cooldown_seconds):
    hashed_server_id = await __main__.hash_server_id(server.id)
    hashed_user_id = await __main__.hash_member_id(server.id,user.id)
    if(server.id not in alert_users): alert_users[server.id] = []

    cursor = __main__.db.cursor()
    cursor.execute("UPDATE users SET alertme_cooldown=? WHERE user_id=?",(cooldown_seconds,hashed_user_id,))
    __main__.db.commit()

    fu_run = 0
    while(fu_run < len(alert_users[server.id])):
        if(alert_users[server.id][fu_run]['user_id'] == user.id):
            alert_users[server.id][fu_run]['cooldown'] = cooldown_seconds
            break
        fu_run = fu_run + 1


async def compare_alert_word_to_message(alert_word,message_text):
    found_word = False
    
    #The pseudo_words bodge attempts to apply some basic tenses to whatever alert words have been specified by this user, to catch things like "someuser's" where there is no apostrophe
    pseudo_words = []
    pseudo_words.append(alert_word)
    pseudo_words.append(alert_word+'s')
    pseudo_words.append(alert_word+'es')
    pseudo_words.append(alert_word+'d')
    pseudo_words.append(alert_word+'ed')

    #If the adjacent characters to the detected alert word are any of the blocked characters then this would be a false positive, as it isn't its own word or phrase
    block_chars = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0']

    found_words = []
    for check_word in pseudo_words:

        split_msg = message_text.split(check_word)
        check_word_found = False
        if(len(split_msg) > 1):
            
            msg_run = 0
            while(msg_run < len(split_msg)):
                if(msg_run < (len(split_msg) - 1)):
                    block_char = False

                    #Check to see if this chunk ends with a block character
                    if(block_char == False):
                        for bc in block_chars:
                            if(split_msg[msg_run].endswith(bc) == True):
                                block_char = True
                                break

                    #Check to see if the next chunk starts with a block character
                    if(block_char == False):
                        next_run = msg_run + 1
                        for bc in block_chars:
                            if(split_msg[next_run].startswith(bc) == True):
                                block_char = True
                                break

                    #Check to see if this string is an emoji trigger
                    if(block_char == False):
                        next_run = msg_run + 1
                        if(split_msg[msg_run].endswith(':') == True and split_msg[next_run].startswith(':') == True):
                            block_char = True
                            break

                    if(block_char == False):
                        check_word_found = True
                        break

                msg_run = msg_run + 1

        if(check_word_found == True):
            found_words.append(check_word)
            break

    if(len(found_words) > 0): found_word = True
    return found_word


async def check_for_alertme(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)
    if(message.author.id != __main__.client.user.id and message.channel.is_private == False and message.content.startswith(bot_cmd_char+'alertme') == False):
        time_now = await __main__.current_timestamp() 
        
        #Check if this message contains an alert word
        if(message.server.id in alert_users):

            #Check to see if the message author has active alert words, if so record when they were last seen in this channel
            au_index = 0
            while(au_index < len(alert_users[message.server.id])):
                if(alert_users[message.server.id][au_index]['user_id'] == message.author.id):
                    alert_users[message.server.id][au_index]['channels'][message.channel.id] = time_now
                    break
                au_index = au_index + 1

            #Look for alert words in this message
            found_alert_users = {}
            for alert_user in alert_users[message.server.id]:

                blacklist_okay = True
                if(message.channel.id in alert_user['blacklist']['channel']): blacklist_okay = False
                if(message.author.id in alert_user['blacklist']['user']): blacklist_okay = False

                if(blacklist_okay == True):
                    for alert_word in alert_user['words']:
                        word_match = await compare_alert_word_to_message(alert_word.lower(),message.content.lower())
                        if(word_match == True):
                            if(alert_user['user_id'] not in found_alert_users): found_alert_users[alert_user['user_id']] = []
                            found_alert_users[alert_user['user_id']].append(alert_word)

            for user_id,triggered_words in found_alert_users.items():
                
                #Check that user has read permission for the channel this was detected in
                alert_user_object = await __main__.find_user(message.server,'<@'+user_id+'>',True)
                if(alert_user_object != False):
                    user_permissions = message.channel.permissions_for(alert_user_object)
                    if(user_permissions.read_messages == True):

                        #Check that the user isn't currently active in this channel
                        send_alert = True
                        au_index = 0
                        for alert_user in alert_users[message.server.id]:
                            if(alert_user['user_id'] == user_id):
                                if('channels' in alert_user):
                                    if(message.channel.id in alert_user['channels']):
                                        if((time_now - alert_user['channels'][message.channel.id]) < alert_user['cooldown']): send_alert = False
                                break
                            au_index = au_index + 1

                        if(send_alert == True):
                            #Send alert to users DMs

                            icon_url = message.author.avatar_url
                            if(icon_url == None or icon_url == ""): icon_url = message.author.default_avatar_url

                            repost_title = 'Alert in #'+message.channel.name+' ('+message.server.name+'):'

                            repost_description = ''
                            for this_word in triggered_words:
                                if(repost_description != ""): repost_description = repost_description+', '
                                repost_description = repost_description+'"'+this_word+'"'
                            repost_description = 'Detected: '+repost_description

                            em = __main__.discord.Embed(title=repost_title, description=repost_description, colour=3447003)
                            em.set_author(name=message.author.display_name, icon_url=icon_url)
                            em.set_thumbnail(url=icon_url)

                            em.add_field(name="Posted:",value=message.content,inline=False)

                            msg_time = str(message.timestamp).split(".")
                            msg_time = msg_time[0]
                            em.set_footer(text=msg_time)
                            await __main__.client.send_message(alert_user_object, embed=em)



#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'AlertMe'
    help_info['description'] = 'DMs you with an alert when certain things happen.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'alertme'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'on'
    help_entry['args'] = ''
    help_entry['description'] = 'Turn on your alerts'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'off'
    help_entry['args'] = ''
    help_entry['description'] = 'Turn off your alerts'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'active_cooldown'
    help_entry['args'] = 'time_int time_scale'
    help_entry['description'] = 'Set how long the cooldown for alerts should be when you\'re active in a channel. Time_int must be a number and time_scale can be seconds or minutes.'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'wordlist'
    help_entry['args'] = ''
    help_entry['description'] = 'List which words or phrases are on your alert list'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add_word'
    help_entry['args'] = 'word_or_phrase'
    help_entry['description'] = 'Adds word_or_phrase to your alert list'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'remove_word'
    help_entry['args'] = 'word_or_phrase'
    help_entry['description'] = 'Removes word_or_phrase from your alert list'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'alertme_blacklist'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'channels'
    help_entry['args'] = ''
    help_entry['description'] = 'Lists the channels on your alert blacklist'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Adds channel_name to your alert blacklist'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'remove_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Removes channel_name from your alert blacklist'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'users'
    help_entry['args'] = ''
    help_entry['description'] = 'Lists the users on your alert blacklist'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add_user'
    help_entry['args'] = 'user_name'
    help_entry['description'] = 'Adds user_name to your alert blacklist'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'remove_user'
    help_entry['args'] = 'user_name'
    help_entry['description'] = 'Removes user_name from your alert blacklist'
    help_entry['perm_name'] = 'use_alerts'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'use_alerts'
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
    hashed_server_id = await __main__.hash_server_id(server.id)
    user_cursor = __main__.db.cursor()
    user_cursor.execute("SELECT stored_user_id FROM users WHERE server_id=? AND alertme='1'",(hashed_server_id,))
    for row in user_cursor:
        stored_user_id = await __main__.decrypt_data(row['stored_user_id'])
        find_user_obj = await __main__.find_user(server,'<@'+stored_user_id+'>',True)
        if(find_user_obj != None and find_user_obj != False):
            await switch_on_alertme(find_user_obj,server,False)


#===================================================================================================================
#MESSAGE EVENTS

async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)

    if(message.content.startswith(bot_cmd_char+'alertme')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'alertme','use_alerts',True)
        if(chk_user_perm == True):
            
            proc_msg = await __main__.get_cmd_args(message.content,2)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length > 1):

                if(proc_msg[1] == "on"):
                    alertme_toggle = await switch_on_alertme(message.author,message.server)
                    if(alertme_toggle == True):
                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, your alerts have been turned on.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, your alerts are already turned on.')

                if(proc_msg[1] == "off"):
                    alertme_toggle = await switch_off_alertme(message.author,message.server)
                    if(alertme_toggle == True):
                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, your alerts have been turned off.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, your alerts are already turned off.')


                if(proc_msg[1] == "wordlist"):
                    hashed_server_id = await __main__.hash_server_id(message.server.id)
                    hashed_user_id = await __main__.hash_member_id(message.server.id,message.author.id)

                    icon_url = message.author.avatar_url
                    if(icon_url == None or icon_url == ""): icon_url = message.author.default_avatar_url
                    
                    cursor = __main__.db.cursor()
                    cursor.execute("SELECT * FROM alertme_words WHERE user=? AND server=?",(hashed_user_id,hashed_server_id,))
                    build_words = ''
                    for row in cursor:
                       decrypt_word = await __main__.decrypt_data(row['word']) 
                       build_words = build_words+'** - ** "'+decrypt_word+'"\n'

                    if(build_words != ""):
                        embed_description = 'Here are the words and phrases on your alert list:'
                    else: embed_description = 'You do not have any words or phrases on your alert list.'

                    em = __main__.discord.Embed(title='Alert words', description=embed_description, colour=3447003)
                    em.set_author(name=message.author.display_name, icon_url=icon_url)
                    em.set_thumbnail(url=icon_url)

                    if(build_words != ""): em.add_field(name="Words and phrases",value=build_words,inline=False)
                    await __main__.client.send_message(message.author, embed=em)


                if(proc_msg[1] == "add_word"):
                    if(proc_msg_length == 3):
                        hashed_server_id = await __main__.hash_server_id(message.server.id)
                        hashed_user_id = await __main__.hash_member_id(message.server.id,message.author.id)

                        word_cursor = __main__.db.cursor()
                        word_cursor.execute("SELECT id,word FROM alertme_words WHERE user=? AND server=?",(hashed_user_id,hashed_server_id,))
                        found_id = None
                        for row in word_cursor:
                            decrypt_word = await __main__.decrypt_data(row['word']) 
                            if(decrypt_word == proc_msg[2]): found_id = row['id']

                        if(found_id == None):
                            encrypt_word = await __main__.encrypt_data(proc_msg[2]) 
                            word_cursor.execute("INSERT INTO alertme_words (user,server,word) VALUES (?,?,?)",(hashed_user_id,hashed_server_id,encrypt_word,))
                            __main__.db.commit()

                            if(message.server.id not in alert_users): alert_users[message.server.id] = []
                            fu_run = 0
                            while(fu_run < len(alert_users[message.server.id])):
                                if(alert_users[message.server.id][fu_run]['user_id'] == message.author.id):
                                    if('words' not in alert_users[message.server.id][fu_run]): alert_users[message.server.id][fu_run]['words'] = []
                                    alert_users[message.server.id][fu_run]['words'].append(proc_msg[2])
                                    break
                                fu_run = fu_run + 1

                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have added "'+str(proc_msg[2])+'" to your alert list.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that is already in your alert word list.')

                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a word or phrase to add to your alert list.')



                if(proc_msg[1] == "remove_word"):
                    if(proc_msg_length == 3):
                        hashed_server_id = await __main__.hash_server_id(message.server.id)
                        hashed_user_id = await __main__.hash_member_id(message.server.id,message.author.id)

                        word_cursor = __main__.db.cursor()
                        word_cursor.execute("SELECT id,word FROM alertme_words WHERE user=? AND server=?",(hashed_user_id,hashed_server_id,))
                        found_id = None
                        for row in word_cursor:
                            decrypt_word = await __main__.decrypt_data(row['word']) 
                            if(decrypt_word == proc_msg[2]): found_id = row['id']

                        if(found_id != None):
                            word_cursor.execute("DELETE FROM alertme_words WHERE user=? AND server=? AND id=?",(hashed_user_id,hashed_server_id,found_id,))
                            __main__.db.commit()

                            if(message.server.id not in alert_users): alert_users[message.server.id] = []
                            fu_run = 0
                            while(fu_run < len(alert_users[message.server.id])):
                                if(alert_users[message.server.id][fu_run]['user_id'] == message.author.id):
                                    if('words' in alert_users[message.server.id][fu_run] and proc_msg[2] in alert_users[message.server.id][fu_run]['words']): alert_users[message.server.id][fu_run]['words'].remove(proc_msg[2])
                                    break
                                fu_run = fu_run + 1

                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have removed "'+str(proc_msg[2])+'" from your alert list.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find "'+str(proc_msg[2])+'" in your alert word list.')

                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a word or phrase to remove from your alert list.')


                if(proc_msg[1] == "active_cooldown"):
                    proc_msg = await __main__.get_cmd_args(message.content)
                    proc_msg_length = len(proc_msg)
                    if(proc_msg_length >= 3):
                        hashed_server_id = await __main__.hash_server_id(message.server.id)
                        hashed_user_id = await __main__.hash_member_id(message.server.id,message.author.id)

                        if(proc_msg_length == 4):
                            time_int = int(proc_msg[2])
                            time_scale = proc_msg[3]
                        else:
                            time_int = 0
                            time_scale = 'mins'

                        if(time_int == 0):
                            display_time = 'off'
                        else: display_time = str(time_int)+' '+time_scale

                        time_seconds = await __main__.cmd_time_args(time_int,time_scale)
                        await set_alertme_cooldown(message.author,message.server,time_seconds)

                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set your active cooldown time for alerts to "'+display_time+'".')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either "off" or a number and a time scale.')



    if(message.content.startswith(bot_cmd_char+'alertme_blacklist')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'alertme','use_alerts',True)
        if(chk_user_perm == True):

            proc_msg = await __main__.get_cmd_args(message.content,2)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length > 1):

                if(proc_msg[1] == "channels" or proc_msg[1] == "users"):
                    hashed_server_id = await __main__.hash_server_id(message.server.id)
                    hashed_user_id = await __main__.hash_member_id(message.server.id,message.author.id)
                    
                    use_type = proc_msg[1]+'#'
                    use_type = use_type.replace('s#','')

                    icon_url = message.author.avatar_url
                    if(icon_url == None or icon_url == ""): icon_url = message.author.default_avatar_url
                    
                    cursor = __main__.db.cursor()
                    cursor.execute("SELECT * FROM alertme_blacklist WHERE user=? AND server=? AND type=?",(hashed_user_id,hashed_server_id,use_type,))
                    build_words = ''
                    for row in cursor:
                        decrypt_word = await __main__.decrypt_data(row['value'])
                        if(use_type == 'channel'): decrypt_word = await __main__.channel_name_from_id(message.server,decrypt_word)
                        if(use_type == 'user'):
                            user_obj = await __main__.find_user(message.server,'<@'+decrypt_word+'>',True)
                            if(user_obj != False):
                                decrypt_word = user_obj.display_name+' ('+user_obj.name+'#'+user_obj.discriminator+')'
                            else: decrypt_word = False

                        if(decrypt_word != None and decrypt_word != False): build_words = build_words+'** - ** "'+decrypt_word+'"\n'

                    if(build_words != ""):
                        embed_description = 'Here are the '+use_type+'s on your alert blacklist:'
                    else: embed_description = 'You do not have any '+use_type+'s on your alert blacklist.'

                    em = __main__.discord.Embed(title='Alertme '+use_type+' blacklist', description=embed_description, colour=3447003)
                    em.set_author(name=message.author.display_name, icon_url=icon_url)
                    em.set_thumbnail(url=icon_url)

                    if(build_words != ""): em.add_field(name=use_type.capitalize()+'s',value=build_words,inline=False)
                    await __main__.client.send_message(message.author, embed=em)


                if(proc_msg[1] == "add_channel" or proc_msg[1] == "add_user"):
                    if(proc_msg_length == 3):
                        hashed_server_id = await __main__.hash_server_id(message.server.id)
                        hashed_user_id = await __main__.hash_member_id(message.server.id,message.author.id)

                        use_type = proc_msg[1].replace("add_","")

                        use_value = proc_msg[2]
                        if(use_type == 'channel'): use_value = await __main__.channel_id_from_name(message.server,use_value)
                        if(use_type == 'user'): use_value = await __main__.find_user(message.server,use_value)
                        if(use_value != None and use_value != False):

                            word_cursor = __main__.db.cursor()
                            word_cursor.execute("SELECT id,value FROM alertme_blacklist WHERE user=? AND server=? AND type=?",(hashed_user_id,hashed_server_id,use_type,))
                            found_id = None
                            for row in word_cursor:
                                decrypt_word = await __main__.decrypt_data(row['value']) 
                                if(decrypt_word == use_value): found_id = row['id']

                            if(found_id == None):
                                encrypt_word = await __main__.encrypt_data(use_value) 
                                word_cursor.execute("INSERT INTO alertme_blacklist (user,server,type,value) VALUES (?,?,?,?)",(hashed_user_id,hashed_server_id,use_type,encrypt_word,))
                                __main__.db.commit()

                                if(message.server.id not in alert_users): alert_users[message.server.id] = []
                                fu_run = 0
                                while(fu_run < len(alert_users[message.server.id])):
                                    if(alert_users[message.server.id][fu_run]['user_id'] == message.author.id):
                                        if('blacklist' not in alert_users[message.server.id][fu_run]): alert_users[message.server.id][fu_run]['blacklist'] = {}
                                        if(use_type not in alert_users[message.server.id][fu_run]['blacklist']): alert_users[message.server.id][fu_run]['blacklist'][use_type] = []
                                        alert_users[message.server.id][fu_run]['blacklist'][use_type].append(use_value)
                                        break
                                    fu_run = fu_run + 1

                                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have added the '+use_type+' "'+str(proc_msg[2])+'" to your alert blacklist.')

                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that '+use_type+' is already on your alert blacklist.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a '+use_type+' called "'+proc_msg[2]+'", please try again.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a '+use_type+' to add to your alert blacklist.')


                if(proc_msg[1] == "remove_channel" or proc_msg[1] == "remove_user"):
                    if(proc_msg_length == 3):
                        hashed_server_id = await __main__.hash_server_id(message.server.id)
                        hashed_user_id = await __main__.hash_member_id(message.server.id,message.author.id)

                        use_type = proc_msg[1].replace("remove_","")

                        use_value = proc_msg[2]
                        if(use_type == 'channel'): use_value = await __main__.channel_id_from_name(message.server,use_value)
                        if(use_type == 'user'): use_value = await __main__.find_user(message.server,use_value)
                        if(use_value != None and use_value != False):

                            word_cursor = __main__.db.cursor()
                            word_cursor.execute("SELECT id,value FROM alertme_blacklist WHERE user=? AND server=? AND type=?",(hashed_user_id,hashed_server_id,use_type,))
                            found_id = None
                            for row in word_cursor:
                                decrypt_word = await __main__.decrypt_data(row['value']) 
                                if(decrypt_word == use_value): found_id = row['id']

                            if(found_id != None):
                                word_cursor.execute("DELETE FROM alertme_blacklist WHERE user=? AND server=? AND type=? AND id=?",(hashed_user_id,hashed_server_id,use_type,found_id,))
                                __main__.db.commit()

                                if(message.server.id not in alert_users): alert_users[message.server.id] = []
                                fu_run = 0
                                while(fu_run < len(alert_users[message.server.id])):
                                    if(alert_users[message.server.id][fu_run]['user_id'] == message.author.id):
                                        alert_users[message.server.id][fu_run]['blacklist'][use_type].remove(use_value)
                                        break
                                    fu_run = fu_run + 1

                                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have removed the '+use_type+' "'+str(proc_msg[2])+'" from your alert blacklist.')

                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that '+use_type+' is already not on your alert blacklist.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a '+use_type+' called "'+proc_msg[2]+'", please try again.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a '+use_type+' to remove from your alert blacklist.')

                    





async def message_new(message):
    await check_for_alertme(message)

async def message_edit(before,after):
    await check_for_alertme(after)

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
