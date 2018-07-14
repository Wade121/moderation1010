#!/usr/bin/python

import __main__
import json
import math

global last_search_crit
last_search_crit = {}

global xp_cool_log
xp_cool_log = {}

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Member profiles'
    help_info['description'] = 'Setup your public profile for other members to see.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'profile'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'add_field'
    help_entry['args'] = 'field_name'
    help_entry['description'] = 'Adds field_name to all user profiles as an optional field.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'field_list'
    help_entry['args'] = ''
    help_entry['description'] = 'Lists all the fields available on the profiles'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'edit_field'
    help_entry['args'] = 'field_id field_name'
    help_entry['description'] = 'Renames the field with ID field_id to field_name.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'del_field'
    help_entry['args'] = 'field_id'
    help_entry['description'] = 'Deletes the field with ID field_id.'
    help_entry['perm_name'] = 'change_settings'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'member_name'
    help_entry['description'] = 'View member_name\'s profile.'
    help_entry['perm_name'] = 'view_profiles'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = ''
    help_entry['description'] = 'View your own profile and how to set its fields.'
    help_entry['perm_name'] = 'view_profiles'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'set'
    help_entry['args'] = 'field_name'
    help_entry['description'] = 'Sets what the field called field_name says on your profile.'
    help_entry['perm_name'] = 'view_profiles'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'search'
    help_entry['args'] = 'criteria1, criteria2, criteria3...'
    help_entry['description'] = 'Search for profiles with matching criteria. Each criteria is a role name they must have to match, you can also put a minus in front of a role name to specify if they shouldn\'t have that role.'
    help_entry['perm_name'] = 'view_profiles'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'change_settings'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')

    this_perm = 'view_profiles'
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


async def earn_xp(user,server):
    xp_amount = 1
    xp_cooldown = 20

    time_now = await __main__.current_timestamp()
    if(server.id not in xp_cool_log): xp_cool_log[server.id] = {}
    if(user.id in xp_cool_log[server.id]):
        time_diff = time_now - xp_cool_log[server.id][user.id]
    else: time_diff = xp_cooldown

    if(time_diff >= xp_cooldown):
        use_server_id = await __main__.hash_server_id(server.id)
        use_member_id = await __main__.hash_member_id(server.id,user.id)

        user_creds = __main__.db.cursor()
        user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
        found_balance = 0
        for row in user_creds:
            if(row['xp'] != None and row['xp'] != ""):
                dec_balance = await __main__.decrypt_data(row['xp'])
                if(dec_balance != False): found_balance = int(dec_balance)

        new_balance = found_balance + xp_amount
        save_balance = await __main__.encrypt_data(str(new_balance))
        user_creds.execute("UPDATE users SET xp=? WHERE user_id=? AND server_id=?",(save_balance,use_member_id,use_server_id,))
        __main__.db.commit()

        orig_level = await xp_to_level(found_balance)
        new_level = await xp_to_level(new_balance)
        if(new_level > orig_level): await __main__.client.send_message(user,'Level up! You are now level '+str(new_level)+' on '+server.name+' :)')

        xp_cool_log[server.id][user.id] = time_now


async def xp_to_level(xp_amount):
    xp_amount = int(xp_amount)
    level_count = 0
    level_step = 25
    next_barrier = level_step
    exhausted_xp = False
    while(exhausted_xp == False and xp_amount > 0):
        if(xp_amount >= next_barrier):
            level_count = level_count + 1
            xp_amount = xp_amount - next_barrier
            next_barrier = next_barrier + level_step
        else: exhausted_xp = True
    return level_count


#===================================================================================================================
#MESSAGE EVENTS

