#!/usr/bin/python

import __main__

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Purge messages'
    help_info['description'] = 'Delete messages in bulk from public channels.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'purge'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = 'type number'
    help_entry['description'] = 'Bulk deletes the latest messages from a public channel. Type can be either a users name or "all", number must be between 1 and 100.'
    help_entry['perm_name'] = 'del_messages'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'del_messages'
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

purge_data = {}

def purge_user_check(message):
    if(message.author.id == purge_data[message.server.id]['user'].id):
        if(purge_data[message.server.id]['del_count'] < purge_data[message.server.id]['amount']):
            purge_data[message.server.id]['del_count'] = purge_data[message.server.id]['del_count'] + 1
            return True
        else: return False
    else: return False


async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)
    if(message.content.startswith(bot_cmd_char+'purge')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'purge','del_messages',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 3):
                del_amount = int(proc_msg[2])
                if(del_amount <= 100 and del_amount > 0):

                    if(proc_msg[1] == "all"):
                        #delete all messages
                        await __main__.client.delete_message(message)
                        await __main__.client.purge_from(message.channel,limit=del_amount)
                    else:
                        #delete messages by a specific user
                        this_user = await __main__.find_user(message.server,proc_msg[1],True)
                        if(this_user != False):

                            if(message.server.id not in purge_data): purge_data[message.server.id] = {}
                            if('amount' not in purge_data[message.server.id]): purge_data[message.server.id]['amount'] = 0

                            if(purge_data[message.server.id]['amount'] == 0):
                                await __main__.client.delete_message(message)
                                purge_data[message.server.id]['user'] = this_user
                                purge_data[message.server.id]['amount'] = del_amount
                                purge_data[message.server.id]['del_count'] = 0
                                await __main__.client.purge_from(message.channel,limit=1000,check=purge_user_check)
                                del purge_data[message.server.id]
                            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I\'m busy doing another purge user command at the moment. Please try again in a few moments.')
                        else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user called "'+proc_msg[1]+'".')
                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, the amount of messages to delete must be between 1 and 100.')
            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify either "all" messages or a specific user, and the number of messages to remove.')

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
