#!/usr/bin/python

import __main__
import json

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Server statistics'
    help_info['description'] = 'Track channel activity on this server.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'stats'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'server'
    help_entry['args'] = 'mmm yyyy'
    help_entry['description'] = 'View the number of posts made in text channels across the server for month mmm and year yyyy. If month and date are not specified, the current month and date will be used instead.'
    help_entry['perm_name'] = 'view_stats'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'channel_name mmm yyyy'
    help_entry['description'] = 'View the number of posts made in channel_name for month mmm and year yyyy. If month and date are not specified, the current month and date will be used instead.'
    help_entry['perm_name'] = 'view_stats'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'view_stats'
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

async def stats_next_key(date_key=None,date_dir=None):
    ret_str = False
    if(date_key != None and date_dir != None):
        date_key = date_key.lower()
        dk_split = date_key.split(" ")
        dk_split[1] = int(dk_split[1])

        if(date_dir == "next"):
            if(dk_split[0] == "jan"): dk_split[0] = 'feb'
            elif(dk_split[0] == "feb"): dk_split[0] = 'mar'
            elif(dk_split[0] == "mar"): dk_split[0] = 'apr'
            elif(dk_split[0] == "apr"): dk_split[0] = 'may'
            elif(dk_split[0] == "may"): dk_split[0] = 'jun'
            elif(dk_split[0] == "jun"): dk_split[0] = 'jul'
            elif(dk_split[0] == "jul"): dk_split[0] = 'aug'
            elif(dk_split[0] == "aug"): dk_split[0] = 'sep'
            elif(dk_split[0] == "sep"): dk_split[0] = 'oct'
            elif(dk_split[0] == "oct"): dk_split[0] = 'nov'
            elif(dk_split[0] == "nov"): dk_split[0] = 'dec'
            elif(dk_split[0] == "dec"):
                dk_split[0] = 'jan'
                dk_split[1] = dk_split[1] + 1
        else:
            if(dk_split[0] == "dec"): dk_split[0] = 'nov'
            elif(dk_split[0] == "nov"): dk_split[0] = 'oct'
            elif(dk_split[0] == "oct"): dk_split[0] = 'sep'
            elif(dk_split[0] == "sep"): dk_split[0] = 'aug'
            elif(dk_split[0] == "aug"): dk_split[0] = 'jul'
            elif(dk_split[0] == "jul"): dk_split[0] = 'jun'
            elif(dk_split[0] == "jun"): dk_split[0] = 'may'
            elif(dk_split[0] == "may"): dk_split[0] = 'apr'
            elif(dk_split[0] == "apr"): dk_split[0] = 'mar'
            elif(dk_split[0] == "mar"): dk_split[0] = 'feb'
            elif(dk_split[0] == "feb"): dk_split[0] = 'jan'
            elif(dk_split[0] == "jan"):
                dk_split[0] = 'dec'
                dk_split[1] = dk_split[1] - 1

        ret_str = dk_split[0]+' '+str(dk_split[1])

    return ret_str