async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)
    if(message.content.startswith(bot_cmd_char+'profile')):
        proc_msg = await __main__.get_cmd_args(message.content,2)
        proc_msg_length = len(proc_msg)
        if(proc_msg_length == 1):
            proc_msg[1] = '<@'+message.author.id+'>'
            proc_msg_length = 2

        use_server_id = await __main__.hash_server_id(message.server.id)
        load_profile = True

        if(proc_msg[1] == "add_field"):
            load_profile = False
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'profile','change_settings',True)
            if(chk_user_perm == True):
                if(proc_msg_length >= 3):
                    save_field_name = await __main__.encrypt_data(proc_msg[2])
                    chk_field = __main__.db.cursor()
                    chk_field.execute("INSERT INTO profile_fields (server_id,field_name) VALUES (?,?)",(use_server_id,save_field_name,))
                    __main__.db.commit()
                    await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have added the field "'+proc_msg[2]+'" to all profiles.')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the name of the field you want to add.')


        if(proc_msg[1] == "field_list"):
            load_profile = False
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'profile','change_settings',True)
            if(chk_user_perm == True):
                get_list = __main__.db.cursor()
                get_list.execute("SELECT * FROM profile_fields WHERE server_id=? ORDER BY id ASC",(use_server_id,))
                get_list_count = 0
                build_fields = ''
                for row in get_list:
                    get_list_count = get_list_count + 1
                    field_name = await __main__.decrypt_data(row['field_name'])
                    build_fields = build_fields+'**'+str(row['id'])+' - ** '+str(field_name)+'\n'

                icon_url = __main__.client.user.avatar_url
                if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url

                if(get_list_count == 0):
                    list_descript = 'No fields have been setup for the user profiles yet..'
                else: list_descript = build_fields

                em = __main__.discord.Embed(title='Custom profile fields', description=list_descript, colour=3447003)
                em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
                #em.set_thumbnail(url=icon_url)
                #em.set_image(url)

                await __main__.client.send_message(message.channel, embed=em)


        if(proc_msg[1] == "edit_field"):
            load_profile = False
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'profile','change_settings',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,3)
                proc_msg_length = len(proc_msg)
                if(proc_msg_length >= 4):

                    get_list = __main__.db.cursor()
                    get_list.execute("SELECT * FROM profile_fields WHERE server_id=? AND id=?",(use_server_id,proc_msg[2],))
                    get_list_count = 0
                    get_field_name = ''
                    for row in get_list:
                        get_list_count = get_list_count + 1
                        get_field_name = await __main__.decrypt_data(row['field_name'])

                    if(get_list_count == 1):
                        save_field_name = await __main__.encrypt_data(proc_msg[3])
                        del_field = __main__.db.cursor()
                        del_field.execute("UPDATE profile_fields SET field_name=? WHERE server_id=? AND id=?",(save_field_name,use_server_id,proc_msg[2],))
                        __main__.db.commit()

                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have renamed the profile field from "'+get_field_name+'" to "'+proc_msg[3]+'".')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a field with ID "'+str(proc_msg[2])+'".')

                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the ID number of the field you want to edit and its new name.')


        if(proc_msg[1] == "del_field"):
            load_profile = False
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'profile','change_settings',True)
            if(chk_user_perm == True):
                if(proc_msg_length >= 3):

                    get_list = __main__.db.cursor()
                    get_list.execute("SELECT * FROM profile_fields WHERE server_id=? AND id=?",(use_server_id,proc_msg[2],))
                    get_list_count = 0
                    get_field_name = ''
                    for row in get_list:
                        get_list_count = get_list_count + 1
                        get_field_name = await __main__.decrypt_data(row['field_name'])

                    if(get_list_count == 1):
                        del_field = __main__.db.cursor()
                        del_field.execute("DELETE FROM profile_fields WHERE server_id=? AND id=?",(use_server_id,proc_msg[2],))
                        __main__.db.commit()

                        upd_users = __main__.db.cursor()
                        upd_users.execute("SELECT * FROM users WHERE server_id=?",(use_server_id,))
                        for row in upd_users:
                            use_profile = await __main__.decrypt_data(row['profile'])
                            if(use_profile != False and use_profile != None and use_profile != ""):
                                new_profile = json.loads(use_profile)
                                if(proc_msg[2] in new_profile):
                                    del new_profile[proc_msg[2]]
                                    new_profile = await __main__.encrypt_data(json.dumps(new_profile))
                                    save_user = __main__.db.cursor()
                                    save_user.execute("UPDATE users SET profile=? WHERE user_id=? AND server_id=?",(new_profile,row['user_id'],use_server_id,))
                                    __main__.db.commit()

                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have deleted the field "'+get_field_name+'" from all profiles.')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a field with ID "'+str(proc_msg[2])+'".')

                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the ID number of the field you want to remove.')



        if(proc_msg[1] == "set"):
            load_profile = False
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'profile','view_profiles',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,2)
                proc_msg_length = len(proc_msg)
                if(proc_msg_length >= 3):

                    get_list = __main__.db.cursor()
                    get_list.execute("SELECT * FROM profile_fields WHERE server_id=?",(use_server_id,))
                    get_list_count = 0
                    get_field_name = ''
                    get_field_id = ''
                    for row in get_list:
                        chk_field_name = await __main__.decrypt_data(row['field_name'])
                        if(chk_field_name.lower() == proc_msg[2].lower()):
                            get_list_count = get_list_count + 1
                            get_field_name = chk_field_name
                            get_field_id = str(row['id'])

                    if(get_list_count == 1):
                        use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)

                        upd_users = __main__.db.cursor()
                        upd_users.execute("SELECT * FROM users WHERE server_id=? AND user_id=?",(use_server_id,use_member_id,))
                        for row in upd_users:
                            use_profile = await __main__.decrypt_data(row['profile'])
                            if(use_profile == False or use_profile == None or use_profile == ""):
                                new_profile = {}
                            else: new_profile = json.loads(use_profile)

                            if(get_field_id not in new_profile):
                                await __main__.client.send_message(message.author,'The value of your '+get_field_name+' field is currently not set.')
                            else:
                                await __main__.client.send_message(message.author,'The value of your '+get_field_name+' field is currently set to:')
                                await __main__.client.send_message(message.author,str(new_profile[get_field_id]))

                            await __main__.client.send_message(message.author,'**I will update it to match the contents of the next message you send me. Otherwise you can send me a message saying "clear" to empty this field, or "cancel" to keep it as it is. I am now listening for your response.**')


                            update_field_opt = await __main__.client.wait_for_message(author=message.author,channel=message.channel)
                            if(update_field_opt.content.lower() != "cancel"):

                                if(update_field_opt.content.lower() == "clear"):
                                    del new_profile[get_field_id]
                                else: new_profile[get_field_id] = update_field_opt.content
                                new_profile = await __main__.encrypt_data(json.dumps(new_profile))

                                save_user = __main__.db.cursor()
                                save_user.execute("UPDATE users SET profile=? WHERE user_id=? AND server_id=?",(new_profile,use_member_id,use_server_id,))
                                __main__.db.commit()

                                await __main__.client.send_message(message.author,'Okay <@'+message.author.id+'>, I have updated your profile field "'+get_field_name+'"')

                            else: await __main__.client.send_message(message.author,'Okay <@'+message.author.id+'>, I have cancelled updating that field.')

                    else: await __main__.client.send_message(message.author,'Sorry <@'+message.author.id+'>, I couldn\'t find a field called "'+str(proc_msg[2])+'".')

                else: await __main__.client.send_message(message.author,'Sorry <@'+message.author.id+'>, you must specify the name of the profile field you want to change.')



        if(proc_msg[1] == "search"):
            load_profile = False
            chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'profile','view_profiles',True)
            if(chk_user_perm == True):
                proc_msg = await __main__.get_cmd_args(message.content,2)
                proc_msg_length = len(proc_msg)
                if(proc_msg_length >= 3):
                    if(proc_msg[2].lower().startswith('page ')):
                        if(message.server.id in last_search_crit and message.author.id in last_search_crit[message.server.id]):
                            use_search_crit = last_search_crit[message.server.id][message.author.id]
                            fail_search_crit = []
                            use_page = proc_msg[2].split(" ")
                            if(len(use_page) == 2):
                                use_page = int(use_page[1])
                            else: await __main__.client.send_message(message.author,'Sorry <@'+message.author.id+'>, you must specify a page number to view.')
                        else: await __main__.client.send_message(message.author,'Sorry <@'+message.author.id+'>, you must search for something before you can switch between result pages.')
                    else:
                        use_page = 1

                        search_crit = proc_msg[2].replace(", ",",")
                        search_crit = search_crit.replace(" ,",",")
                        search_crit = search_crit.split(",")

                        use_search_crit = []
                        fail_search_crit = []
                        for crit in search_crit:
                            use_crit = '[#^#]'+crit
                            use_crit = use_crit.replace("[#^#]+","")
                            use_crit = use_crit.replace("[#^#]-","")
                            use_crit = use_crit.replace("[#^#]","")

                            found_role_id = await __main__.find_role_arg(message.server,use_crit)
                            if(found_role_id != False):
                                add_crit = {}
                                add_crit['id'] = found_role_id
                                if(crit.startswith('-')):
                                    add_crit['mode'] = '-'
                                else: add_crit['mode'] = '+'
                                use_search_crit.append(add_crit)
                            else: fail_search_crit.append(use_crit)

                    if(len(use_search_crit) > 0):
                        found_profiles_count = 0
                        found_profiles = []
                        for this_mem in message.server.members:
                            if(str(this_mem.status) == "online" or str(this_mem.status) == "idle" or str(this_mem.status) == "busy" or str(this_mem.status) == "dnd"):
                                is_match = True
                                for chk_crit in use_search_crit:
                                    has_role = False
                                    for this_role in this_mem.roles:
                                        if(this_role.id == chk_crit['id']): has_role = True
                                    if(has_role == True and chk_crit['mode'] == "-"): is_match = False
                                    if(has_role == False and chk_crit['mode'] == "+"): is_match = False

                                if(is_match == True):
                                    found_profiles_count = found_profiles_count + 1
                                    list_profile = {}
                                    list_profile['id'] = this_mem.id
                                    list_profile['status'] = str(this_mem.status)
                                    list_profile['nick'] = this_mem.display_name
                                    list_profile['username'] = this_mem.name+'#'+this_mem.discriminator
                                    found_profiles.append(list_profile)

                        if(found_profiles_count > 0):
                            real_page = use_page - 1
                            per_page = 20
                            run_index = real_page * per_page
                            max_pages = math.ceil((found_profiles_count / per_page))

                            if(message.server.id not in last_search_crit): last_search_crit[message.server.id] = {}
                            last_search_crit[message.server.id][message.author.id] = use_search_crit
                            last_index = found_profiles_count - 1

                            if(run_index <= last_index):

                                start_res = run_index + 1
                                end_res = start_res + (per_page - 1)
                                if(found_profiles_count < end_res): end_res = found_profiles_count
                                search_overview = 'Showing results '+str(start_res)+' to '+str(end_res)+' of '+str(found_profiles_count)+'.'
                                if(max_pages > 1):
                                    search_overview = search_overview+'\n\n**Page '+str(use_page)+' of '+str(max_pages)+'**'
                                    search_overview = search_overview+'\nTo view another page of these results, run `'+bot_cmd_char+'profile search page PAGE-NUMBER`.'

                                failed_crit_list = ''
                                for failed_crit in fail_search_crit:
                                    if(failed_crit_list != ""): failed_crit_list = failed_crit_list+', '
                                    failed_crit_list = failed_crit_list+'"'+failed_crit+'"'
                                if(failed_crit_list != ""):
                                    search_overview = search_overview+'\n\n**However I left out the following criteria because I did not understand:**\n'+failed_crit_list

                                icon_url = __main__.client.user.avatar_url
                                if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url
                                em = __main__.discord.Embed(title='Profile search results', description=search_overview, colour=3447003)
                                em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)

                                built_profiles = 0
                                while(built_profiles < per_page and run_index <= (found_profiles_count - 1)):
                                    found_nick = found_profiles[run_index]['nick']
                                    found_status = found_profiles[run_index]['status']
                                    found_username = found_profiles[run_index]['username']
                                    list_details = '**Status:** '+found_status.capitalize()
                                    list_details = list_details+'\nTo view this profile run `'+bot_cmd_char+'profile '+found_username+'`'
                                    em.add_field(name=found_nick+' ('+found_username+')',value=list_details,inline=False)
                                    built_profiles = built_profiles + 1
                                    run_index = run_index + 1

                                await __main__.client.send_message(message.author,embed=em)

                            else: await __main__.client.send_message(message.author,'Sorry <@'+message.author.id+'>, there is no page "'+str(use_page)+'" to view.')
                        else: await __main__.client.send_message(message.author,'Sorry <@'+message.author.id+'>, I couldn\'t find any members matching that criteria.')
                    else: await __main__.client.send_message(message.author,'Sorry <@'+message.author.id+'>, I did understand any of the tags you entered, please try again.')
                else: await __main__.client.send_message(message.author,'Sorry <@'+message.author.id+'>, you must specify some tags you want to search profiles for.')




        if(load_profile == True):
            proc_msg = await __main__.get_cmd_args(message.content,1)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length == 1):
                proc_msg[1] = '<@'+message.author.id+'>'
                proc_msg_length = 2

            found_user = await __main__.find_user(message.server,proc_msg[1],True)
            if(found_user != False):
                await view_profile(message.server,found_user,message.author)
                await __main__.client.delete_message(message)
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user with that name.')



