#!/usr/bin/python

import __main__

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Polls and votes'
    help_info['description'] = 'Cast your vote on polls.'
    return help_info


async def help_section():
    help_info = {}

    
    cmd_name = 'poll'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'add'
    help_entry['args'] = 'question, answer 1, answer 2, answer 3...'
    help_entry['description'] = 'Create a new poll'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'remove'
    help_entry['args'] = 'poll_id'
    help_entry['description'] = 'Delete poll_id and all associated data'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'open'
    help_entry['args'] = 'poll_id'
    help_entry['description'] = 'Open poll_id for voting.'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'close'
    help_entry['args'] = 'poll_id'
    help_entry['description'] = 'Close poll_id for voting.'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'list'
    help_entry['args'] = ''
    help_entry['description'] = 'List all the polls on this server.'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'view'
    help_entry['args'] = 'poll_id'
    help_entry['description'] = 'View a poll and its current results.'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'post'
    help_entry['args'] = 'poll_id'
    help_entry['description'] = 'Post a poll into a public channel, if the poll is open it will show how to vote, if the poll is closed it will show the results.'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'edit_question'
    help_entry['args'] = 'poll_id new_question'
    help_entry['description'] = 'Changes poll_id\'s question to new_question.'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'edit_option'
    help_entry['args'] = 'poll_id option_num new_option'
    help_entry['description'] = 'Changes option_num on poll_id to new_option.'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add_option'
    help_entry['args'] = 'poll_id new_option'
    help_entry['description'] = 'Adds new_option to poll_id.'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'del_option'
    help_entry['args'] = 'poll_id option_num'
    help_entry['description'] = 'Deletes option_num from poll_id.'
    help_entry['perm_name'] = 'manage_polls'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'vote'
    help_entry['args'] = 'poll_id'
    help_entry['description'] = 'View the poll with id poll_id and cast your vote.'
    help_entry['perm_name'] = 'vote_in_polls'
    help_info[cmd_name].append(help_entry)
    

    return help_info