async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)
    if(message.content.startswith(bot_cmd_char+'stats')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'stats','view_stats',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 2):
                time_now = await __main__.current_timestamp()
                use_server_id = await __main__.hash_server_id(message.server.id)
                
                if(proc_msg[1] != "server"):
                    use_channel = await __main__.find_channel_arg(message.server,proc_msg[1],True)
                else: use_channel = False
                
                if(proc_msg_length == 4):
                    date_key = proc_msg[2]+' '+proc_msg[3]
                else:
                    date_key = __main__.datetime.datetime.fromtimestamp(int(time_now)).strftime('%b %Y')
                date_key = date_key.lower()
                
                icon_url = __main__.client.user.avatar_url
                if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url
                
                if(proc_msg[1] == "server"):
                    list_title = 'Statistics for server'
                else: list_title = 'Statistics for channel '+use_channel.name
                list_descript = ''
                list_title = list_title+' **('+date_key.title()+')**'
                
                if(proc_msg[1] == "server"):
                    
                    prev_date_key = await stats_next_key(date_key,'prev')
                    total_posts = 0
                    chan_data = []
                    
                    get_stats = __main__.db.cursor()
                    get_stats.execute("SELECT * FROM channels WHERE server_id=? AND deleted='0'",(use_server_id,))
                    for row in get_stats:
                        get_count = await __main__.decrypt_data(row['post_count'])
                        if(get_count == False or get_count == None or get_count == ''):
                            get_count = {}
                        else: get_count = json.loads(get_count)

                        if(date_key in get_count):
                            curr_count = int(get_count[date_key]['count'])
                        else: curr_count = 0
                        if(curr_count > 0):
                            curr_appd = curr_count / 30
                        else: curr_appd = 0
                        curr_appd = round(curr_appd,2)

                        if(prev_date_key in get_count):
                            prev_count = int(get_count[prev_date_key]['count'])
                        else: prev_count = 0
                        prev_diff = curr_count - prev_count
                        if(prev_diff >= 0): prev_diff = '+'+str(prev_diff)

                        use_channel_name = await __main__.decrypt_data(row['name'])

                        total_posts = total_posts + curr_count
                        #if(curr_count > 0): list_descript = list_descript+'**'+use_channel_name+' - **'+str(curr_count)+' posts ('+str(prev_diff)+')\n'
                        add_chan_data = {}
                        add_chan_data['name'] = use_channel_name
                        add_chan_data['posts'] = curr_count
                        add_chan_data['prev_diff'] = prev_diff
                        chan_data.append(add_chan_data)

                    sort_chan_data = []
                    done_data = []
                    while(len(done_data) < len(chan_data)):
                        last_highest = False
                        for data in chan_data:
                            if((last_highest == False or last_highest['posts'] <= data['posts']) and data not in done_data):
                                last_highest = data
                        done_data.append(last_highest)
                        sort_chan_data.append(last_highest)

                    for data in sort_chan_data:
                        list_descript = list_descript+'**'+data['name']+' - **'+str(data['posts'])+' posts ('+str(data['prev_diff'])+')\n'

                        if(len(list_descript) >= 1600):
                            em = __main__.discord.Embed(title=list_title, description=list_descript, colour=3447003)
                            em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                            await __main__.client.send_message(message.channel, embed=em)
                            list_descript = ''
                    
                    total_appd = total_posts / 30
                    total_appd = round(total_appd,2)
                    list_descript = list_descript+'\n**TOTAL POSTS - **'+str(total_posts)
                    
                    if(len(list_descript) > 1):
                        em = __main__.discord.Embed(title=list_title, description=list_descript, colour=3447003)
                        em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                        await __main__.client.send_message(message.channel, embed=em)

                else:
                    if(use_channel != False):
                        use_channel_id = await __main__.hash_member_id(message.server.id,use_channel.id)

                        get_stats = __main__.db.cursor()
                        get_stats.execute("SELECT * FROM channels WHERE server_id=? AND deleted='0' AND channel_id=?",(use_server_id,use_channel_id,))
                        for row in get_stats:
                            get_count = await __main__.decrypt_data(row['post_count'])
                            if(get_count == False or get_count == None or get_count == ''):
                                get_count = {}
                            else: get_count = json.loads(get_count)

                        use_date_key = date_key
                        run_count = 0
                        while(run_count <= 12):

                            prev_date_key = await stats_next_key(use_date_key,'prev')

                            if(use_date_key in get_count):
                                curr_count = int(get_count[use_date_key]['count'])
                            else: curr_count = 0
                            if(curr_count > 0):
                                curr_appd = curr_count / 30
                            else: curr_appd = 0
                            curr_appd = round(curr_appd,2)

                            if(prev_date_key in get_count):
                                prev_count = int(get_count[prev_date_key]['count'])
                            else: prev_count = 0
                            prev_diff = curr_count - prev_count
                            if(prev_diff >= 0): prev_diff = '+'+str(prev_diff)

                            if(curr_count > 0): list_descript = list_descript+'**'+use_date_key.title()+' - **'+str(curr_count)+' posts ('+str(prev_diff)+')\n'

                            use_date_key = await stats_next_key(use_date_key,'prev')
                            run_count = run_count + 1

                        if(list_descript == ''): list_descript = 'There are no stats for this channel to display.'

                        em = __main__.discord.Embed(title=list_title, description=list_descript, colour=3447003)
                        em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                        #em.set_thumbnail(url=icon_url)
                        #em.set_image(url)

                        await __main__.client.send_message(message.channel, embed=em)


                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[1]+'"')

            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must at least specify a place, which can be either "server" or a channel name.')




