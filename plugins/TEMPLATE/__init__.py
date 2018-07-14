#!/usr/bin/python

import __main__

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Title of help section'
    help_info['description'] = 'Brief description of what this module does.'
    return help_info


async def help_section():
    help_info = {}

    '''
    cmd_name = 'coin'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = ''
    help_entry['description'] = 'Flip a coin'
    help_entry['perm_name'] = ''
    help_info[cmd_name].append(help_entry)
    '''

    return help_info


async def plugin_permissions():
    perm_info = {}

    ''' 
    this_perm = 'manage_plugins'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')
    '''

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
    if(message.content.startswith(bot_cmd_char+'somecommand')):

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