async def plugin_permissions():
    perm_info = {}
    
    this_perm = 'manage_polls'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')
    
    this_perm = 'vote_in_polls'
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
    if(message.content.startswith(bot_cmd_char+'poll')):
        proc_msg = await __main__.get_cmd_args(message.content,3)
        proc_msg_length = len(proc_msg)
        if(proc_msg_length >= 2):

            if(proc_msg[1] == "add"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    proc_msg = await __main__.get_cmd_args(message.content,2)
                    option_list = proc_msg[2]
                    option_list = option_list.replace(', ',',')
                    option_list = option_list.split(',')
                    option_list_length = len(option_list)
                    if(option_list_length >= 3):

                        use_server_id = await __main__.hash_server_id(message.server.id)
                        save_question = await __main__.encrypt_data(option_list[0])

                        new_poll = __main__.db.cursor()
                        new_poll.execute("INSERT INTO polls (active,question,server_id) VALUES (1,?,?)",(save_question,use_server_id,))
                        __main__.db.commit()
                        new_poll_id = new_poll.lastrowid

                        option_list_length = option_list_length - 1
                        ol_run = 1
                        while(ol_run <= option_list_length):
                            save_option = await __main__.encrypt_data(option_list[ol_run])
                            add_option = __main__.db.cursor()
                            add_option.execute("INSERT INTO polls_options (poll_id,option,server_id) VALUES (?,?,?)",(new_poll_id,save_option,use_server_id,))
                            __main__.db.commit()
                            ol_run = ol_run + 1

                        await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve created a new poll with ID '+str(new_poll_id)+'. You can view it by running the command `'+bot_cmd_char+'poll view '+str(new_poll_id)+'`')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must enter a question and at least two options to choose from. Otherwise it\'s not really a choice is it?')


            if(proc_msg[1] == "remove"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    if(proc_msg_length >= 3):
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        find_poll = __main__.db.cursor()
                        find_poll.execute("SELECT * FROM polls WHERE id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                        find_poll_length = 0
                        for row in find_poll:
                            find_poll_length = find_poll_length + 1

                        if(find_poll_length == 1):
                            del_opts = __main__.db.cursor()
                            del_opts.execute("DELETE FROM polls_options WHERE poll_id=? AND server_id=?",(proc_msg[2],use_server_id,))
                            __main__.db.commit()

                            del_votes = __main__.db.cursor()
                            del_votes.execute("DELETE FROM polls_votes WHERE poll_id=? AND server_id=?",(proc_msg[2],use_server_id,))
                            __main__.db.commit()

                            del_poll = __main__.db.cursor()
                            del_poll.execute("DELETE FROM polls WHERE id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                            __main__.db.commit()

                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve removed that poll from the database for you.')

                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a poll with the ID "'+str(proc_msg[2])+'"')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the ID of the poll you want me to remove.')


            if(proc_msg[1] == "open"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    if(proc_msg_length >= 3):
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        find_poll = __main__.db.cursor()
                        find_poll.execute("SELECT * FROM polls WHERE id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                        find_poll_length = 0
                        poll_open = 0
                        for row in find_poll:
                            find_poll_length = find_poll_length + 1
                            poll_open = int(row['active'])

                        if(find_poll_length == 1):
                            if(poll_open == 0):
                                upd_opts = __main__.db.cursor()
                                upd_opts.execute("UPDATE polls SET active='1' WHERE id=? AND server_id=?",(proc_msg[2],use_server_id,))
                                __main__.db.commit()
                                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve opened voting for that poll.')
                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that poll is already open for voting.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a poll with the ID "'+str(proc_msg[2])+'"')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the ID of a poll you want me to open.')
                    

            if(proc_msg[1] == "close"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    if(proc_msg_length >= 3):
                        use_server_id = await __main__.hash_server_id(message.server.id)
                        find_poll = __main__.db.cursor()
                        find_poll.execute("SELECT * FROM polls WHERE id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                        find_poll_length = 0
                        poll_open = 1
                        for row in find_poll:
                            find_poll_length = find_poll_length + 1
                            poll_open = int(row['active'])

                        if(find_poll_length == 1):
                            if(poll_open == 1):
                                upd_opts = __main__.db.cursor()
                                upd_opts.execute("UPDATE polls SET active='0' WHERE id=? AND server_id=?",(proc_msg[2],use_server_id,))
                                __main__.db.commit()
                                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve closed voting for that poll.')
                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that poll is already closed.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a poll with the ID "'+str(proc_msg[2])+'"')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the ID of a poll that you want me to close.')
                    

            if(proc_msg[1] == "list"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    use_server_id = await __main__.hash_server_id(message.server.id)
                    icon_url = __main__.client.user.avatar_url
                    if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url

                    get_polls = __main__.db.cursor()
                    get_polls.execute("SELECT * FROM polls WHERE server_id=? ORDER BY id ASC",(use_server_id,))
                    get_polls_count = 0
                    open_poll_count = 0
                    closed_poll_count = 0
                    for row in get_polls:
                        get_polls_count = get_polls_count + 1
                        if(int(row['active']) == 1):
                            open_poll_count = open_poll_count + 1
                        else: closed_poll_count = closed_poll_count + 1

                    if(get_polls_count > 0):
                        poll_list_descript = 'There are '+str(open_poll_count)+' open polls, and '+str(closed_poll_count)+' closed ones.\nType `'+bot_cmd_char+'poll view POLL-NUMBER` to view a poll.'
                    else: poll_list_descript = 'There are no polls to display at the moment.'

                    em = __main__.discord.Embed(title='Polls', description=poll_list_descript, colour=3447003)
                    em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)

                    if(get_polls_count > 0):
                        get_polls.execute("SELECT * FROM polls WHERE server_id=? ORDER BY active DESC, id DESC LIMIT 23",(use_server_id,))
                        for row in get_polls:
            
                            if(int(row['active']) == 1):
                                this_poll_descript = '**Status:** __Open for voting!__\n'
                            else: 
                                this_poll_descript = '**Status:** Closed\n'

                            vote_count = __main__.db.cursor()
                            vote_count.execute("SELECT * FROM polls_votes WHERE poll_id=? AND server_id=? AND valid='1'",(str(row['id']),use_server_id,))
                            vote_counter = 0
                            for vc in vote_count:
                                vote_counter = vote_counter + 1

                            this_poll_descript = this_poll_descript+'**Votes cast:** '+str(vote_counter)

                            show_question = await __main__.decrypt_data(row['question'])
                            em.add_field(name=str(row['id'])+' - '+show_question,value=this_poll_descript,inline=False)

                    await __main__.client.send_message(message.channel, embed=em)


            if(proc_msg[1] == "view" or proc_msg[1] == "post"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    use_server_id = await __main__.hash_server_id(message.server.id)
                    if(proc_msg_length >= 3):
                        find_poll = __main__.db.cursor()
                        find_poll.execute("SELECT * FROM polls WHERE id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                        find_poll_count = 0
                        for row in find_poll:
                            find_poll_count = find_poll_count + 1

                        if(find_poll_count == 1):
                            await poll_view(proc_msg[2],message,message.server,proc_msg[1])
                            if(proc_msg[1] == "post"): await __main__.client.delete_message(message)
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a poll with ID "'+proc_msg[2]+'"')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a poll number to view.')


            if(proc_msg[1] == "edit_question"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    use_server_id = await __main__.hash_server_id(message.server.id)
                    if(proc_msg_length >= 4):
                        new_question = proc_msg[3]
                        save_new_question = await __main__.encrypt_data(new_question)
                        find_poll = __main__.db.cursor()
                        find_poll.execute("SELECT * FROM polls WHERE id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                        find_poll_count = 0
                        for row in find_poll:
                            find_poll_count = find_poll_count + 1

                        if(find_poll_count == 1):
                            edit_poll = __main__.db.cursor()
                            edit_poll.execute("UPDATE polls SET question=? WHERE id=? AND server_id=?",(save_new_question,int(proc_msg[2]),use_server_id,))
                            __main__.db.commit()
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve changed that polls question to say "'+new_question+'"')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a poll with ID "'+proc_msg[2]+'"')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a poll number to edit.')


            if(proc_msg[1] == "edit_option"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    use_server_id = await __main__.hash_server_id(message.server.id)
                    proc_msg = await __main__.get_cmd_args(message.content,4)
                    proc_msg_length = len(proc_msg)
                    if(proc_msg_length >= 4):
                        new_option = proc_msg[4]
                        save_new_option = await __main__.encrypt_data(new_option)
                        find_poll = __main__.db.cursor()
                        find_poll.execute("SELECT * FROM polls WHERE id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                        find_poll_count = 0
                        for row in find_poll:
                            find_poll_count = find_poll_count + 1

                        if(find_poll_count == 1):
                            find_option = __main__.db.cursor()
                            find_option.execute("SELECT * FROM polls_options WHERE poll_id=? AND server_id=? ORDER BY id ASC",(proc_msg[2],use_server_id,))
                            find_option_id = ''
                            find_option_count = 0
                            for opt in find_option:
                                find_option_count = find_option_count + 1
                                if(find_option_count == int(proc_msg[3])): find_option_id = opt['id']

                            if(find_option_id != ''):

                                edit_poll = __main__.db.cursor()
                                edit_poll.execute("UPDATE polls_options SET option=? WHERE id=? AND server_id=?",(save_new_option,find_option_id,use_server_id,))
                                __main__.db.commit()
                                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve changed that option to say "'+new_option+'"')
                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find option number "'+proc_msg[3]+'"')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a poll with ID "'+proc_msg[2]+'"')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a poll number and an option number to edit.')


            if(proc_msg[1] == "del_option"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    use_server_id = await __main__.hash_server_id(message.server.id)
                    if(proc_msg_length >= 4):
                        find_poll = __main__.db.cursor()
                        find_poll.execute("SELECT * FROM polls WHERE id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                        find_poll_count = 0
                        for row in find_poll:
                            find_poll_count = find_poll_count + 1

                        if(find_poll_count == 1):
                            find_option = __main__.db.cursor()
                            find_option.execute("SELECT * FROM polls_options WHERE poll_id=? AND server_id=? ORDER BY id ASC",(proc_msg[2],use_server_id,))
                            find_option_id = ''
                            find_option_count = 0
                            for opt in find_option:
                                find_option_count = find_option_count + 1
                                if(find_option_count == int(proc_msg[3])): find_option_id = opt['id']

                            if(find_option_id != ''):
                                edit_poll = __main__.db.cursor()
                                edit_poll.execute("DELETE FROM polls_options WHERE id=? AND server_id=?",(find_option_id,use_server_id,))
                                __main__.db.commit()
                                del_votes = __main__.db.cursor()
                                del_votes.execute("DELETE FROM polls_votes WHERE option_id=? AND server_id=?",(find_option_id,use_server_id,))
                                __main__.db.commit()
                                await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve removed that option from the poll.')
                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find option number "'+proc_msg[3]+'"')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a poll with ID "'+proc_msg[2]+'"')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a poll number and an option number to remove.')


            if(proc_msg[1] == "add_option"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','manage_polls',True)
                if(chk_user_perm == True):
                    use_server_id = await __main__.hash_server_id(message.server.id)
                    if(proc_msg_length >= 3):
                        new_option = proc_msg[3]
                        save_new_option = await __main__.encrypt_data(new_option)
                        find_poll = __main__.db.cursor()
                        find_poll.execute("SELECT * FROM polls WHERE id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                        find_poll_count = 0
                        for row in find_poll:
                            find_poll_count = find_poll_count + 1

                        if(find_poll_count == 1):
                            edit_poll = __main__.db.cursor()
                            edit_poll.execute("INSERT INTO polls_options (poll_id,option,server_id) VALUES (?,?,?)",(proc_msg[2],save_new_option,use_server_id,))
                            __main__.db.commit()
                            await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, I\'ve added "'+new_option+'" to that poll as an option.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a poll with ID "'+proc_msg[2]+'"')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a poll number to add an option to.')


            if(proc_msg[1] == "vote"):
                chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'poll','vote_in_polls',True)
                if(chk_user_perm == True):
                    use_server_id = await __main__.hash_server_id(message.server.id)
                    use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)
                
                    #poll_vote_restrict = await get_config('poll_vote_restrict',message.server)
                    '''
                    poll_vote_restrict = 1209600
                    if(poll_vote_restrict != False and str(poll_vote_restrict) != "0"):
                        vote_allowed = False
                        user_joined = message.author.joined_at.timestamp()
                        time_now = await current_timestamp()
                        delay_time = int(poll_vote_restrict)
                        user_joined = user_joined + delay_time
                        if(delay_time <= time_now): vote_allowed = True
                    else: vote_allowed = True
                    '''
                    
                    vote_valid = '5' #member left server before poll closed
                    vote_valid = '4' #member level too low, not activate enough
                    vote_valid = '3' #not a member for long enough
                    vote_valid = '2' #alt account
                    vote_valid = '1'


                    if(proc_msg_length >= 3):
                        find_poll = __main__.db.cursor()
                        find_poll.execute("SELECT * FROM polls WHERE active='1' AND id=? AND server_id=?",(int(proc_msg[2]),use_server_id,))
                        find_poll_count = 0
                        for row in find_poll:
                            find_poll_count = find_poll_count + 1

                        if(find_poll_count == 1):
                            await poll_view(proc_msg[2],message,message.server,'vote')
                    
                            vote_msg = await __main__.client.send_message(message.author,'Please send me a message with either the number of the option you want to vote for, or say "cancel".')
                            conf_msg = await __main__.client.wait_for_message(author=message.author,channel=vote_msg.channel)
                            conf_msg = conf_msg.content.lower()

                            if(conf_msg != "cancel"):
                                conf_msg = conf_msg.replace("option ","")
                                                                                   
                                find_option = __main__.db.cursor()
                                find_option.execute("SELECT * FROM polls_options WHERE poll_id=? AND server_id=?",(proc_msg[2],use_server_id,))
                                found_option_id = ''
                                found_option_text = ''
                                find_option_count = 0
                                for opt in find_option:
                                    find_option_count = find_option_count + 1
                                    if(find_option_count == int(conf_msg)):
                                        found_option_id = opt['id']
                                        found_option_txt = await __main__.decrypt_data(opt['option'])

                                if(found_option_id == ""):
                                    await client.send_message(message.author,'Sorry <@'+message.author.id+'>, I couldn\'t find an option with the number "'+conf_msg+'".')
                                else:
                                    check_previous = __main__.db.cursor()
                                    check_previous.execute("DELETE FROM polls_votes WHERE poll_id=? AND user_id=? AND server_id=?",(proc_msg[2],use_member_id,use_server_id,))
                                    __main__.db.commit()

                                    cast_vote = __main__.db.cursor()
                                    cast_vote.execute("INSERT INTO polls_votes (poll_id,user_id,option_id,server_id,valid) VALUES (?,?,?,?,?)",(proc_msg[2],use_member_id,found_option_id,use_server_id,vote_valid,))
                                    __main__.db.commit()

                                    await __main__.client.send_message(message.author,'Okay <@'+message.author.id+'>, your vote has been cast. You voted for "'+found_option_txt+'"')
                            

                            else: await __main__.client.send_message(message.channel,'Okay <@'+message.author.id+'>, cancelled voting.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find an open poll with ID "'+proc_msg[2]+'"')
                    else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a poll number and an option number to vote for.')


async def poll_view(poll,message,server_obj,view_mode):
    #view_mode = vote/view/post
    poll = int(poll)
    use_server_id = await __main__.hash_server_id(message.server.id)
    use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)
    bot_cmd_char = await __main__.get_cmd_char(message.server)

    icon_url = __main__.client.user.avatar_url
    if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url

    get_poll = __main__.db.cursor()
    get_poll.execute("SELECT * FROM polls WHERE id=? AND server_id=?",(poll,use_server_id,))
    poll_question = ''
    poll_status = ''
    for row in get_poll:
        poll_question = await __main__.decrypt_data(row['question'])
        poll_status = int(row['active'])

    poll_descript = 'Status: '
    if(poll_status == 1):
        poll_descript = poll_descript+'__Open for voting!__'
    else: poll_descript = poll_descript+'Closed'

    if(view_mode == 'post' and poll_status == 1): poll_descript = 'To cast or change your vote run `'+bot_cmd_char+'poll vote '+str(poll)+'`\nYou will then be asked which option you want to vote for.'

    if(view_mode == 'view' or (view_mode == 'post' and poll_status == 0)):
        total_votes = __main__.db.cursor()
        total_votes.execute("SELECT * FROM polls_votes WHERE poll_id=? AND server_id=? AND valid='1'",(poll,use_server_id,))
        total_votes_count = 0
        for row in total_votes:
            total_votes_count = total_votes_count + 1
        
        poll_descript = poll_descript+'\nVotes cast: '+str(total_votes_count)


    if(view_mode == 'vote'):
        user_voted = __main__.db.cursor()
        user_voted.execute("SELECT * FROM polls_votes WHERE poll_id=? AND user_id=? AND server_id=?",(poll,use_member_id,use_server_id,))
        user_voted_for = ''
        for row in user_voted:
            user_voted_for = row['option_id']

        if(user_voted_for != ""):
            user_voted.execute("SELECT * FROM polls_options WHERE id=? AND server_id=?",(int(user_voted_for),use_server_id,))
            for row in user_voted:
                voted_option_text = await __main__.decrypt_data(row['option'])
                poll_descript = poll_descript+'\n**You voted for:** __'+voted_option_text+'__'
        else: poll_descript = poll_descript+'\n**You have not voted on this poll**'


    em = __main__.discord.Embed(title='__**'+poll_question+'**__', description=poll_descript, colour=3447003)
    em.set_author(name=__main__.client.user.display_name, icon_url=icon_url)
    
    vote_options = __main__.db.cursor()
    vote_options.execute("SELECT * FROM polls_options WHERE poll_id=? AND server_id=? ORDER BY id ASC",(poll,use_server_id,))
    vote_options_count = 0
    for row in vote_options:
        vote_options_count = vote_options_count + 1
        show_opt_text = await __main__.decrypt_data(row['option'])
        use_opt_title = show_opt_text
        
        if(view_mode == 'view' or (view_mode == 'post' and poll_status == 0)):
            opt_voted = __main__.db.cursor()
            opt_voted.execute("SELECT * FROM polls_votes WHERE poll_id=? AND option_id=? AND server_id=? AND valid='1'",(poll,row['id'],use_server_id,))
            opt_voted_count = 0
            for voted in opt_voted:
                opt_voted_count = opt_voted_count + 1

            if(total_votes_count > 0):
                opt_voted_perc = (opt_voted_count / total_votes_count) * 100
            else: opt_voted_perc = 0
            opt_voted_descript = str(opt_voted_count)+' votes / '+str(round(opt_voted_perc,2))+'%'
        else:
            use_opt_title = 'Option '+str(vote_options_count)
            opt_voted_descript = show_opt_text
        
        em.add_field(name=use_opt_title,value=opt_voted_descript,inline=False)

    if(view_mode == "vote"):
        await __main__.client.send_message(message.author, embed=em)
    else:
        await __main__.client.send_message(message.channel, embed=em)


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

async def role_delete(role): pass

async def role_update(before,after): pass

#===================================================================================================================
#EMOJI LIST EVENTS

async def emoji_list_update(before,after): pass

#===================================================================================================================
#GROUP CHAT EVENTS

async def group_join(channel,user): pass

async def group_remove(channel,user): pass
