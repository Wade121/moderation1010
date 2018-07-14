#!/usr/bin/python

import __main__
import json

#===================================================================================================================
#PLUGIN CALLS

async def help_menu():
    help_info = {}
    help_info['title'] = 'Message log'
    help_info['description'] = 'Search logged messages.'
    return help_info


async def help_section():
    help_info = {}

    cmd_name = 'log'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'deleted_by'
    help_entry['args'] = '@someuser'
    help_entry['description'] = 'Show all messages deleted or edited recently by @someuser.'
    help_entry['perm_name'] = 'read_deleted'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'deleted_in'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Show all messages deleted or edited recently in channel_name.'
    help_entry['perm_name'] = 'read_deleted'
    help_info[cmd_name].append(help_entry)

    return help_info


async def plugin_permissions():
    perm_info = {}

    this_perm = 'read_deleted'
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

async def message_process(message):
    bot_cmd_char = await __main__.get_cmd_char(message.server)
    if(message.content.startswith(bot_cmd_char+'log')):
        chk_user_perm = await __main__.has_perm_to_run(message.server,message,message.author.id,'msglog','read_deleted',True)
        if(chk_user_perm == True):
            proc_msg = await __main__.get_cmd_args(message.content)
            proc_msg_length = len(proc_msg)

            use_server_id = await __main__.hash_server_id(message.server.id)
            found_messages = False

            if(proc_msg[1] == "deleted_in"):
                #list users who have deleted messages in this channel, how many and when the latest was
                check_channel = await __main__.find_channel_arg(message.server,proc_msg[2],True)
                if(check_channel != False):
                    use_channel_id = await __main__.hash_member_id(message.server.id,check_channel.id)
                    found_messages = []
                    get_msg = __main__.db.cursor()
                    get_msg.execute("SELECT * FROM deleted_msgs WHERE server_id=? AND channel_id=? ORDER BY del_date DESC LIMIT 23",(use_server_id,use_channel_id,))
                    for row in get_msg:
                        new_record = {}
                        new_record['channel_id'] = await __main__.decrypt_data(row['stored_channel_id'])
                        new_record['user_id'] = await __main__.decrypt_data(row['stored_user_id'])
                        new_record['del_date'] = row['del_date']
                        new_record['msg_date'] = row['msg_date']
                        new_record['msg_content'] = await __main__.decrypt_data(row['msg_content'])
                        new_record['msg_embeds'] = await __main__.decrypt_data(row['msg_embeds'])
                        new_record['new_content'] = await __main__.decrypt_data(row['new_content'])
                        new_record['new_embeds'] = await __main__.decrypt_data(row['new_embeds'])
                        found_messages.append(new_record)

                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel with that name. Please try again.')

            if(proc_msg[1] == "deleted_by"):
                #list messages deleted by this user in each channel
                check_user = await __main__.find_user(message.server,proc_msg[2],True)
                if(check_user != False):
                    use_member_id = await __main__.hash_member_id(message.server.id,check_user.id)
                    found_messages = []
                    get_msg = __main__.db.cursor()
                    get_msg.execute("SELECT * FROM deleted_msgs WHERE server_id=? AND user_id=? ORDER BY del_date DESC LIMIT 23",(use_server_id,use_member_id,))
                    for row in get_msg:
                        new_record = {}
                        new_record['channel_id'] = await __main__.decrypt_data(row['stored_channel_id'])
                        new_record['user_id'] = await __main__.decrypt_data(row['stored_user_id'])
                        new_record['del_date'] = row['del_date']
                        new_record['msg_date'] = row['msg_date']
                        new_record['msg_content'] = await __main__.decrypt_data(row['msg_content'])
                        new_record['msg_embeds'] = await __main__.decrypt_data(row['msg_embeds'])
                        new_record['new_content'] = await __main__.decrypt_data(row['new_content'])
                        new_record['new_embeds'] = await __main__.decrypt_data(row['new_embeds'])
                        found_messages.append(new_record)

                else: await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a member with that name. Please try again.')

            if(found_messages != False and len(found_messages) > 0):

                icon_url = __main__.client.user.avatar_url
                if(icon_url == None or icon_url == ""): icon_url = __main__.client.user.default_avatar_url
                repost_title = 'Deleted/edited message log results'

                em = __main__.discord.Embed(title=repost_title, description='Here are the logs of deleted or edited messages which were found:', colour=3447003)
                em.set_author(name=__main__.client.user.id, icon_url=icon_url)

                field_count = 0
                for del_msg in found_messages:
                    use_author = await __main__.find_user(message.server,'<@'+del_msg['user_id']+'>',True)
                    use_channel = await __main__.find_channel_arg(message.server,'<#'+del_msg['channel_id']+'>',True)
                    if(use_author != False and use_channel != False):
                        use_date = await __main__.timestamp_to_date_short(del_msg['del_date'])
                        use_name = use_author.display_name+' ('+use_author.name+'#'+use_author.discriminator+') deleted in #'+use_channel.name+' at '+str(use_date)
                        use_content = del_msg['msg_content']
                        em.add_field(name=use_name,value=use_content,inline=False)
                        field_count = field_count + 1
                
                await __main__.client.send_message(message.channel, embed=em)

            elif(found_messages != False):
                await __main__.client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find any deleted or edited message records to display.')