async def message_new(message):
    if(message.channel.is_private == False):
        time_now = await __main__.current_timestamp()
        use_server_id = await __main__.hash_server_id(message.server.id)
        use_channel_id = await __main__.hash_member_id(message.server.id,message.channel.id)
        day_key = __main__.datetime.datetime.fromtimestamp(int(time_now)).strftime('%a')
        day_key = day_key.lower()
        hour_key = __main__.datetime.datetime.fromtimestamp(int(time_now)).strftime('%H')
        date_key = __main__.datetime.datetime.fromtimestamp(int(time_now)).strftime('%b %Y')
        date_key = date_key.lower()

        #adjust channel activity count
        get_mets = __main__.db.cursor()
        get_mets.execute("SELECT * FROM channels WHERE server_id=? AND channel_id=?",(use_server_id,use_channel_id,))
        found_mets = False
        for row in get_mets:
            found_mets = await __main__.decrypt_data(row['post_count'])

        if(found_mets == None or found_mets == False or found_mets == ""):
            found_mets = {}
        else: found_mets = json.loads(found_mets)

        if(date_key not in found_mets):
            found_mets[date_key] = {}
            found_mets[date_key]['count'] = 0

        found_mets[date_key]['count'] = found_mets[date_key]['count'] + 1
        found_mets = await __main__.encrypt_data(json.dumps(found_mets))

        save_mets = __main__.db.cursor()
        save_mets.execute("UPDATE channels SET post_count=? WHERE server_id=? AND channel_id=?",(found_mets,use_server_id,use_channel_id,))
        __main__.db.commit()


        #adjust user activity counts
        if(message.author.id != __main__.client.user.id):
            use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)

            get_mets = __main__.db.cursor()
            get_mets.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id))
            for row in get_mets:
                post_count = await __main__.decrypt_data(row['post_count'])

            if(post_count != False and post_count != None and post_count != ""):
                post_count = json.loads(post_count)
            else: post_count = {}

            if(date_key not in post_count):
                post_count[date_key] = {}
                post_count[date_key]['total'] = 0
                post_count[date_key]['days'] = {}
                post_count[date_key]['channels'] = {}

            post_count[date_key]['total'] = post_count[date_key]['total'] + 1

            if(day_key not in post_count[date_key]['days']):
                post_count[date_key]['days'][day_key] = {}
                post_count[date_key]['days'][day_key]['total'] = 0
                post_count[date_key]['days'][day_key]['hours'] = {}
            post_count[date_key]['days'][day_key]['total'] = post_count[date_key]['days'][day_key]['total'] + 1

            if(hour_key not in post_count[date_key]['days'][day_key]['hours']): post_count[date_key]['days'][day_key]['hours'][hour_key] = 0
            post_count[date_key]['days'][day_key]['hours'][hour_key] = post_count[date_key]['days'][day_key]['hours'][hour_key] + 1

            if(message.channel.id not in post_count[date_key]['channels']): post_count[date_key]['channels'][message.channel.id] = 0
            post_count[date_key]['channels'][message.channel.id] = post_count[date_key]['channels'][message.channel.id] + 1

            post_count = await __main__.encrypt_data(json.dumps(post_count))

            save_mets.execute("UPDATE users SET post_count=? WHERE user_id=? AND server_id=?",(post_count,use_member_id,use_server_id))
            __main__.db.commit()
            