async def view_profile(server_obj=None,interact_user=None,post_to=None):
    if(interact_user != None and post_to != None):
        bot_cmd_char = await __main__.get_cmd_char(server_obj)
        use_server_id = await __main__.hash_server_id(server_obj.id)
        use_member_id = await __main__.hash_member_id(server_obj.id,interact_user.id)

        icon_url = interact_user.avatar_url
        if(icon_url == None or icon_url == ""): icon_url = interact_user.default_avatar_url

        user_status = 'offline'
        if(str(interact_user.status) == "online"): user_status = 'online'
        if(str(interact_user.status) == "dnd"): user_status = 'busy'
        if(str(interact_user.status) == "idle"): user_status = 'idle'
        if(str(interact_user.game) != "None"): user_status = user_status+', playing '+str(interact_user.game)
        user_status = 'Currently '+user_status

        user_creds = __main__.db.cursor()
        user_creds.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
        found_balance = 0
        for row in user_creds:
            if(row['xp'] != None and row['xp'] != ""):
                dec_balance = await __main__.decrypt_data(row['xp'])
                if(dec_balance != False): found_balance = int(dec_balance)
        user_level = await xp_to_level(found_balance)
        user_status = '**Level '+str(user_level)+'** ('+str(found_balance)+'XP)\n'+user_status

        em = __main__.discord.Embed(title=interact_user.display_name+'\'s profile', description=user_status, colour=3447003)
        em.set_author(name=interact_user.display_name, icon_url=icon_url)
        em.set_thumbnail(url=icon_url)

        mem_roles = ''
        for role in interact_user.roles:
            if(mem_roles != ""): mem_roles = mem_roles+', '
            if(str(role) != "@everyone"):
                mem_roles = mem_roles+str(role)


        em.add_field(name="Joined Discord",value=interact_user.created_at.strftime("%a %d %b %Y %H:%M UTC 0"),inline=True)
        em.add_field(name="Joined server",value=interact_user.joined_at.strftime("%a %d %b %Y %H:%M UTC 0"),inline=True)

        if(interact_user.id == post_to.id): mem_roles = mem_roles+'\n\nTo change this field run`'+bot_cmd_char+'role list`.'
        if(mem_roles != ""): em.add_field(name="Roles",value=mem_roles,inline=False)

        user_data = __main__.db.cursor()
        user_data.execute("SELECT * FROM users WHERE server_id=? AND user_id=?",(use_server_id,use_member_id,))
        user_profile_data = {}
        for row in user_data:
            use_profile = await __main__.decrypt_data(row['profile'])
            if(use_profile != False and use_profile != None and use_profile != ""): user_profile_data = json.loads(use_profile)


        get_list = __main__.db.cursor()
        get_list.execute("SELECT * FROM profile_fields WHERE server_id=? ORDER BY id ASC",(use_server_id,))
        for row in get_list:
            if(str(row['id']) in user_profile_data):
                use_field_val = user_profile_data[str(row['id'])]
            else: use_field_val = ''

            if(use_field_val != "" or interact_user.id == post_to.id):
                use_field_name = await __main__.decrypt_data(row['field_name'])
                if(interact_user.id == post_to.id):
                    if(use_field_val == ""): use_field_val = 'Not set'
                    use_field_val = use_field_val+'\n\nTo change this field run `'+bot_cmd_char+'profile set '+use_field_name+'`.'

                em.add_field(name=use_field_name,value=use_field_val,inline=False)

        return await __main__.client.send_message(post_to,embed=em)


async def message_new(message):
    if(message.channel.is_private == False and message.author.id != __main__.client.user.id and message.author.bot == False):
        await earn_xp(message.author,message.server)

async def message_edit(before,after): pass

async def message_delete(message): pass

async def message_typing(channel,user,datestamp): pass

#===================================================================================================================
#MESSAGE REACTION EVENTS

async def reaction_add(reaction,user):
    if(reaction.message.channel.is_private == False and user.id != __main__.client.user.id and user.bot == False):
        await earn_xp(user,reaction.message.server)

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