async def message_new(message): pass

async def message_edit(before,after):
    use_server_id = await __main__.hash_server_id(before.server.id)
    use_channel_id = await __main__.hash_member_id(before.server.id,before.channel.id)
    save_channel_id = await __main__.encrypt_data(before.channel.id)
    use_member_id = await __main__.hash_member_id(before.server.id,before.author.id)
    save_member_id = await __main__.encrypt_data(before.author.id)

    del_date = await __main__.current_timestamp()
    msg_time = before.timestamp.timestamp()

    save_msg_content = await __main__.encrypt_data(before.content)
    save_msg_embeds = await __main__.encrypt_data(json.dumps(before.attachments))

    save_new_content = await __main__.encrypt_data(after.content)
    save_new_embeds = await __main__.encrypt_data(json.dumps(after.attachments))

    save_dm = __main__.db.cursor()
    save_dm.execute("INSERT INTO deleted_msgs (server_id,channel_id,stored_channel_id,user_id,stored_user_id,del_date,msg_date,msg_content,msg_embeds,new_content,new_embeds) VALUES (?,?,?,?,?,?,?,?,?,?,?)",(use_server_id,use_channel_id,save_channel_id,use_member_id,save_member_id,del_date,msg_time,save_msg_content,save_msg_embeds,save_new_content,save_new_embeds,))
    __main__.db.commit()


async def message_delete(message):
    use_server_id = await __main__.hash_server_id(message.server.id)
    use_channel_id = await __main__.hash_member_id(message.server.id,message.channel.id)
    save_channel_id = await __main__.encrypt_data(message.channel.id)
    use_member_id = await __main__.hash_member_id(message.server.id,message.author.id)
    save_member_id = await __main__.encrypt_data(message.author.id)

    del_date = await __main__.current_timestamp()
    msg_time = message.timestamp.timestamp()

    save_msg_content = await __main__.encrypt_data(message.content)
    save_msg_embeds = await __main__.encrypt_data(json.dumps(message.attachments))

    save_dm = __main__.db.cursor()
    save_dm.execute("INSERT INTO deleted_msgs (server_id,channel_id,stored_channel_id,user_id,stored_user_id,del_date,msg_date,msg_content,msg_embeds) VALUES (?,?,?,?,?,?,?,?,?)",(use_server_id,use_channel_id,save_channel_id,use_member_id,save_member_id,del_date,msg_time,save_msg_content,save_msg_embeds,))
    __main__.db.commit()

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
