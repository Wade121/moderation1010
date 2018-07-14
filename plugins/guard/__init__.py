#!/usr/bin/python

import __main__

msg_count = {}

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Server guard'
    help_info['description'] = 'Anti spam system settings.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'set'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'spam_alert_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Sets the channel where spam notifications will be posted.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'spam_alert_role'
    help_entry['args'] = 'role_name'
    help_entry['description'] = 'Sets the role_name which will be alerted about spam notifications.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'guard'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'PLACE settings'
    help_entry['args'] = ''
    help_entry['description'] = 'View current guard settings for PLACE, where PLACE can either be "server" or a channel name.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'PLACE clear_settings'
    help_entry['args'] = ''
    help_entry['description'] = 'Resets a channels guard settings back to server defaults.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'PLACE trigger_limit'
    help_entry['args'] = 'msg_limit_per_min'
    help_entry['description'] = 'Set how many messages per minute before anti-spam is triggered.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    '''
    help_entry = {}
    help_entry['command'] = 'PLACE spam_action'
    help_entry['args'] = 'action_to_take'
    help_entry['description'] = 'Set how the bot handles being triggered by spam, can either be "notify" or "timeout"'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)
    '''

    help_entry = {}
    help_entry['command'] = 'PLACE spam_warning'
    help_entry['args'] = 'warning_status'
    help_entry['description'] = 'Sets whether the bot will warn a user before taking the appropriate spam action when triggered. Can either be "on" or "off".'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'PLACE block_urls'
    help_entry['args'] = 'status'
    help_entry['description'] = 'Sets whether the bot will delete posts containing URLs or not. Can either be "on" or "off".'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'PLACE block_text'
    help_entry['args'] = 'status'
    help_entry['description'] = 'Sets whether the bot will delete posts containing text or not. Can either be "on" or "off".'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'PLACE block_files'
    help_entry['args'] = 'status'
    help_entry['description'] = 'Sets whether the bot will delete posts containing uploaded files or not. Can either be "on" or "off".'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'guard_continued'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'PLACE time_limit_between_posts'
    help_entry['args'] = 'limit_time_int limit_time_scale'
    help_entry['description'] = 'Sets how much time must elapse before a member can make another post. Can either be "off" or a number and time scale.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'PLACE one_post_per_person'
    help_entry['args'] = 'status'
    help_entry['description'] = 'Sets whether the bot will delete all prior posts by each member or not. Can either be "on" or "off".'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'PLACE ignore list'
    help_entry['args'] = ''
    help_entry['description'] = 'List all the users on the white list for PLACE'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'PLACE ignore add'
    help_entry['args'] = 'member_name'
    help_entry['description'] = 'Adds member_name to the whitelist for PLACE.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'PLACE ignore REMOVE'
    help_entry['args'] = 'member_name'
    help_entry['description'] = 'Removes member_name from the whitelist for PLACE.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

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

async def server_remove(server):
    await spam_check_remove_server(server)

async def server_update(before,after): pass

async def server_connected(server): pass

#===================================================================================================================
#MESSAGE EVENTS

async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)

    if(message.content.startswith(bot_cmd_char+'set')):
        proc_msg = await __main__.get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)

        if(proc_msg[1] == "spam_alert_channel"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'guard','change_settings',True)
            if(chk_user_perm == True):
                find_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    await __main__.bot_set_channel(message.server,'guard','spam_alert_channel',find_channel.id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will now use that channel for posting spam alerts.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')

        if(proc_msg[1] == "spam_alert_role"):
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'guard','change_settings',True)
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
                    await __main__.set_config('spam_alert_role',message.server,'guard',use_role_id)
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the spam alert role to "'+proc_msg[2]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that is incorrect. You must specify either "off" or a valid role name.')


    if(message.content.startswith(bot_cmd_char+'guard')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'guard','change_settings',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 3):

                use_area = False
                if(proc_msg[1] == "server"):
                    use_area = {}
                    use_area['name'] = 'server'
                    use_area['id'] = 'server'
                else:
                    use_chan = await __main__.find_channel_arg(message.server,proc_msg[1],True)
                    if(use_chan != False):
                        use_area = {}
                        use_area['name'] = use_chan.name
                        use_area['id'] = use_chan.id

                if(use_area != False):

                    if(proc_msg[2] == "ignore"):

                        if(proc_msg[1] == "server"):
                            get_whitelist = await __main__.get_config('spam_whitelist',message.server,'guard')
                            if(get_whitelist == False): get_whitelist = []
                        else:
                            curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                            if(curr_chan_settings == False): curr_chan_settings = {}
                            if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                            if('spam_whitelist' not in curr_chan_settings[use_area['id']]):
                                get_whitelist = []
                            else: get_whitelist = curr_chan_settings[use_area['id']]['spam_whitelist']
                        whitelist_length = len(get_whitelist)



                        if(proc_msg[3] == "list"):
                            icon_url = __main__.client.user.avatar_url
                            if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url
                            if(proc_msg[1] == "server"):
                                list_title = 'Guard white list for the server'
                            else: list_title = 'Guard white list for '+use_area['name']+' channel'

                            if(whitelist_length > 0):

                                wl_run = 0
                                whitelist_length = whitelist_length - 1
                                list_descript = ''
                                while(wl_run <= whitelist_length):
                                    found_user = await __main__.find_user(message.server,get_whitelist[wl_run],True)
                                    if(found_user != False):
                                        list_descript = list_descript+'**-** '+found_user.display_name+'#'+found_user.discriminator+'\n'
                                    else: list_descript = list_descript+'**-** '+str(get_whitelist[wl_run])
                                    wl_run = wl_run + 1

                            else: list_descript = 'There are no users on the whitelist.'

                            em = __main__.discord.Embed(title=list_title, description=list_descript, colour=3447003)
                            em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                            #em.set_thumbnail(url=icon_url)
                            #em.set_image(url)

                            await __main__.client.send_message(message.channel, embed=em)


                        if(proc_msg[3] == "add"):
                            found_user = await __main__.find_user(message.server,proc_msg[4],True)
                            if(found_user != False):
                                if(found_user.id not in get_whitelist):
                                    get_whitelist.append(found_user.id)

                                    if(proc_msg[1] == "server"):
                                        await __main__.set_config('spam_whitelist',message.server,'guard',get_whitelist)
                                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have added <@'+found_user.id+'> to the server white list.')
                                    else:
                                        curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                        if(curr_chan_settings == False): curr_chan_settings = {}
                                        if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                        chk_set = await __main__.get_config('channel_spam',message.server,'guard')

                                        curr_chan_settings[use_area['id']]['spam_whitelist'] = get_whitelist
                                        await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)
                                        chk_set = await __main__.get_config('channel_spam',message.server,'guard')
                                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have added <@'+found_user.id+'> to the <#'+use_area['id']+'> white list.')
                                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that user is already on this white list.')
                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find that user.')


                        if(proc_msg[3] == "remove"):
                            found_user = await __main__.find_user(message.server,proc_msg[4],True)
                            if(found_user != False):
                                if(found_user.id in get_whitelist and whitelist_length > 0):

                                    if(whitelist_length > 0):
                                        wl_run = 0
                                        found_record = False
                                        whitelist_length = whitelist_length - 1
                                        while(wl_run <= whitelist_length):
                                            if(found_user.id == get_whitelist[wl_run]):
                                                del get_whitelist[wl_run]
                                                found_record = True
                                            wl_run = wl_run + 1

                                    if(found_record == True):

                                        if(proc_msg[1] == "server"):
                                            await __main__.set_config('spam_whitelist',message.server,'guard',get_whitelist)
                                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have removed <@'+found_user.id+'> from the server white list.')
                                        else:
                                            curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                            if(curr_chan_settings == False): curr_chan_settings = {}
                                            if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                            curr_chan_settings[use_area['id']]['spam_whitelist'] = get_whitelist
                                            await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)
                                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have removed <@'+found_user.id+'> from the <#'+use_area['id']+'> white list.')
                                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find that user on this white list.')
                                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find that user on this white list.')
                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find that user.')


                    if(proc_msg[2] == "settings"):
                        use_spam_action = await __main__.get_config('spam_action',message.server,'guard')
                        if(use_spam_action == False): use_spam_action = 'notify'
                        use_spam_action = use_spam_action+' (Server default)'

                        use_trigger_limit = await __main__.get_config('msg_limit_per_min',message.server,'guard')
                        if(use_trigger_limit == False or int(use_trigger_limit) == 0):
                            use_trigger_limit = 'off'
                        else: use_trigger_limit = str(use_trigger_limit)
                        use_trigger_limit = use_trigger_limit+' (Server default)'

                        use_spam_warning = await __main__.get_config('spam_warning',message.server,'guard')
                        if(use_spam_warning == False): use_spam_warning = 'off'
                        use_spam_warning = use_spam_warning+' (Server default)'

                        use_block_urls = await __main__.get_config('block_urls',message.server,'guard')
                        if(use_block_urls == False): use_block_urls = 'off'
                        use_block_urls = use_block_urls+' (Server default)'

                        use_block_text = await __main__.get_config('block_text',message.server,'guard')
                        if(use_block_text == False): use_block_text = 'off'
                        use_block_text = use_block_text+' (Server default)'

                        use_block_files = await __main__.get_config('block_files',message.server,'guard')
                        if(use_block_files == False): use_block_files = 'off'
                        use_block_files = use_block_files+' (Server default)'

                        use_one_post_per_person = await __main__.get_config('one_post_per_person',message.server,'guard')
                        if(use_one_post_per_person == False): use_one_post_per_person = 'off'
                        use_one_post_per_person = use_one_post_per_person+' (Server default)'

                        use_time_limit_between_posts = await __main__.get_config('time_limit_between_posts',message.server,'guard')
                        if(use_time_limit_between_posts == False or use_time_limit_between_posts == 0):
                            use_time_limit_between_posts = 'off'
                        else: use_time_limit_between_posts = str(use_time_limit_between_posts)+' seconds (Server default)'

                        if(proc_msg[1] != "server"):
                            curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                            if(curr_chan_settings != False):
                                if(use_area['id'] in curr_chan_settings):
                                    if('spam_action' in curr_chan_settings[use_area['id']]):
                                        use_spam_action = curr_chan_settings[use_area['id']]['spam_action']
                                    if('msg_limit_per_min' in curr_chan_settings[use_area['id']]):
                                        use_trigger_limit = str(curr_chan_settings[use_area['id']]['msg_limit_per_min'])
                                    if('spam_warning' in curr_chan_settings[use_area['id']]):
                                        use_spam_warning = curr_chan_settings[use_area['id']]['spam_warning']
                                    if('block_urls' in curr_chan_settings[use_area['id']]):
                                        use_block_urls = curr_chan_settings[use_area['id']]['block_urls']
                                    if('block_text' in curr_chan_settings[use_area['id']]):
                                        use_block_text = curr_chan_settings[use_area['id']]['block_text']
                                    if('block_files' in curr_chan_settings[use_area['id']]):
                                        use_block_files = curr_chan_settings[use_area['id']]['block_files']
                                    if('one_post_per_person' in curr_chan_settings[use_area['id']]):
                                        use_one_post_per_person = curr_chan_settings[use_area['id']]['one_post_per_person']
                                    if('time_limit_between_posts' in curr_chan_settings[use_area['id']]):
                                        use_time_limit_between_posts = curr_chan_settings[use_area['id']]['time_limit_between_posts']
                                        if(use_time_limit_between_posts == 0):
                                            use_time_limit_between_posts = 'off'
                                        else: use_time_limit_between_posts = str(use_time_limit_between_posts)+' seconds (Server default)'

                        if(use_trigger_limit == "0"): use_trigger_limit = 'off'
                        if(use_trigger_limit != "off" and use_trigger_limit != "off (Server default)"): use_trigger_limit = use_trigger_limit+' messages per minute'


                        icon_url = __main__.client.user.avatar_url
                        if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url

                        if(proc_msg[1] == "server"):
                            list_title = 'Default guard settings for the server'
                        else: list_title = 'Guard settings for '+use_area['name']+' channel'

                        #list_descript = '**Spam action:** '+use_spam_action
                        list_descript = '**Trigger limit:** '+use_trigger_limit
                        list_descript = list_descript+'\n**Spam warning:** '+use_spam_warning
                        list_descript = list_descript+'\n**Block URLs:** '+use_block_urls
                        list_descript = list_descript+'\n**Block text:** '+use_block_text
                        list_descript = list_descript+'\n**Block files:** '+use_block_files
                        list_descript = list_descript+'\n**One post per person:** '+use_one_post_per_person
                        list_descript = list_descript+'\n**Time limit between posts:** '+use_time_limit_between_posts

                        em = __main__.discord.Embed(title=list_title, description=list_descript, colour=3447003)
                        em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                        #em.set_thumbnail(url=icon_url)
                        #em.set_image(url)

                        await __main__.client.send_message(message.channel, embed=em)




                    if(proc_msg[2] == "clear_settings"):
                        if(proc_msg[1] != "server"):
                            curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                            if(curr_chan_settings == False): curr_chan_settings = {}
                            if(use_area['id'] in curr_chan_settings): del curr_chan_settings[use_area['id']]

                            await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the guard settings for <#'+use_area['id']+'> to server defaults.')
                        else:
                            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you can only clear settings for specific channels, not the server.')


                    '''
                    if(proc_msg[2] == "spam_action"):
                        proc_msg[3].lower()
                        if(proc_msg[3] == "notify" or proc_msg[3] == "timeout"):

                            if(proc_msg[1] == "server"):
                                await __main__.set_config('spam_action',message.server,'guard',proc_msg[3])
                            else:
                                curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                if(curr_chan_settings == False): curr_chan_settings = {}
                                if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                curr_chan_settings[use_area['id']]['spam_action'] = proc_msg[3]
                                await __main__.change_setting('channel_spam',message.server,'guard',curr_chan_settings)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the spam action for '+use_area['name']+' to "'+proc_msg[3]+'".')

                        else:
                            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either "notify" or "timeout".')
                    '''

                    if(proc_msg[2] == "trigger_limit"):
                        if(proc_msg[3] == "off"):
                            use_limit = 0
                        else: use_limit = proc_msg[3]
                        use_limit = int(use_limit)
                        if(use_limit <= 20 and use_limit >= 0):

                            if(proc_msg[1] == "server"):
                                await __main__.set_config('msg_limit_per_min',message.server,'guard',use_limit)
                            else:
                                curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                if(curr_chan_settings == False): curr_chan_settings = {}
                                if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                curr_chan_settings[use_area['id']]['msg_limit_per_min'] = use_limit
                                await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)

                             #await spam_check_remove_server(message.server)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the trigger limit for '+use_area['name']+' to "'+str(use_limit)+'".')
                        else:
                            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a number between 1 and 20, or "off" if you want to disable anti spam.')


                    if(proc_msg[2] == "spam_warning"):
                        proc_msg[3].lower()
                        if(proc_msg[3] == "on" or proc_msg[3] == "off"):

                            if(proc_msg[1] == "server"):
                                await __main__.set_config('spam_warning',message.server,'guard',proc_msg[3])
                            else:
                                curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                if(curr_chan_settings == False): curr_chan_settings = {}
                                if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                curr_chan_settings[use_area['id']]['spam_warning'] = proc_msg[3]
                                await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the spam warning for '+use_area['name']+' to "'+proc_msg[3]+'".')

                        else:
                            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either "on" or "off".')


                    if(proc_msg[2] == "block_urls"):
                        proc_msg[3].lower()
                        if(proc_msg[3] == "on" or proc_msg[3] == "off"):

                            if(proc_msg[1] == "server"):
                                await __main__.set_config('block_urls',message.server,'guard',proc_msg[3])
                            else:
                                curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                if(curr_chan_settings == False): curr_chan_settings = {}
                                if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                curr_chan_settings[use_area['id']]['block_urls'] = proc_msg[3]
                                await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set block posted urls for '+use_area['name']+' to "'+proc_msg[3]+'".')

                        else:
                            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either "on" or "off".')


                    if(proc_msg[2] == "block_text"):
                        proc_msg[3].lower()
                        if(proc_msg[3] == "on" or proc_msg[3] == "off"):

                            if(proc_msg[1] == "server"):
                                await __main__.set_config('block_text',message.server,'guard',proc_msg[3])
                            else:
                                curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                if(curr_chan_settings == False): curr_chan_settings = {}
                                if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                curr_chan_settings[use_area['id']]['block_text'] = proc_msg[3]
                                await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set block posted text for '+use_area['name']+' to "'+proc_msg[3]+'".')

                        else:
                            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either "on" or "off".')


                    if(proc_msg[2] == "block_files"):
                        proc_msg[3].lower()
                        if(proc_msg[3] == "on" or proc_msg[3] == "off"):

                            if(proc_msg[1] == "server"):
                                await __main__.set_config('block_files',message.server,'guard',proc_msg[3])
                            else:
                                curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                if(curr_chan_settings == False): curr_chan_settings = {}
                                if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                curr_chan_settings[use_area['id']]['block_files'] = proc_msg[3]
                                await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set block posted files for '+use_area['name']+' to "'+proc_msg[3]+'".')

                        else:
                            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either "on" or "off".')


                    if(proc_msg[2] == "one_post_per_person"):
                        proc_msg[3].lower()
                        if(proc_msg[3] == "on" or proc_msg[3] == "off"):

                            if(proc_msg[1] == "server"):
                                await __main__.set_config('one_post_per_person',message.server,'guard',proc_msg[3])
                            else:
                                curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                if(curr_chan_settings == False): curr_chan_settings = {}
                                if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                curr_chan_settings[use_area['id']]['one_post_per_person'] = proc_msg[3]
                                await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set one post per person for '+use_area['name']+' to "'+proc_msg[3]+'".')

                        else:
                            await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either "on" or "off".')


                    if(proc_msg[2] == "time_limit_between_posts"):

                        if(proc_msg_length >= 4):

                            if(proc_msg_length == 4):
                                proc_msg[3].lower()
                                if(proc_msg[3] == "off"):
                                    use_time = 0
                            else: use_time = await __main__.cmd_time_args(proc_msg[3],proc_msg[4]) 

                            if(use_time == 0):
                                use_time_text = 'off'
                            else:
                                use_time_text = proc_msg[3]+' '+proc_msg[4]

                            if(proc_msg[1] == "server"):
                                await __main__.set_config('time_limit_between_posts',message.server,'guard',use_time)
                            else:
                                curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
                                if(curr_chan_settings == False): curr_chan_settings = {}
                                if(use_area['id'] not in curr_chan_settings): curr_chan_settings[use_area['id']] = {}

                                curr_chan_settings[use_area['id']]['time_limit_between_posts'] = use_time
                                await __main__.set_config('channel_spam',message.server,'guard',curr_chan_settings)
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set the time limit between posts for '+use_area['name']+' to '+use_time_text+'.')

                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either the length of time required between posts, or "off".')




                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a place. Which can either be "server" or a channel name, I couldn\'t find a channel called "'+str(proc_msg[1])+'".')



async def user_on_guard_whitelist(message):
    on_whitelist = False
    if(message.author.id == __main__.client.user.id):
        on_whitelist = True
    else:
        curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
        if(curr_chan_settings == False): curr_chan_settings = {}

        server_spam_whitelist = await __main__.get_config('spam_whitelist',message.server,'guard')
        if(server_spam_whitelist == False): server_spam_whitelist = []

        channel_spam_whitelist = []
        if(message.channel.id in curr_chan_settings and 'spam_whitelist' in curr_chan_settings[message.channel.id]):
            channel_spam_whitelist = curr_chan_settings[message.channel.id]['spam_whitelist']

        if(on_whitelist == False):
            for clear_user in channel_spam_whitelist:
                if(str(clear_user) == str(message.author.id)):
                    on_whitelist = True
                    break

        if(on_whitelist == False):
            for clear_user in server_spam_whitelist:
                if(str(clear_user) == str(message.author.id)):
                    on_whitelist = True
                    break

    return on_whitelist


async def spam_check_remove_user(server_obj,user_obj):
    if(server_obj.id in msg_count and user_obj.id in msg_count[server_obj.id]):
        del msg_count[server_obj.id][user_obj.id]
        if(__main__.verbose_out == True): await __main__.log_entry('Removing '+user_obj.name+'#'+user_obj.discriminator+' from '+server_obj.name+' spam tracker',server_obj)

async def spam_check_remove_server(server_obj):
    if(server_obj.id in msg_count):
        del msg_count[server_obj.id]
        if(__main__.verbose_out == True): await __main__.log_entry('Removing server '+server_obj.name+' from spam tracker',server_obj)


async def spam_check(message):
    use_spam_action = await __main__.get_config('spam_action',message.server,'guard')
    if(use_spam_action == False): use_spam_action = 'notify'

    use_trigger_limit = await __main__.get_config('msg_limit_per_min',message.server,'guard')
    if(use_trigger_limit == False):
        use_trigger_limit = 0
    else: use_trigger_limit = int(use_trigger_limit)

    use_spam_warning = await __main__.get_config('spam_warning',message.server,'guard')
    if(use_spam_warning == False): use_spam_warning = 'off'

    curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
    if(curr_chan_settings != False):
        if(message.channel.id in curr_chan_settings):
            if('spam_action' in curr_chan_settings[message.channel.id]): use_spam_action = curr_chan_settings[message.channel.id]['spam_action']
            if('msg_limit_per_min' in curr_chan_settings[message.channel.id]): use_trigger_limit = int(curr_chan_settings[message.channel.id]['msg_limit_per_min'])
            if('spam_warning' in curr_chan_settings[message.channel.id]): use_spam_warning = curr_chan_settings[message.channel.id]['spam_warning']
    else: curr_chan_settings = {}

    run_anti_spam = True
    msg_limit_per_min = use_trigger_limit

    timeout_available = False
    timeout_role = await __main__.get_config('timeout_add_role',message.server,'users')
    if(timeout_role != False): timeout_available = True

    spam_action = use_spam_action

    if(msg_limit_per_min > 0 and run_anti_spam == True):

        msg_time = message.timestamp
        msg_time = msg_time.timestamp()

        reset_tracker = False
        if(message.server.id not in msg_count): msg_count[message.server.id] = {}
        if(message.author.id not in msg_count[message.server.id]):
            reset_tracker = True
        elif(msg_count[message.server.id][message.author.id]['chan'] != message.channel.id):
            reset_tracker = True

        if(reset_tracker == True):
            msg_count[message.server.id][message.author.id] = {}
            msg_count[message.server.id][message.author.id]['chan'] = message.channel.id
            msg_count[message.server.id][message.author.id]['count'] = []
            msg_count[message.server.id][message.author.id]['notified'] = False
            msg_count[message.server.id][message.author.id]['warned'] = False

        mc_len = len(msg_count[message.server.id][message.author.id]['count'])

        if(mc_len > msg_limit_per_min):
            if(mc_len >= 21): del msg_count[message.server.id][message.author.id]['count'][0]
            limit_key = 0
            limit_key = (mc_len - 1) - msg_limit_per_min
            oldest_time = msg_count[message.server.id][message.author.id]['count'][limit_key]
            time_diff = msg_time - oldest_time
            if(time_diff <= 60):
                msg_count[message.server.id][message.author.id]['count'] = []

                if(use_spam_warning == "on" and msg_count[message.server.id][message.author.id]['warned'] == False):

                    await __main__.client.send_message(message.channel,'Please do not spam posts <@'+message.author.id+'>, thank you.')
                    msg_count[message.server.id][message.author.id]['warned'] = True

                else:
                    notify_mods = await __main__.bot_use_channel(message.server,'guard','spam_alert_channel')
                    notify_role = await __main__.get_config('spam_alert_role',message.server,'guard')
                    if(notify_mods != False and msg_count[message.server.id][message.author.id]['notified'] == False):
                        #remove this
                        timeout_available = False
                        #remove this
                        if(spam_action == "notify" or (timeout_available == False and spam_action == "timeout")):
                            if(__main__.verbose_out == True): await __main__.log_entry('Detected spam from '+message.author.name+'#'+message.author.discriminator+' in '+message.channel.name+' ('+message.server.name+')',message.server)

                            '''
                            if(spam_action == "timeout"):
                                to_error = ' I\'m supposed to put them into timeout, but I can\'t because my timeout channel and timeout role settings have not been set.'
                            else: to_error = ''
                            '''
                            to_error = ''

                            alert_note = '<@'+message.author.id+'> ('+message.author.name+'#'+message.author.discriminator+') is spamming in <#'+message.channel.id+'>.'+to_error
                        else:
                            #TODO: ADAPT TIMEOUT STUFFS
                            print("timeout this user")
                            #await auto_timeout_user(message.server,message.author.id)
                            alert_note = 'I\'ve put <@'+message.author.id+'> ('+message.author.name+'#'+message.author.discriminator+') into timeout for spamming in <#'+message.channel.id+'>, please investigate this matter.'

                        if(notify_role != False):
                            use_alert_note = await __main__.create_alert(message.server,notify_role,alert_note)
                        else: use_alert_note = alert_note

                        await __main__.client.send_message(notify_mods,use_alert_note)
                        msg_count[message.server.id][message.author.id]['notified'] = True

        msg_count[message.server.id][message.author.id]['count'].append(msg_time)


async def check_block_filters(message):
    block_filters_passed = True

    use_block_urls = await __main__.get_config('block_urls',message.server,'guard')
    if(use_block_urls == False): use_block_urls = 'off'

    use_block_text = await __main__.get_config('block_text',message.server,'guard')
    if(use_block_text == False): use_block_text = 'off'

    use_block_files = await __main__.get_config('block_files',message.server,'guard')
    if(use_block_files == False): use_block_files = 'off'

    curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
    if(curr_chan_settings != False):
        if(message.channel.id in curr_chan_settings):
            if('block_urls' in curr_chan_settings[message.channel.id]):
                use_block_urls = curr_chan_settings[message.channel.id]['block_urls']
            if('block_text' in curr_chan_settings[message.channel.id]):
                use_block_text = curr_chan_settings[message.channel.id]['block_text']
            if('block_files' in curr_chan_settings[message.channel.id]):
                use_block_files = curr_chan_settings[message.channel.id]['block_files']

    failed_on = ''
    allowed_filters = []

    if(use_block_urls == "on"):
        if(block_filters_passed == True):
            if('http' in message.content or 'https' in message.content):
                block_filters_passed = False
                failed_on = 'URLs'
    else: allowed_filters.append('URLs')

    if(use_block_text == "on"):
        if(block_filters_passed == True):
            process_message_content = message.content
            for word_item in process_message_content.split(" "):
                if(word_item.startswith('http')): process_message_content = process_message_content.replace(word_item,'')
            process_message_content = process_message_content.replace(" ","")
            if(process_message_content != ""):
                block_filters_passed = False
                failed_on = 'text'
    else: allowed_filters.append('text')

    if(use_block_files == "on"):
        if(block_filters_passed == True):
            if(len(message.attachments) > 0):
                block_filters_passed = False
                failed_on = 'file attachments'
    else: allowed_filters.append('file attachments')


    if(block_filters_passed == False):
        allowed_filters_text = ''
        af_run = 0
        while(af_run < len(allowed_filters)):
            if(allowed_filters_text != ""):
                if(allowed_filters[af_run] == allowed_filters[-1]):
                    allowed_filters_text = allowed_filters_text+' or '
                else:
                    allowed_filters_text = allowed_filters_text+', '
            allowed_filters_text = allowed_filters_text+allowed_filters[af_run]
            af_run = af_run + 1

        await __main__.client.send_message(message.author,'Sorry '+message.author.display_name+', you\'re not allowed to post '+failed_on+' in the '+message.channel.name+' channel. You are allowed to post '+allowed_filters_text+'.')
        await __main__.client.delete_message(message)


    return block_filters_passed



async def check_post_frequency(message):
    block_filters_passed = True

    use_one_post_per_person = await __main__.get_config('one_post_per_person',message.server,'guard')
    if(use_one_post_per_person == False): use_one_post_per_person = 'off'

    use_time_limit_between_posts = await __main__.get_config('time_limit_between_posts',message.server,'guard')
    if(use_time_limit_between_posts == False): use_time_limit_between_posts = 0

    curr_chan_settings = await __main__.get_config('channel_spam',message.server,'guard')
    if(curr_chan_settings != False):
        if(message.channel.id in curr_chan_settings):
            if('one_post_per_person' in curr_chan_settings[message.channel.id]):
                use_one_post_per_person = curr_chan_settings[message.channel.id]['one_post_per_person']
            if('time_limit_between_posts' in curr_chan_settings[message.channel.id]):
                use_time_limit_between_posts = curr_chan_settings[message.channel.id]['time_limit_between_posts']


    if(use_time_limit_between_posts > 0 and block_filters_passed == True):
        last_msg = None
        async for m in __main__.client.logs_from(message.channel,limit=100):
            if(m.author == message.author and m.id != message.id):
                last_msg = m
                break
        if(last_msg != None):
            time_diff = message.timestamp.timestamp() - last_msg.timestamp.timestamp()
            if(time_diff < use_time_limit_between_posts):
                block_filters_passed = False
                time_left = (last_msg.timestamp.timestamp() + use_time_limit_between_posts) - message.timestamp.timestamp()
                time_left = __main__.math.ceil(time_left)
                time_left_string = await __main__.convert_seconds_to_time_string(time_left)
                await __main__.client.send_message(message.author,'Sorry '+message.author.display_name+', you\'re not allowed to post anything in the '+message.channel.name+' channel for another '+str(time_left_string)+'.')
                await __main__.client.delete_message(message)


    if(use_one_post_per_person == "on" and block_filters_passed == True):
        delete_limit = 10
        delete_count = 0
        async for m in __main__.client.logs_from(message.channel,limit=100):
            if(m.author == message.author and m.id != message.id):
                await __main__.client.delete_message(m)
                delete_count = delete_count + 1
                if(delete_count == delete_limit): break

    return block_filters_passed


async def message_new(message):
    check_whitelist = await user_on_guard_whitelist(message)
    if(check_whitelist == False):
        filters_passed = await check_block_filters(message)
        if(filters_passed == True):
            frequency_passed = await check_post_frequency(message)
            if(frequency_passed == True): await spam_check(message)

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