async def user_info_data(server,user):
    ret_data = []
    use_server_id = await __main__.hash_server_id(server.id)
    use_member_id = await __main__.hash_member_id(server.id,user.id)

    last_seen_timestamp = False
    used_code = __main__.db.cursor()
    used_code.execute("SELECT * FROM users WHERE server_id=? AND user_id=?",(use_server_id,use_member_id,))
    for row in used_code:
        post_count = await __main__.decrypt_data(row['post_count'])
        if(row['last_seen'] != None and row['last_seen'] != ""): last_seen_timestamp = int(row['last_seen'])

    if(post_count != False and post_count != None and post_count != ""):
        post_count = json.loads(post_count)
        if(len(post_count) > 0):

            time_now = await __main__.current_timestamp()
            date_key = __main__.datetime.datetime.fromtimestamp(int(time_now)).strftime('%b %Y')
            date_key = date_key.lower()
            found_key = False
            while(found_key == False):
                if(date_key not in post_count):
                    date_key = await stats_new_key(date_key,'prev')
                else:
                    found_key = True
            prev_date_key = await stats_next_key(date_key,'prev')

            count_total = 0
            if(date_key in post_count): count_total = count_total + post_count[date_key]['total']
            if(prev_date_key in post_count): count_total = count_total + post_count[prev_date_key]['total']

            #active days
            weekdays_str = '';
            if(last_seen_timestamp != False): weekdays_str = '__Last seen__\n'+str(await __main__.timestamp_to_date(last_seen_timestamp))
            weekdays_run = ['mon','tue','wed','thu','fri','sat','sun']
            for weekday in weekdays_run:
                day_total = 0
                if(date_key in post_count and weekday in post_count[date_key]['days']): day_total = day_total + post_count[date_key]['days'][weekday]['total']
                if(prev_date_key in post_count and weekday in post_count[prev_date_key]['days']): day_total = day_total + post_count[prev_date_key]['days'][weekday]['total']
                day_percent = round((day_total / count_total) * 100,0)
                if(day_total > 0):

                    hour_run = 0
                    hour_block = ''
                    hour_block_total = 0
                    hours_out = ''
                    while(hour_run <= 23):
                        use_hour_key = hour_run
                        if(use_hour_key <= 9):
                            use_hour_key = '0'+str(use_hour_key)
                        else: use_hour_key = str(use_hour_key)

                        hour_total = 0
                        if(date_key in post_count and weekday in post_count[date_key]['days'] and use_hour_key in post_count[date_key]['days'][weekday]['hours']):
                            hour_total = hour_total + post_count[date_key]['days'][weekday]['hours'][use_hour_key]
                        if(prev_date_key in post_count and weekday in post_count[prev_date_key]['days'] and use_hour_key in post_count[prev_date_key]['days'][weekday]['hours']):
                            hour_total = hour_total + post_count[prev_date_key]['days'][weekday]['hours'][use_hour_key]
                        
                        if(hour_total > 0): hour_block_total = hour_block_total + hour_total
                        if(hour_block == '' and hour_run != 23):
                                if(hour_total > 0): hour_block = use_hour_key+':00 - '
                        else:
                            if(hour_block == '' and hour_run == 23):
                                    if(hour_total > 0): hour_block = use_hour_key+':00 - '

                            if(hour_total == 0 or hour_run == 23):
                                hour_percent = round((hour_block_total / day_total) * 100,0)
                                if(hour_run == 23):
                                    last_time = '23:59'
                                else: last_time = use_hour_key+':00'
                                if(hour_block_total > 0):
                                    hour_block = hour_block+last_time+' ('+str(hour_percent)+'% / '+str(hour_block_total)+')'
                                    if(hours_out != ''): hours_out = hours_out+', '
                                    hours_out = hours_out+hour_block
                                hour_block = ''
                                hour_block_total = 0

                        hour_run = hour_run + 1

                    weekdays_str = weekdays_str+'\n\n__'+weekday.capitalize()+' ('+str(day_percent)+'% / '+str(day_total)+')__\n'+hours_out

            if(weekdays_str != ""):
                b_field = {}
                b_field['name'] = 'Active times (UTC)'
                b_field['value'] = weekdays_str
                b_field['inline'] = True
                ret_data.append(b_field)


            #active channels
            use_channels = []
            if(date_key in post_count):
                for this_channel in post_count[date_key]['channels']:
                    if(this_channel not in use_channels): use_channels.append(this_channel)
            if(prev_date_key in post_count):
                for this_channel in post_count[prev_date_key]['channels']:
                    if(this_channel not in use_channels): use_channels.append(this_channel)

            channels_str = ''
            for this_channel in use_channels:
                this_channel_total = 0

                if(date_key in post_count and this_channel in post_count[date_key]['channels']):
                    this_channel_total = this_channel_total + post_count[date_key]['channels'][this_channel]
                if(prev_date_key in post_count and this_channel in post_count[prev_date_key]['channels']):
                    this_channel_total = this_channel_total + post_count[prev_date_key]['channels'][this_channel]

                if(this_channel_total > 0):
                    channel_obj = await __main__.find_channel_arg(server,'<#'+this_channel+'>',True)
                    if(channel_obj != False):
                        this_channel_percent = round((this_channel_total / count_total) * 100,0)
                        channels_str = channels_str+'\n**-** '+channel_obj.name+' ('+str(this_channel_percent)+'% / '+str(this_channel_total)+')'

            if(channels_str != ""):
                b_field = {}
                b_field['name'] = 'Active channels'
                b_field['value'] = channels_str
                b_field['inline'] = True
                ret_data.append(b_field)


    if(len(ret_data) == 0): ret_data = False
    return ret_data



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
