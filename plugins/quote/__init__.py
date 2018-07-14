#!/usr/bin/python

import __main__

global quote_reacted
quote_reacted = {}

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Quote messages'
    help_info['description'] = 'Quote other members messages in channel for replies.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'quote'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'id'
    help_entry['args'] = 'message_id'
    help_entry['description'] = 'Quote the message with ID number message_id.'
    help_entry['perm_name'] = 'quote_messages'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'text'
    help_entry['args'] = 'message_text'
    help_entry['description'] = 'Quote the message whose content contains or matches message_text.'
    help_entry['perm_name'] = 'quote_messages'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'reacted'
    help_entry['args'] = ''
    help_entry['description'] = 'Quote the message you last reacted to.'
    help_entry['perm_name'] = 'quote_messages'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'user'
    help_entry['args'] = '@someuser'
    help_entry['description'] = 'Quote the message last posted by @someuser.'
    help_entry['perm_name'] = 'quote_messages'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'quote_messages'
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
    if(message.content.startswith(bot_cmd_char+'quote')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'quote','quote_messages',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 2):
                found_message = False

                if(proc_msg[1] == "id"):
                    try:
                        msg_data = await __main__.client.get_message(message.channel,proc_msg[2])
                        found_message = True
                    except: found_message = False

                if(proc_msg[1] == "reacted"):
                    if(message.server.id in quote_reacted):
                        if(message.author.id in quote_reacted[message.server.id]):
                            try:
                                msg_data = quote_reacted[message.server.id][message.author.id]
                                found_message = True
                            except: found_message = False

                if(proc_msg[1] == "text"):
                    proc_msg = await __main__.get_cmd_args(message.content,2)
                    try:
                        async for log_msg in __main__.client.logs_from(message.channel, limit=250):
                            if(proc_msg[2].lower() in log_msg.content.lower() and log_msg.id != message.id):
                                msg_data = log_msg
                                found_message = True
                                break
                    except: found_message = False

                if(proc_msg[1] == "user"):
                    proc_msg = await __main__.get_cmd_args(message.content,2)
                    look_user = await __main__.find_user(message.server,proc_msg[2],True)
                    if(look_user != False):
                        try:
                            async for log_msg in __main__.client.logs_from(message.channel, limit=250):
                                if(look_user.id == log_msg.author.id and log_msg.id != message.id):
                                    msg_data = log_msg
                                    found_message = True
                                    break
                        except: found_message = False



                if(found_message != False):

                    icon_url = message.author.avatar_url
                    if(icon_url == None or icon_url == ""): icon_url = message.author.default_avatar_url

                    quote_icon = msg_data.author.avatar_url
                    if(quote_icon == None or quote_icon == ""): quote_icon = msg_data.author.default_avatar_url

                    em = __main__.discord.Embed(title='Quoted '+msg_data.author.display_name+' who said:', description=msg_data.content, colour=3447003)
                    em.set_author(name=message.author.display_name, icon_url=icon_url)
                    em.set_thumbnail(url=quote_icon)

                    msg_time = str(msg_data.timestamp).split(".")
                    msg_time = msg_time[0]
                    em.set_footer(text='#'+msg_data.channel.name+' ('+msg_time+')')

                    attach_length = len(msg_data.attachments)
                    if(attach_length > 0):
                        file_type = await __main__.attachment_file_type(msg_data.attachments[0])
                        if(file_type == "image"):
                            em.set_image(url=msg_data.attachments[0]['url'])

                    await __main__.client.send_message(message.channel, embed=em)
                    await __main__.client.delete_message(message)

                else:  await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a message matching that criteria to quote.')

            else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify how and what you want to quote.')

async def message_new(message): pass

async def message_edit(before,after): pass

async def message_delete(message): pass

async def message_typing(channel,user,datestamp): pass

#===================================================================================================================
#MESSAGE REACTION EVENTS

async def reaction_add(reaction,user):
    if(reaction.message.server.id not in quote_reacted): quote_reacted[reaction.message.server.id] = {}
    quote_reacted[reaction.message.server.id][user.id] = reaction.message

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
