#!/usr/bin/python

import discord
import asyncio
import sqlite3
import random
import datetime
import os
import json
import importlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib
import math

bot_version = '17.11'
verbose_out = True

#===================================================================================================================
#GLOBAL CONFIG

bot_token = 'NDY3NTA3NjA0OTQwMjU5MzMw.Dirsbg.GL_TZHKfsSW6NegFzUSeYrGuTuE'
bot_cmd_char = '/'
bot_playing_tag = ''
utc_time_modifier = 0
bot_pm_server_timeout = 15 #minutes to remember DM server pref for

bot_abs_path = os.path.dirname(os.path.abspath(__file__))+'/'

with open(bot_abs_path+"config.conf","r") as f:
    for line in f:
        use_line = line.rstrip('\r\n')
        line_break = use_line.split(" ")
        lb_length = len(line_break)

        if(line_break[0] == "bot_token" and lb_length == 2):
            if(line_break[1] != "bot-token-goes-here"):
                bot_token = line_break[1]

        if(line_break[0] == "bot_playing_tag" and lb_length >= 2):
            bot_playing_tag = use_line.replace(line_break[0]+' ','')

        if(line_break[0] == "bot_cmd_char" and lb_length == 2):
            bot_cmd_char = line_break[1]

        if(line_break[0] == "utc_time_modifier" and lb_length == 2):
            utc_time_modifier = int(line_break[1])


db_path = bot_abs_path+'bot.db'
db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row

client = discord.Client()

config = {}
tasklist = []
pm_servers = {}
global invite_list
invite_list = {}

startup_complete = False
enc_key = ''

#===================================================================================================================
#ENCRYPTION

def enc_load_key(enc_pass=None):
    if(enc_pass != None):
        enc_pass_b = bytes(enc_pass,'utf-8')
        salt_file = open(bot_abs_path+'salt','r')
        salt = bytes(salt_file.read(),'utf-8')
        salt_file.close()

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(enc_pass_b))

        global enc_key
        enc_key = Fernet(key)

        if(os.path.isfile(bot_abs_path+'pass_verif') == True):
            key_verified = False
            pass_verif_file = open(bot_abs_path+'pass_verif','r')
            pass_verif = pass_verif_file.read()
            pass_verif_file.close()
            chk_decrypt = decrypt_data_blocking(pass_verif)
            if(chk_decrypt != False): key_verified = True
        else: key_verified = True

        return key_verified
    else: return False


def enc_startup():
    enc_res = False

    if(os.path.isfile(bot_abs_path+'salt') == True and os.path.isfile(bot_abs_path+'pass_verif') == True):

        if(os.path.isfile(bot_abs_path+'master_pass') == True):
            #master pass is present
            print("Found master password file")
            master_pass = open(bot_abs_path+'master_pass','r')
            key_res = enc_load_key(master_pass.read())
            master_pass.close()
            if(key_res == True):
                enc_res = True
                print("Master password is correct")
            else: print("Master password is INCORRECT")
        else: print("ERROR: NO MASTER PASSWORD FILE PRESENT BUT IS EXPECTED.")

    else:
        #verification and salt files not present, new setup?
        print("No encryption files find, generating new set...")
        new_salt = os.urandom(16)
        new_salt_str = base64.b64encode(new_salt).decode('utf-8')
        new_pass = ''.join(random.SystemRandom().choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(64))

        master_pass = open(bot_abs_path+'master_pass','w')
        master_pass.write(new_pass)
        master_pass.close()

        salt_file = open(bot_abs_path+'salt','w')
        salt_file.write(new_salt_str)
        salt_file.close()

        load_new_key = enc_load_key(new_pass)
        if(load_new_key == True):
            new_verif = encrypt_data_blocking(''.join(random.SystemRandom().choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(128)))
            if(new_verif != False):
                verif_file = open(bot_abs_path+'pass_verif','w')
                verif_file.write(new_verif)
                verif_file.close()
                enc_res = True
                print("\n\nA NEW ENCRYPTION SET HAS BEEN GENERATED, YOU SHOULD COPY THE MASTER_PASS, PASS_VERIF AND SALT FILES TO SOMEWHERE SAFE. THEN DELETE THE MASTER_PASS FILE. THAT FILE SHOULD ONLY BE PRESENT WHILE KIT10 IS STARTING UP, ONCE ACTIVE IT SHOULD BE DELETED.\n\n")
            else: print("Unknown error, failed to create new key verification")
        else: print("Unknown error, failed to set new key")

    return enc_res


def encrypt_data_blocking(plain_text):
    try:
        enc_token = enc_key.encrypt(bytes(plain_text,'utf-8'))
        enc_str = enc_token.decode('utf-8')
        return enc_str
    except:
        return False

async def encrypt_data(plain_text):
    enc_str = encrypt_data_blocking(plain_text)
    return enc_str

def decrypt_data_blocking(secret_text):
    try:
        dec_token = enc_key.decrypt(bytes(secret_text,'utf-8'))
        dec_str = dec_token.decode('utf-8')
        return dec_str
    except:
        return False

async def decrypt_data(secret_text):
    dec_str = decrypt_data_blocking(secret_text)
    return dec_str

async def hash_data(plain_text):
    plain_text = str(plain_text)
    hash_data = hashlib.sha256(bytes(plain_text,'utf-8'))
    hash_data_str = hash_data.hexdigest()
    return hash_data_str

async def hash_server_id(server_id=None):
    server_id = str(server_id)
    if(server_id != None): hashed_id = await hash_data(server_id)
    return hashed_id

async def hash_member_id(server_id=None,member_id=None):
    server_id = str(server_id)
    member_id = str(member_id)
    if(server_id != None and member_id != None): hashed_id = await hash_data(server_id+':'+member_id)
    return hashed_id

#===================================================================================================================
#PLUGINS

plugins = {}
for file_entry in os.scandir(bot_abs_path+'plugins/'):
    if(file_entry.is_dir() == True and file_entry.name != "TEMPLATE"):
        module_name = str(file_entry.name)
        print("Load plugin: "+module_name)
        plugins[module_name] = importlib.import_module('plugins.'+module_name)

async def trigger_plugins(server=None,event_name=None,*dargs):
    if(server != None and event_name != None):
        for plugin in plugins: await trigger_plugin(server,event_name,plugin,*dargs)

async def trigger_permission_plugins(server=None,event_name=None,user_id=None,message=None,*dargs):
    if(server != None and event_name != None):
        for plugin in plugins:
            perm_to_run = await has_perm_to_run(server,message,user_id,plugin,None,False)
            if(perm_to_run == True): await trigger_active_plugin(server,event_name,plugin,*dargs)

async def trigger_active_plugins(server=None,event_name=None,*dargs):
    if(server != None and event_name != None):
        ret_vals = {}
        for plugin in plugins:
            ret_vals[plugin] = await trigger_active_plugin(server,event_name,plugin,*dargs)
        return ret_vals
    else: return False

async def trigger_active_plugin(server=None,event_name=None,plugin=None,*dargs):
    if(server != None and event_name != None and plugin != None):
        plugin_status = await is_plugin(server,plugin)
        if(plugin_status == True):
            plugin_return = await trigger_plugin(server,event_name,plugin,*dargs)
            return plugin_return
        else: return False

async def trigger_plugin(server=None,event_name=None,plugin=None,*dargs):
    if(server != None and event_name != "none" and plugin != "none"):
        try:
            run_plugin_function = 'plugins[\''+plugin+'\'].'+event_name+'(*dargs)'
            plugin_return = await eval(run_plugin_function)
        except: plugin_return = False
        return plugin_return


async def is_plugin(server=None,plugin=None):
    if(server != None and plugin != None):
        if(plugin == "bot"):
            return True
        else:
            active_plugins = await get_config('plugins',server,'bot')
            if(active_plugins == False): active_plugins = []
            if(plugin in active_plugins):
                return True
            else: return False


async def plugin_controls(message):
    proc_msg = await get_cmd_args(message.content)
    proc_msg_length = len(proc_msg)

    if(proc_msg_length >= 2):

        if(proc_msg[1] == "list"):
            #list available plugins and their activation status
            list_title = 'Kit10 Plugins'
            list_descript = 'Here is the list of my plugins, and their status on this server:'
            em = discord.Embed(title=list_title, description=list_descript, colour=3447003)

            for this_plugin in plugins:
                plugin_info = await trigger_plugin(message.server,'help_menu',this_plugin)
                plugin_status = ''

                plugin_active = await is_plugin(message.server,this_plugin)
                if(plugin_active == True):
                    plugin_status = plugin_status+'**Status:** active\n'
                else: plugin_status = plugin_status+'**Status:** disabled\n'

                plugin_status = plugin_status+plugin_info['description']
                em.add_field(name='__**'+str(plugin_info['title'])+' ('+this_plugin+')'+'**__',value=plugin_status)


            icon_url = client.user.avatar_url
            if(icon_url == None or icon_url == ""): icon_url = client.user.default_avatar_url
            em.set_author(name=client.user.display_name, icon_url=icon_url)
            em.set_thumbnail(url=icon_url)
            #em.set_image(url)
            await client.send_message(message.channel,embed=em)

        if(proc_msg[1] == "activate"):
            #activate a plugin
            if(proc_msg_length >= 3):
                if(proc_msg[2] in plugins):
                    plugin_active = await is_plugin(message.server,proc_msg[2])
                    if(plugin_active == False):
                        active_plugins = await get_config('plugins',message.server,'bot')
                        if(active_plugins == False): active_plugins = []
                        active_plugins.append(proc_msg[2])
                        await set_config('plugins',message.server,'bot',active_plugins)
                        await trigger_active_plugin(message.server,'server_connected',proc_msg[2],message.server)
                        await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have activated the "'+proc_msg[2]+'" plugin.')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that plugin is already active.')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find the plugin "'+proc_msg[2]+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a plugin to activate')

        if(proc_msg[1] == "deactivate"):
            #deactivate a plugin
            if(proc_msg_length >= 3):
                if(proc_msg[2] in plugins):
                    plugin_active = await is_plugin(message.server,proc_msg[2])
                    if(plugin_active == True):
                        active_plugins = await get_config('plugins',message.server,'bot')
                        if(active_plugins == False): active_plugins = []
                        active_plugins.remove(proc_msg[2])
                        await set_config('plugins',message.server,'bot',active_plugins)
                        await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have deactivated the "'+proc_msg[2]+'" plugin.')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that plugin is already deactivated.')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find the plugin "'+proc_msg[2]+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a plugin to deactivate')

    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify additional arguments.')


async def bot_help_menu():
    help_info = {}
    help_info['title'] = 'Kit10 management'
    help_info['description'] = 'Control which plugins are active, and who can use what commands.'
    return help_info


async def bot_help_section():
    help_info = {}

    cmd_name = 'set'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'log_channel'
    help_entry['args'] = 'channel_name'
    help_entry['description'] = 'Sets the default channel where the bot will post log messages.'
    help_entry['perm_name'] = 'manage_plugins'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'plugin'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'list'
    help_entry['args'] = ''
    help_entry['description'] = 'Lists available plugins and their status on this server.'
    help_entry['perm_name'] = 'manage_plugins'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'activate'
    help_entry['args'] = 'plugin_name'
    help_entry['description'] = 'Activates the plugin called plugin_name.'
    help_entry['perm_name'] = 'manage_plugins'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'deactivate'
    help_entry['args'] = 'plugin_name'
    help_entry['description'] = 'Deactivates the plugin called plugin_name.'
    help_entry['perm_name'] = 'manage_plugins'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'group'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'list'
    help_entry['args'] = ''
    help_entry['description'] = 'Lists the permission groups which different users can be associated with.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add'
    help_entry['args'] = 'group_name'
    help_entry['description'] = 'Create a new permission group called group_name.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'del'
    help_entry['args'] = 'group_name'
    help_entry['description'] = 'Deletes the permission group called group_name.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add_role'
    help_entry['args'] = 'group_name role_name'
    help_entry['description'] = 'Associates role_name to group_name, role_name can also be "server_everyone" or "server_owner".'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'del_role'
    help_entry['args'] = 'group_name role_name'
    help_entry['description'] = 'Deletes a role association called role_name from group_name, role_name can also be "server_everyone" or "server_owner"..'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add_user'
    help_entry['args'] = 'group_name user_name'
    help_entry['description'] = 'Associates user_name to group_name.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'del_user'
    help_entry['args'] = 'group_name user_name'
    help_entry['description'] = 'Deletes the association of user_name from group_name.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'permission'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = 'reset'
    help_entry['args'] = 'plugin_name'
    help_entry['description'] = 'Resets plugin_name\'s permission settings back to defaults.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'list'
    help_entry['args'] = 'plugin_name'
    help_entry['description'] = 'Lists the current permission level settings associated with plugin_name.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'allow_group'
    help_entry['args'] = 'permission_set group_name'
    help_entry['description'] = 'Adds group_name to permission_set.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'revoke_group'
    help_entry['args'] = 'permission_set group_name'
    help_entry['description'] = 'Removes group_name from permission_set.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'channel_mode'
    help_entry['args'] = 'permission_set new_channel_mode'
    help_entry['description'] = 'Sets the channel_mode of permission_set to either "whitelist" or "blacklist".'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'add_channel'
    help_entry['args'] = 'permission_set channel_name'
    help_entry['description'] = 'Adds channel_name to the permission_set. The permission set will process the channel list according to the channel_mode settings.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    help_entry = {}
    help_entry['command'] = 'del_channel'
    help_entry['args'] = 'permission_set channel_name'
    help_entry['description'] = 'Removes channel_name from the permission_set. The permission set will process the channel list according to the channel_mode settings.'
    help_entry['perm_name'] = 'manage_permissions'
    help_info[cmd_name].append(help_entry)

    cmd_name = 'bottime'
    help_info[cmd_name] = []

    help_entry = {}
    help_entry['command'] = ''
    help_entry['args'] = ''
    help_entry['description'] = 'Displays the current bot time.'
    help_entry['perm_name'] = 'manage_plugins'
    help_info[cmd_name].append(help_entry)

    return help_info


async def bot_plugin_permissions():
    perm_info = {}

    this_perm = 'manage_plugins'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')

    this_perm = 'manage_permissions'
    perm_info[this_perm] = {}
    perm_info[this_perm]['groups'] = [] #members/admins/owner
    perm_info[this_perm]['groups'].append('owner')

    return perm_info




#===================================================================================================================
#Permission functions


async def get_permission_groups(server):
    perm_groups = await get_config('perm_groups',server,'bot')
    if(perm_groups == False): perm_groups = {}
    def_groups = {}
    if('owner' not in perm_groups):
        def_groups['owner'] = {}
        def_groups['owner']['roles'] = []
        def_groups['owner']['roles'].append('server_owner')
        def_groups['owner']['users'] = []
    if('admins' not in perm_groups):
        def_groups['admins'] = {}
        def_groups['admins']['roles'] = []
        def_groups['admins']['users'] = []
    if('members' not in perm_groups):
        def_groups['members'] = {}
        def_groups['members']['roles'] = []
        def_groups['members']['roles'].append('server_everyone')
        def_groups['members']['users'] = []
    if(len(def_groups) > 0):
        final_groups = {}
        final_groups.update(def_groups)
        final_groups.update(perm_groups)
    else: final_groups = perm_groups
    return final_groups

async def has_user_group(server,user_id,group_qualifs):
    has_this_group = False

    if(server.owner.id == user_id):
        has_this_group = True
    else:

        if(has_this_group == False):
            for list_user in group_qualifs['users']:
                if(user_id == list_user): has_this_group = True

        if(has_this_group == False):
            for list_role in group_qualifs['roles']:
                if(list_role == "server_everyone"):
                    has_this_group = True
                elif(list_role == "server_owner"):
                    if(str(server.owner.id) == str(user_id)): has_this_group = True
                elif(has_this_group == False):
                    has_this_role = await has_role(user_id,list_role,server)
                    if(has_this_role == True): has_this_group = True

    return has_this_group

async def get_user_groups(server,user_id):
    group_list = await get_permission_groups(server)
    has_groups = []

    has_owner = await has_user_group(server,user_id,group_list['owner'])

    for group in group_list:
        has_this_group = False
        if(has_owner == True):
            has_this_group = True
        else:
            has_this_group = await has_user_group(server,user_id,group_list[group])
        if(has_this_group == True): has_groups.append(group)

    return has_groups

async def has_perm_to_run(server=None,message=None,user_id=None,plugin=None,sub_perm=None,speak_error=False):
    member_of = await get_user_groups(server,user_id)
    plugin_perms = await get_plugin_perms(server,plugin)
    has_perm = False

    if('owner' in member_of):
        has_perm = True
    else:

        if(sub_perm != None):
            if(sub_perm in plugin_perms['sub']):
                use_perms = plugin_perms['sub'][sub_perm]
            else: use_perms = False
        else: use_perms = plugin_perms['global']

        if(use_perms != False):
            conflict_found = False

            if(conflict_found == False and message != None and message.channel.is_private == False):
                #check channel is valid
                if('channel_mode' not in use_perms): use_perms['channel_mode'] = 'blacklist'
                if('channels' not in use_perms): use_perms['channels'] = []

                if(use_perms['channel_mode'] == "blacklist"):
                    if(message.channel.id in use_perms['channels']): conflict_found = True
                else:
                    if(message.channel.id not in use_perms['channels']): conflict_found = True

                if(speak_error == True and conflict_found == True): await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you cannot run that command in this channel.')

            if(conflict_found == False):
                #check group is valid
                valid_group = False
                if('groups' not in use_perms or len(use_perms['groups']) == 0):
                    if('members' in member_of): valid_group = True
                else:
                    for list_group in use_perms['groups']:
                        if(list_group in member_of): valid_group = True

                if(valid_group == False):
                    conflict_found = True
                    if(message != None and speak_error == True): await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you don\'t have the required permissions to run that command.')

            if(conflict_found == False): has_perm = True

    return has_perm



async def get_plugin_perms(server,plugin):
    perm_settings = await get_config('perm_settings',server,'bot')
    if(perm_settings == False): perm_settings = {}

    def_perms = {}
    def_perms['global'] = {}
    if(plugin == "bot"):
        def_perms['sub'] = await bot_plugin_permissions()
    else: def_perms['sub'] = await trigger_plugin(server,'plugin_permissions',plugin)

    if(plugin in perm_settings and perm_settings[plugin] != False):
        final_perms = perm_settings[plugin]
    else:
        final_perms = def_perms
        #stored_perms = {}
        #stored_perms['global'] = {}
        #stored_perms['sub'] = {}

    #final_perms = {}
    #final_perms.update(stored_perms)
    #final_perms.update(def_perms)

    return final_perms

async def set_plugin_perms(server,plugin,new_perm_data):
    perm_settings = await get_config('perm_settings',server,'bot')
    if(perm_settings == False): perm_settings = {}
    perm_settings[plugin] = new_perm_data
    await set_config('perm_settings',server,'bot',perm_settings)
    return True


async def permission_group_controls(message):
    proc_msg = await get_cmd_args(message.content)
    proc_msg_length = len(proc_msg)

    if(proc_msg_length >= 2):

        if(proc_msg[1] == "list"):
            #list all current permission groups
            list_title = 'Permission groups'
            list_descript = 'Here are the permission groups currently in place:'
            icon_url = client.user.avatar_url
            if(icon_url == None or icon_url == ""): icon_url = client.user.default_avatar_url
            em = discord.Embed(title=list_title, description=list_descript, colour=3447003)
            em.set_author(name=client.user.display_name, icon_url=icon_url)
            em.set_thumbnail(url=icon_url)
            #em.set_image(url)

            perm_groups = await get_permission_groups(message.server)
            for this_group in perm_groups:
                group_info = ''

                list_info = ''
                for entry in perm_groups[this_group]['roles']:
                    if(entry == "server_owner" or entry == "server_everyone"):
                        get_rname = entry
                    else:
                        get_rname = await role_name_from_id(entry,message.server)
                        if(get_rname == False): get_rname = ''
                    if(get_rname != ""):
                        if(list_info != ""): list_info = list_info+', '
                        list_info = list_info+get_rname
                if(list_info == ""): list_info = 'None assigned'
                #em.add_field(name=str(this_group),value='**Roles: **'+list_info)
                group_info = group_info+'**Roles: **'+list_info+'\n'

                list_info = ''
                for entry in perm_groups[this_group]['users']:
                    get_rname = await find_user(message.server,'<@'+str(entry)+'>',True)
                    if(get_rname != False):
                        if(list_info != ""): list_info = list_info+', '
                        list_info = list_info+get_rname.name
                if(list_info == ""): list_info = 'None assigned'
                group_info = group_info+'**Users: **'+list_info+'\n'

                em.add_field(name=str(this_group),value=group_info)

            await client.send_message(message.channel,embed=em)

        if(proc_msg[1] == "add"):
            #create a new group
            if(proc_msg_length == 3):
                perm_groups = await get_permission_groups(message.server)
                if(proc_msg[2] not in perm_groups):
                    perm_groups[proc_msg[2]] = {}
                    perm_groups[proc_msg[2]]['roles'] = []
                    perm_groups[proc_msg[2]]['users'] = []
                    await set_config('perm_groups',message.server,'bot',perm_groups)
                    await client.send_message(message.channel,'Okay <@'+message.author.id+'>, that group has been created')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, a group with that name already exists')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the name of a group to add')

        if(proc_msg[1] == "del"):
            #delete a group and remove from all permission settings
            if(proc_msg_length == 3):
                if(proc_msg[2] != "owner" and proc_msg[2] != "admins" and proc_msg[2] != "members"):
                    perm_groups = await get_permission_groups(message.server)
                    if(proc_msg[2] in perm_groups):

                        #TODO: REMOVE GROUP FROM PERMISSIONS OBJECT

                        del perm_groups[proc_msg[2]]
                        await set_config('perm_groups',message.server,'bot',perm_groups)
                        await client.send_message(message.channel,'Okay <@'+message.author.id+'>, that group has been removed')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, a group with that name does not exist')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that group is fixed, you cannot remove it.')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the name of a group to remove')

        if(proc_msg[1] == "add_role"):
            #add a role to the definition for a group
            proc_msg = await get_cmd_args(message.content,3)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length == 4):
                perm_groups = await get_permission_groups(message.server)
                if(proc_msg[2] in perm_groups):

                    if(proc_msg[3] == "server_owner" or proc_msg[3] == "server_everyone"):
                        r_name = proc_msg[3]
                    else: r_name = await find_role_arg(message.server,proc_msg[3])

                    if(r_name not in perm_groups[proc_msg[2]]['roles']):
                        if(r_name != False):
                            perm_groups[proc_msg[2]]['roles'].append(r_name)
                            await set_config('perm_groups',message.server,'bot',perm_groups)
                            await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have added that role to the "'+proc_msg[2]+'" group')
                        else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a role with the name "'+proc_msg[3]+'"')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that role is already in that group')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a group with the name "'+proc_msg[2]+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the name of a group and the name of a role to add to it.')

        if(proc_msg[1] == "del_role"):
            #remove a role from the definition for a group
            proc_msg = await get_cmd_args(message.content,3)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length == 4):
                perm_groups = await get_permission_groups(message.server)
                if(proc_msg[2] in perm_groups):

                    if(proc_msg[3] == "server_owner" or proc_msg[3] == "server_everyone"):
                        r_name = proc_msg[3]
                    else: r_name = await find_role_arg(message.server,proc_msg[3])

                    if(r_name in perm_groups[proc_msg[2]]['roles']):
                        if(r_name != False):
                            perm_groups[proc_msg[2]]['roles'].remove(r_name)
                            await set_config('perm_groups',message.server,'bot',perm_groups)
                            await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have removed that role from the "'+proc_msg[2]+'" group')
                        else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a role with the name "'+proc_msg[3]+'"')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that role is already not in that group')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a group with the name "'+proc_msg[2]+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the name of a group and the name of a role to remove from it.')

        if(proc_msg[1] == "add_user"):
            #add user to definition group
            proc_msg = await get_cmd_args(message.content)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 4):
                perm_groups = await get_permission_groups(message.server)
                if(proc_msg[2] in perm_groups):
                    r_name = await find_user(message.server,proc_msg[3])
                    if(r_name not in perm_groups[proc_msg[2]]['users']):
                        if(r_name != False):
                            perm_groups[proc_msg[2]]['users'].append(r_name)
                            await set_config('perm_groups',message.server,'bot',perm_groups)
                            await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have added that user to the "'+proc_msg[2]+'" group')
                        else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user with the name "'+proc_msg[3]+'"')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that user is already in that group')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a group with the name "'+proc_msg[2]+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the name of a group and the name of a user to add to it.')

        if(proc_msg[1] == "del_user"):
            #remove user from definition group
            proc_msg = await get_cmd_args(message.content)
            proc_msg_length = len(proc_msg)
            if(proc_msg_length >= 4):
                perm_groups = await get_permission_groups(message.server)
                if(proc_msg[2] in perm_groups):
                    r_name = await find_user(message.server,proc_msg[3])
                    if(r_name in perm_groups[proc_msg[2]]['users']):
                        if(r_name != False):
                            perm_groups[proc_msg[2]]['users'].remove(r_name)
                            await set_config('perm_groups',message.server,'bot',perm_groups)
                            await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have removed that user from the "'+proc_msg[2]+'" group')
                        else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a user with the name "'+proc_msg[3]+'"')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that user is already not in that group')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a group with the name "'+proc_msg[2]+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify the name of a group and the name of a user to remove from it.')


async def permission_controls(message):
    proc_msg = await get_cmd_args(message.content)
    proc_msg_length = len(proc_msg)

    if(proc_msg_length >= 2):

        if(proc_msg[1] == "list"):
            if(proc_msg_length == 3):
                if(proc_msg[2] == "bot" or proc_msg[2] in plugins):
                    plugin_active = await is_plugin(message.server,proc_msg[2])
                    if(plugin_active == True):
                        #list plugin permissions and current values
                        this_plugin = proc_msg[2]

                        if(this_plugin == "bot"):
                            plugin_info = await bot_help_menu()
                        else: plugin_info = await trigger_plugin(message.server,'help_menu',this_plugin)
                        plugin_perms = await get_plugin_perms(message.server,this_plugin)
                        plugin_perms_out = ''

                        sublen = len(plugin_perms['sub'])
                        if(sublen == 0):

                            if('channel_mode' not in plugin_perms['global']):
                                use_channel_mode = 'blacklist'
                            else: use_channel_mode = plugin_perms['global']['channel_mode']
                            plugin_perms_out = plugin_perms_out+'Channel mode: _'+use_channel_mode+'_'

                            if('channels' not in plugin_perms['global']):
                                use_channel_list = []
                            else: use_channel_list = plugin_perms['global']['channels']
                            build_channel_list = ''
                            if(len(use_channel_list) > 0):
                                for channel in use_channel_list:
                                    c_name = await channel_name_from_id(message.server,channel)
                                    if(c_name != False):
                                        if(build_channel_list != ""): build_channel_list = build_channel_list+', '
                                        build_channel_list = build_channel_list+c_name
                            if(build_channel_list == ""):
                                if(use_channel_mode == "blacklist"):
                                    build_channel_list = 'All allowed'
                                else: build_channel_list = 'None allowed'
                            plugin_perms_out = plugin_perms_out+'\nChannels: _'+build_channel_list+'_'

                            if('groups' not in plugin_perms['global']):
                                use_channel_list = []
                            else: use_channel_list = plugin_perms['global']['groups']
                            build_channel_list = ''
                            if(len(use_channel_list) > 0):
                                for channel in use_channel_list:
                                    if(build_channel_list != ""): build_channel_list = build_channel_list+', '
                                    build_channel_list = build_channel_list+channel
                            if(build_channel_list == ""): build_channel_list = 'None specified, will allow anyone in the "members" group by default.'
                            plugin_perms_out = plugin_perms_out+'\nAllowed groups: _'+build_channel_list+'_'

                        for sub_perm in plugin_perms['sub']:
                            plugin_perms_out = plugin_perms_out+'\n\n**'+this_plugin+':'+sub_perm+'**'

                            if('channel_mode' not in plugin_perms['sub'][sub_perm]):
                                use_channel_mode = 'blacklist'
                            else: use_channel_mode = plugin_perms['sub'][sub_perm]['channel_mode']
                            plugin_perms_out = plugin_perms_out+'\nChannel mode: _'+use_channel_mode+'_'

                            if('channels' not in plugin_perms['sub'][sub_perm]):
                                use_channel_list = []
                            else: use_channel_list = plugin_perms['sub'][sub_perm]['channels']
                            build_channel_list = ''
                            if(len(use_channel_list) > 0):
                                for channel in use_channel_list:
                                    c_name = await channel_name_from_id(message.server,channel)
                                    if(c_name != False):
                                        if(build_channel_list != ""): build_channel_list = build_channel_list+', '
                                        build_channel_list = build_channel_list+c_name
                            if(build_channel_list == ""):
                                if(use_channel_mode == "blacklist"):
                                    build_channel_list = 'All allowed'
                                else: build_channel_list = 'None allowed'
                            plugin_perms_out = plugin_perms_out+'\nChannels: _'+build_channel_list+'_'

                            if('groups' not in plugin_perms['sub'][sub_perm]):
                                use_channel_list = []
                            else: use_channel_list = plugin_perms['sub'][sub_perm]['groups']
                            build_channel_list = ''
                            if(len(use_channel_list) > 0):
                                for channel in use_channel_list:
                                    if(build_channel_list != ""): build_channel_list = build_channel_list+', '
                                    build_channel_list = build_channel_list+channel
                                if(build_channel_list == ""): build_channel_list = 'None specified, will allow anyone in the "members" group by default.'
                                plugin_perms_out = plugin_perms_out+'\nAllowed groups: _'+build_channel_list+'_'

                        list_title = 'Kit10 '+str(plugin_info['title'])+' ('+this_plugin+') permissions'
                        list_descript = plugin_perms_out
                        em = discord.Embed(title=list_title, description=list_descript, colour=3447003)
                        icon_url = client.user.avatar_url
                        if(icon_url == None or icon_url == ""): icon_url = client.user.default_avatar_url
                        em.set_author(name=client.user.display_name, icon_url=icon_url)
                        #em.set_thumbnail(url=icon_url)
                        #em.set_image(url)
                        await client.send_message(message.channel,embed=em)
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that plugin is not activated.')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a plugin with that name.')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a plugin to view the permissions for.')


        if(proc_msg[1] == "reset"):
            #reset plugin permissions back to default
            if(proc_msg_length == 3):
                this_plugin = proc_msg[2]

                plugin_active = await is_plugin(message.server,this_plugin)
                if(plugin_active == True):
                    #plugin_perms = await get_plugin_perms(message.server,this_plugin)
                    plugin_perms = False
                    await set_plugin_perms(message.server,this_plugin,plugin_perms)
                    await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have reset permissions for that plugin back to default.')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a plugin called "'+this_plugin+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a plugin you want to reset the permissions for.')


        if(proc_msg[1] == "allow_group"):
            #allow a particular permission group to run command(s) in a certain plugin
            if(proc_msg_length == 4):

                if(':' in proc_msg[2]):
                    proc_plugin = proc_msg[2].split(":")
                    this_plugin = proc_plugin[0]
                    this_sub = proc_plugin[1]
                else:
                    this_plugin = proc_msg[2]
                    this_sub = ''

                plugin_active = await is_plugin(message.server,this_plugin)
                if(plugin_active == True):
                    plugin_perms = await get_plugin_perms(message.server,this_plugin)
                    if(this_sub == "" or this_sub in plugin_perms['sub']):
                        perm_groups = await get_permission_groups(message.server)
                        if(proc_msg[3] in perm_groups):

                            if(this_sub != ""):
                                if('groups' not in plugin_perms['sub'][this_sub]): plugin_perms['sub'][this_sub]['groups'] = []
                                orig_val = plugin_perms['sub'][this_sub]['groups']
                            else:
                                if('groups' not in plugin_perms['global']): plugin_perms['global']['groups'] = []
                                orig_val = plugin_perms['global']['groups']

                            if(proc_msg[3] not in orig_val):

                                if(this_sub != ""):
                                    plugin_perms['sub'][this_sub]['groups'].append(proc_msg[3])
                                else: plugin_perms['global']['groups'].append(proc_msg[3])
                                await set_plugin_perms(message.server,this_plugin,plugin_perms)
                                await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have added that group to the permission list.')

                            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that group is already on that permission list.')
                        else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a group called "'+proc_msg[3]+'"')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a permission in that plugin called "'+this_sub+'"')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a plugin called "'+this_plugin+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a permission area and the group you want to add.')

        if(proc_msg[1] == "revoke_group"):
            #revoke a particular permission group from running command(s)
            #proc_msg[3] = permission
            if(proc_msg_length == 4):

                if(':' in proc_msg[2]):
                    proc_plugin = proc_msg[2].split(":")
                    this_plugin = proc_plugin[0]
                    this_sub = proc_plugin[1]
                else:
                    this_plugin = proc_msg[2]
                    this_sub = ''

                plugin_active = await is_plugin(message.server,this_plugin)
                if(plugin_active == True):
                    plugin_perms = await get_plugin_perms(message.server,this_plugin)
                    if(this_sub == "" or this_sub in plugin_perms['sub']):
                        perm_groups = await get_permission_groups(message.server)
                        if(proc_msg[3] in perm_groups):

                            if(this_sub != ""):
                                if('groups' not in plugin_perms['sub'][this_sub]): plugin_perms['sub'][this_sub]['groups'] = []
                                orig_val = plugin_perms['sub'][this_sub]['groups']
                            else:
                                if('groups' not in plugin_perms['global']): plugin_perms['global']['groups'] = []
                                orig_val = plugin_perms['global']['groups']

                            if(proc_msg[3] in orig_val):

                                if(this_sub != ""):
                                    plugin_perms['sub'][this_sub]['groups'].remove(proc_msg[3])
                                else: plugin_perms['global']['groups'].remove(proc_msg[3])
                                await set_plugin_perms(message.server,this_plugin,plugin_perms)
                                await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have removed that group from the permission list.')

                            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that group is already not on that permission list.')
                        else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a group called "'+proc_msg[3]+'"')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a permission in that plugin called "'+this_sub+'"')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a plugin called "'+this_plugin+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a permission area and the group you want to remove.')


        if(proc_msg[1] == "channel_mode"):
            #list channels list mode can be "blacklist" or "whitelist"
            if(proc_msg_length == 4):

                if(':' in proc_msg[2]):
                    proc_plugin = proc_msg[2].split(":")
                    this_plugin = proc_plugin[0]
                    this_sub = proc_plugin[1]
                else:
                    this_plugin = proc_msg[2]
                    this_sub = ''

                plugin_active = await is_plugin(message.server,this_plugin)
                if(plugin_active == True):
                    plugin_perms = await get_plugin_perms(message.server,this_plugin)
                    if(this_sub == "" or this_sub in plugin_perms['sub']):

                        if(this_sub != ""):
                            if('channel_mode' not in plugin_perms['sub'][this_sub]): plugin_perms['sub'][this_sub]['channel_mode'] = 'blacklist'
                            orig_val = plugin_perms['sub'][this_sub]['channel_mode']
                        else:
                            if('channel_mode' not in plugin_perms['global']): plugin_perms['global']['channel_mode'] = 'blacklist'
                            orig_val = plugin_perms['global']['channel_mode']

                        if(proc_msg[3] == "blacklist" or proc_msg[3] == "whitelist"):

                            if(this_sub != ""):
                                plugin_perms['sub'][this_sub]['channel_mode'] = proc_msg[3]
                            else: plugin_perms['global']['channel_mode'] = proc_msg[3]
                            await set_plugin_perms(message.server,this_plugin,plugin_perms)
                            await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have set that permissions channel mode.')

                        else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you can only set this to either "blacklist" or "whitelist".')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a permission in that plugin called "'+this_sub+'"')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a plugin called "'+this_plugin+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a permission area and the channel mode you want to set.')

        if(proc_msg[1] == "add_channel"):
            #add a channel to the permission list
            if(proc_msg_length == 4):

                if(':' in proc_msg[2]):
                    proc_plugin = proc_msg[2].split(":")
                    this_plugin = proc_plugin[0]
                    this_sub = proc_plugin[1]
                else:
                    this_plugin = proc_msg[2]
                    this_sub = ''

                plugin_active = await is_plugin(message.server,this_plugin)
                if(plugin_active == True):
                    plugin_perms = await get_plugin_perms(message.server,this_plugin)
                    if(this_sub == "" or this_sub in plugin_perms['sub']):
                        perm_groups = await get_permission_groups(message.server)
                        c_data = await channel_id_from_name(message.server,proc_msg[3])
                        if(c_data != False):

                            if(this_sub != ""):
                                if('channels' not in plugin_perms['sub'][this_sub]): plugin_perms['sub'][this_sub]['channels'] = []
                                orig_val = plugin_perms['sub'][this_sub]['channels']
                            else:
                                if('channels' not in plugin_perms['global']): plugin_perms['global']['channels'] = []
                                orig_val = plugin_perms['global']['channels']

                            if(c_data not in orig_val):

                                if(this_sub != ""):
                                    plugin_perms['sub'][this_sub]['channels'].append(c_data)
                                else: plugin_perms['global']['channels'].append(c_data)
                                await set_plugin_perms(message.server,this_plugin,plugin_perms)
                                await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have added that channel to the permission list.')

                            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that channel is already on that permission list.')
                        else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[3]+'"')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a permission in that plugin called "'+this_sub+'"')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a plugin called "'+this_plugin+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a permission area and the channel you want to add.')

        if(proc_msg[1] == "del_channel"):
            #delete a channel from the permission list
            if(proc_msg_length == 4):

                if(':' in proc_msg[2]):
                    proc_plugin = proc_msg[2].split(":")
                    this_plugin = proc_plugin[0]
                    this_sub = proc_plugin[1]
                else:
                    this_plugin = proc_msg[2]
                    this_sub = ''

                plugin_active = await is_plugin(message.server,this_plugin)
                if(plugin_active == True):
                    plugin_perms = await get_plugin_perms(message.server,this_plugin)
                    if(this_sub == "" or this_sub in plugin_perms['sub']):
                        perm_groups = await get_permission_groups(message.server)
                        c_data = await channel_id_from_name(message.server,proc_msg[3])
                        if(c_data != False):

                            if(this_sub != ""):
                                if('channels' not in plugin_perms['sub'][this_sub]): plugin_perms['sub'][this_sub]['channels'] = []
                                orig_val = plugin_perms['sub'][this_sub]['channels']
                            else:
                                if('channels' not in plugin_perms['global']): plugin_perms['global']['channels'] = []
                                orig_val = plugin_perms['global']['channels']

                            if(c_data in orig_val):

                                if(this_sub != ""):
                                    plugin_perms['sub'][this_sub]['channels'].remove(c_data)
                                else: plugin_perms['global']['channels'].remove(c_data)
                                await set_plugin_perms(message.server,this_plugin,plugin_perms)
                                await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I have removed that channel from the permission list.')

                            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, that channel is already not on that permission list.')
                        else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[3]+'"')
                    else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a permission in that plugin called "'+this_sub+'"')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a plugin called "'+this_plugin+'"')
            else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, you must specify a permission area and the channel you want to remove.')




#===================================================================================================================
#SERVER

async def update_server_invites(server):
    new_list = await get_server_invites(server)
    if(new_list == False):
        invite_list[server.id] = []
        return False
    else:
        invite_list[server.id] = await get_server_invites(server)
        return True

async def get_server_invites(server):
    try:
        inv_list = await client.invites_from(server)
    except: inv_list = False
    return inv_list

@client.event
async def on_server_emojis_update(before,after):
    if(startup_complete == True):
        await trigger_active_plugins(before.server,'emoji_list_update',before,after)

@client.event
async def on_server_join(server):
    await log_entry("Joined server "+server.name,server)
    await start_server(server)
    await trigger_active_plugins(server,'server_join',server)


@client.event
async def on_ready():
    await log_entry('Connected to Discord as '+client.user.name+' ('+str(client.user.id)+')\n')

    await log_entry('Starting up...\n')
    await asyncio.sleep(5)

    await set_status()

    await pm_server_expire()

    for server in client.servers:
        await start_server(server)
        await trigger_active_plugins(server,'server_connected',server)

    global startup_complete
    startup_complete = True

    for server in client.servers:
        notify_mods = await bot_use_channel(server,'bot','log_channel')
        if(notify_mods != False): await client.send_message(notify_mods,'**Startup complete**')

    await log_entry("All connected servers configured and updated, startup complete\n")


@client.event
async def on_server_update(server_before,server_after):
    await update_server_db('update',server_after)
    await trigger_active_plugins(server_after,'server_update',server_before,server_after)


@client.event
async def on_server_remove(server):
    await log_entry("Bot has been removed from server \""+server.name+"\"",server)
    if(server.id in config): del config[server.id]

    del_server = db.cursor()
    removed_stamp = await current_timestamp()
    del_server.execute("UPDATE servers SET removed_stamp=? WHERE server_id=?",(removed_stamp,server.id,))
    db.commit()

    await trigger_active_plugins(server,'server_remove',server)


async def start_server(server=None):
    if(server != None):

        if(verbose_out == True): await log_entry("Configuring server "+str(server.name),server)
        await update_server_db('start',server)

        notify_mods = await bot_use_channel(server,'bot','log_channel')
        if(notify_mods != False): await client.send_message(notify_mods,'Restarting, this may take a moment please wait...')

        #update the channel records
        if(verbose_out == True): await log_entry("Updating channel records",server)
        for channel in server.channels:
            await channel_update_db('start',channel)
        if(verbose_out == True): await log_entry("Channel records updated",server)

        #update the user records
        if(verbose_out == True): await log_entry("Updating User records",server)
        for member in server.members:
            await user_update_db('start',member,server)
        if(verbose_out == True): await log_entry("User record update complete",server)

        #update invite list
        if(verbose_out == True): await log_entry("Attempting to get invite list",server)
        invite_list[server.id] = await get_server_invites(server)
        if(invite_list[server.id] == False): invite_list[server.id] = []
        for inv in invite_list[server.id]:
            if(verbose_out == True): await log_entry("Found invite "+inv.code+" ("+inv.url+") used "+str(inv.uses)+" times.",server)

        if(verbose_out == True): await log_entry("Configuration complete\n",server)



async def update_server_db(type=None,server_obj=None):
    if(type != None and server_obj != None):
        use_server_id = await hash_server_id(server_obj.id)

        find_server = db.cursor()
        find_server.execute("SELECT * FROM servers WHERE server_id=?",(use_server_id,))
        found_server_name = ''
        found_server_settings = ''
        for row in find_server:
            found_server_name = await decrypt_data(row['server_name'])
            found_server_settings = await decrypt_data(row['settings'])

        if(found_server_name != False and found_server_name != None and found_server_name != ""):
            #Server is in database

            config[server_obj.id] = json.loads(found_server_settings)
            if(verbose_out == True): await log_entry("Loaded server configuration settings",server_obj)

            save_server = db.cursor()
            if(found_server_name != server_obj.name):
                if(verbose_out == True): await log_entry("Updating record for server "+server_obj.name,server_obj)
                save_server_name = await encrypt_data(server_obj.name)
                save_server.execute("UPDATE servers SET server_name=?, removed_stamp='0' WHERE server_id=?",(save_server_name,use_server_id,))
            else:
                save_server.execute("UPDATE servers SET removed_stamp='0' WHERE server_id=?",(use_server_id,))

            db.commit()
        else:
            #Server is new
            if(verbose_out == True): await log_entry("New server \""+server_obj.name+"\" detected",server_obj)
            config[server_obj.id] = {}
            save_settings = await encrypt_data(json.dumps(config[server_obj.id]))
            save_server_name = await encrypt_data(server_obj.name)
            save_server_id = await encrypt_data(server_obj.id)
            save_server = db.cursor()
            save_server.execute("INSERT INTO servers (server_id,stored_server_id,settings,server_name,removed_stamp) VALUES (?,?,?,?,'0')",(use_server_id,save_server_id,save_settings,save_server_name,))
            db.commit()

        #if(len(config[server_obj.id]) <= 1): await server_setup_wizard(server_obj)


async def server_setup_wizard(server):
    print("run setup wizard")

#===================================================================================================================
#Receive messages

'''
user mention: <@272459124921466890>
role mention: <@&301146362471383040>
mention everyone who can see this channel: @here
mention everyone on the server: @everyone
'''

async def pm_server_expire(dummy_serv=None,dummy_arg=None):

    current_time = await current_timestamp()
    expired_prefs = []

    for pm in pm_servers:
        server_set_time = int(pm_servers[pm]['time'])
        time_diff = current_time - server_set_time
        use_timeout = bot_pm_server_timeout * 60
        if(time_diff >= use_timeout): expired_prefs.append(pm)

    ep_len = len(expired_prefs) - 1
    ep_run = 0
    while(ep_run <= ep_len):
        pm = expired_prefs[ep_run]
        await log_entry("User "+str(pm)+" PM server preference has expired")
        del pm_servers[pm]
        ep_run = ep_run + 1

    exp_time = current_time + 60
    await add_task(None,exp_time,'bot','pm_server_expire')


async def find_pm_server(message):

    current_time = await current_timestamp()

    if(message.author.id in pm_servers):
        ret_server_obj = pm_servers[message.author.id]['server']
        pm_servers[message.author.id]['time'] = current_time
    else: ret_server_obj = False

    if(ret_server_obj == False):
        found_servers = []

        for server in client.servers:
            for member in server.members:
                if(member.id == message.author.id):
                    found_servers.append(server)

        server_run = len(found_servers) - 1
        if(server_run == 0):
            ret_server_obj = found_servers[0]
            pm_servers[message.author.id] = {}
            pm_servers[message.author.id]['time'] = current_time
            pm_servers[message.author.id]['server'] = found_servers[0]
        else:
            s_out = 0
            pick_server = ''
            while(s_out <= server_run):
                pick_num = s_out + 1
                pick_server = pick_server+'\n**'+str(pick_num)+')** '+found_servers[s_out].name
                s_out = s_out + 1

            await client.send_message(message.channel,'<@'+message.author.id+'> it appears you are on more than one of the servers I am also on, please type the number of the server you want to run this command for:\n'+pick_server+'\n\nI will remember your preference for a little while. But if you want to change which server you are running commands against before I ask again, you can do so by running `'+bot_cmd_char+'pick_server`')
            conf_msg = await client.wait_for_message(author=message.author,channel=message.channel)
            s_out = 0
            while(s_out <= server_run):
                pick_num = s_out + 1
                if(str(pick_num) == conf_msg.content):
                    ret_server_obj = found_servers[s_out]
                    pm_servers[message.author.id] = {}
                    pm_servers[message.author.id]['time'] = current_time
                    pm_servers[message.author.id]['server'] = found_servers[s_out]
                    await client.send_message(message.channel,'Okay <@'+message.author.id+'>, for now I will assume you\'re running commands for server "'+ret_server_obj.name+'"')
                s_out = s_out + 1

    return ret_server_obj



@client.event
async def on_typing(channel,user,datestamp):
    if(startup_complete == True):
        if(channel.is_private == False):
            await trigger_active_plugins(channel.server,'message_typing',channel,user,datestamp)

@client.event
async def on_reaction_add(reaction,member):
    if(startup_complete == True):
        await trigger_active_plugins(member.server,'reaction_add',reaction,member)

@client.event
async def on_reaction_remove(reaction,member):
    if(startup_complete == True):
        await trigger_active_plugins(member.server,'reaction_remove',reaction,member)

@client.event
async def on_message_delete(message):
    if(startup_complete == True):
        await trigger_active_plugins(message.server,'message_delete',message)

@client.event
async def on_message(message):
    if(startup_complete == True):
        #print("\nmessage content: \""+message.content+"\"")
        await bot_receive_message(message)
        await trigger_active_plugins(message.server,'message_new',message)


@client.event
async def on_message_edit(old_msg,new_msg):
    if(startup_complete == True):
        if(old_msg.content != new_msg.content): await bot_receive_message(new_msg)
        await trigger_active_plugins(old_msg.server,'message_edit',old_msg,new_msg)


async def bot_receive_message(message):

    if(message.channel.is_private == True):
        if(client.user.id != message.author.id):
            if(message.content.startswith(bot_cmd_char+'pick_server') and message.author.id in pm_servers): del pm_servers[message.author.id]
            ov_server = await find_pm_server(message)
            if(ov_server != False): message.server = ov_server

    if(client.user.id != message.author.id):
        await user_last_seen(message.server,message.author)

        if(message.content.startswith(bot_cmd_char+'help')):
            #help system
            await help_menu(message)
        elif(message.content.startswith(bot_cmd_char+'set log_channel')):
            #main log channel
            has_perm = await has_perm_to_run(message.server,message,message.author.id,'bot','manage_plugins',True)
            if(has_perm == True):
                proc_msg = await get_cmd_args(message.content)
                proc_msg_length = len(proc_msg)
                find_channel = await find_channel_arg(message.server,proc_msg[2],True)
                if(find_channel != False):
                    await bot_set_channel(message.server,'bot','log_channel',find_channel.id)
                    await client.send_message(message.channel,'Okay <@'+message.author.id+'>, I will now use that channel for posting general logs.')
                else: await client.send_message(message.channel,'Sorry <@'+message.author.id+'>, I couldn\'t find a channel called "'+proc_msg[2]+'"')
        elif(message.content.startswith(bot_cmd_char+'plugin')):
            #plugin controls
            has_perm = await has_perm_to_run(message.server,message,message.author.id,'bot','manage_plugins',True)
            if(has_perm == True): await plugin_controls(message)
        elif(message.content.startswith(bot_cmd_char+'permission')):
            #permission controls
            has_perm = await has_perm_to_run(message.server,message,message.author.id,'bot','manage_permissions',True)
            if(has_perm == True): await permission_controls(message)
        elif(message.content.startswith(bot_cmd_char+'group')):
            #permission controls
            has_perm = await has_perm_to_run(message.server,message,message.author.id,'bot','manage_permissions',True)
            if(has_perm == True): await permission_group_controls(message)
        elif(message.content.startswith(bot_cmd_char+'bottime')):
            #show current bot time
            has_perm = await has_perm_to_run(message.server,message,message.author.id,'bot','manage_plugins',True)
            if(has_perm == True):
                get_timestamp = await current_timestamp()
                get_timestamp_hr = await timestamp_to_date(get_timestamp)
                await client.send_message(message.channel,'Bot time: '+str(get_timestamp_hr)+' ('+str(get_timestamp)+').')
        else:
            await trigger_permission_plugins(message.server,'message_process',message.author.id,message,message)



#===================================================================================================================
#User functions

@client.event
async def on_member_update(old_member,new_member):
    if(startup_complete == True):
        await user_update_db('update',new_member,new_member.server)
        await trigger_active_plugins(new_member.server,'member_update',old_member,new_member)

@client.event
async def on_member_join(member):
    if(startup_complete == True):
        await user_update_db('join',member,member.server)
        await trigger_active_plugins(member.server,'member_join',member)

@client.event
async def on_member_remove(member):
    if(startup_complete == True):
        await user_update_db('leave',member,member.server)
        await trigger_active_plugins(member.server,'member_remove',member)

@client.event
async def on_voice_state_update(before,after):
    if(startup_complete == True):
        await trigger_active_plugins(before.server,'member_voice_update',before,after)

@client.event
async def on_member_ban(member):
    if(startup_complete == True):
        await trigger_active_plugins(member.server,'member_ban',member)

@client.event
async def on_member_unban(member):
    if(startup_complete == True):
        await trigger_active_plugins(member.server,'member_unban',member)

async def find_user(server_obj=None,user_str=None,get_object=False):
    if(user_str != None and user_str != "" and server_obj != None):
        found_user = ''
        if("<@" in user_str):
            #value passed was a snowflake, reduce to user id number
            user_str = user_str.replace("<@!","<@")
            user_str = user_str.replace("<@","")
            user_str = user_str.replace(">","")
            found_user = user_str

        else:
            #value passed is a string, look in servers member list

            orig_user_str = user_str
            user_str = user_str.lower()

            chk_for_discrim = user_str.split("#")
            cfd_length = len(chk_for_discrim)
            if(cfd_length == 2):
                #discriminator was specified
                d_name = chk_for_discrim[0]
                d_disc = chk_for_discrim[1]
                get_member = discord.utils.find(lambda m: (m.name.lower() == d_name or m.display_name.lower() == d_name) and str(m.discriminator) == d_disc, server_obj.members)
            else:
                #no discriminator found, go off name alone
                get_member = discord.utils.find(lambda m: str(m.id) == user_str or m.name.lower() == user_str or m.display_name.lower() == user_str, server_obj.members)

            if(get_member != None):
                found_user = get_member.id
            else:
                #could not find user in members list, check the database
                use_server_id = hash_server_id(server_obj.id)
                find_user_db = db.cursor()
                if(cfd_length == 2):
                    #discriminator was specified, check users table
                    find_user_db.execute("SELECT * FROM users WHERE server_id=?",(use_server_id,))
                else:
                    #no discriminator found, check user alias table
                    find_user_db.execute("SELECT * FROM user_names WHERE server_id=?",(use_server_id,))

                user_id_db = ''
                find_user_count = 0
                for row in find_user_db:
                    if(cfd_length == 2):
                        #discriminator was specified, check users table
                        this_user_name = await decrypt_data(row['user_name'])
                        if(this_user_name.lower() == orig_user_str.lower()):
                            find_user_count = find_user_count + 1
                            user_id_db = await decrypt_data(row['stored_user_id'])
                            break
                    else:
                        #look for user alias
                        this_user_name = await decrypt_data(row['name'])
                        if(this_user_name.lower() == orig_user_str.lower()):
                            hashed_id = row['user_id']
                            find_hashed = db.cursor()
                            find_hashed.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(hashed_id,use_server_id,))
                            for hrow in find_hashed:
                                find_user_count = find_user_count + 1
                                user_id_db = await decrypt_data(hrow['stored_user_id'])

                        if(find_user_count >= 1): break


                if(find_user_count == 1 and user_id_db != ""):
                    found_user = user_id_db
                else: found_user = None

        if(found_user != None and found_user != ""):
            if(get_object == True):

                found_user_obj = discord.utils.find(lambda m: str(m.id) == str(found_user), server_obj.members)
                if(found_user_obj != None):
                    return found_user_obj
                else:
                    try:
                        found_user_obj = await client.get_user_info(found_user)
                    except: found_user_obj = False
                    return found_user_obj

            else: return found_user
        else: return False
    else: return False


async def last_invite_used(server):
    used_code = 'unknown'
    latest_invites = await get_server_invites(server)
    if(latest_invites == False): latest_invites = []
    found_code = False

    if(server.id in invite_list):

        #check for matching code with increased usage count
        for old_inv in invite_list[server.id]:
            for new_inv in latest_invites:
                if(old_inv.code == new_inv.code and old_inv.uses < new_inv.uses):
                    found_code = True
                    used_code = old_inv.code
                    break

        if(found_code == False):
            #check for code now removed
            for old_inv in invite_list[server.id]:
                code_exists = False
                for new_inv in latest_invites:
                    if(old_inv.code == new_inv.code): code_exists = True

                if(code_exists == False):
                    found_code = True
                    used_code = old_inv.code
                    break

        if(found_code == False):
            #check for code added since last update
            for new_inv in latest_invites:
                code_exists = False
                for old_inv in invite_list[server.id]:
                    if(old_inv.code == new_inv.code): code_exists = True

                if(code_exists == False):
                    found_code = True
                    used_code = new_inv.code
                    break

    invite_list[server.id] = latest_invites
    return used_code


async def user_update_db(context=None,user=None,server_obj=None):
    if(context != None and user != None and server_obj != None):

        '''
        CONTEXTS
        update - updated status or nickname
        join - user has joined the server
        leave - user has left the server
        start - bot startup looking for changes
        '''
        use_server_id = await hash_server_id(server_obj.id)
        use_member_id = await hash_member_id(server_obj.id,user.id)

        time_now = await current_timestamp()

        load_user = db.cursor()
        load_user.execute("SELECT * FROM users WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
        load_user_count = 0
        load_user_auth = ''
        for row in load_user:
            load_user_count = load_user_count + 1

        if(load_user_count == 0):
            #new user not seen before, create record
            if(verbose_out == True): await log_entry("Detected new user "+user.display_name+" / "+user.name+"#"+str(user.discriminator)+" ("+str(user.id)+") on server \""+server_obj.name+"\"",server_obj)

            save_mem_user_name = await encrypt_data(user.name+'#'+user.discriminator)
            save_mem_name = await encrypt_data(user.name)
            save_mem_id = await encrypt_data(user.id)

            new_user = db.cursor()
            new_user.execute("INSERT INTO users (server_id,user_id,stored_user_id,user_name) VALUES (?,?,?,?)",(use_server_id,use_member_id,save_mem_id,save_mem_user_name,))
            db.commit()

            new_name = db.cursor()
            new_name.execute("INSERT INTO user_names (server_id,user_id,name,datestamp) VALUES (?,?,?,?)",(use_server_id,use_member_id,save_mem_name,time_now,))
            db.commit()

        if(context == 'join'):
            inv_used = await last_invite_used(server_obj)
            save_inv_used = await encrypt_data(inv_used)
            new_user = db.cursor()
            new_user.execute("UPDATE users SET inv_used=? WHERE server_id=? AND user_id=?",(save_inv_used,use_server_id,use_member_id,))
            db.commit()



        check_nick = db.cursor()
        check_nick.execute("SELECT * FROM user_names WHERE user_id=? AND server_id=?",(use_member_id,use_server_id,))
        found_nick = False
        for row in check_nick:
            this_nick = await decrypt_data(row['name'])
            if(this_nick == user.display_name): found_nick = True

        if(found_nick == False):
            if(verbose_out == True): await log_entry("User "+str(user.id)+" current nick name \""+user.display_name+"\" does not exist in the database, adding it.",server_obj)
            save_mem_nick = await encrypt_data(user.display_name)
            new_name = db.cursor()
            new_name.execute("INSERT INTO user_names (user_id,name,datestamp,server_id) VALUES (?,?,?,?)",(use_member_id,save_mem_nick,time_now,use_server_id,))
            db.commit()


async def user_last_seen(server,member):
    use_server_id = await hash_server_id(server.id)
    use_member_id = await hash_member_id(server.id,member.id)
    time_now = await current_timestamp()
    time_now = int(time_now)
    save_seen = db.cursor()
    save_seen.execute("UPDATE users SET last_seen=? WHERE user_id=? AND server_id=?",(time_now,use_member_id,use_server_id))
    db.commit()


#===================================================================================================================
#Channel functions

@client.event
async def on_group_join(channel,user):
    if(startup_complete == True):
        await trigger_active_plugins(channel.server,'group_join',channel,user)

@client.event
async def on_group_remove(channel,user):
    if(startup_complete == True):
        await trigger_active_plugins(channel.server,'group_remove',channel,user)

@client.event
async def on_channel_create(channel):
    if(startup_complete == True):
        if(channel.is_private == False):
            await channel_update_db('new',channel)
            await trigger_active_plugins(channel.server,'channel_create',channel)

@client.event
async def on_channel_delete(channel):
    if(startup_complete == True):
        if(channel.is_private == False):
            await channel_update_db('delete',channel)
            await trigger_active_plugins(channel.server,'channel_delete',channel)

@client.event
async def on_channel_update(old_channel,new_channel):
    if(startup_complete == True):
        if(new_channel.is_private == False):
            await channel_update_db('update',new_channel)
            await trigger_active_plugins(old_channel.server,'channel_update',old_channel,new_channel)


async def channel_id_from_name(server_obj=None,channel_name=None,channel_type='text'):
    if(server_obj != None and channel_name != None):
        find_channel = discord.utils.find(lambda m: m.name.lower() == channel_name.lower() and str(m.type) == channel_type, server_obj.channels)
        if(find_channel == None):
            return False
        else:
            return find_channel.id
    else:
        return False


async def channel_name_from_id(server_obj=None,channel_id=None,get_object=False):
    if(server_obj != None and channel_id != None):
        find_channel = discord.utils.find(lambda m: m.id == channel_id, server_obj.channels)
        if(find_channel == None):
            return False
        else:
            if(get_object == True):
                return find_channel
            else:
                return find_channel.name


async def find_channel_arg(server_obj=None,channel_arg=None,get_obj=False):
    if(server_obj != None and channel_arg != None):
        found_channel = False

        if('<#' in channel_arg):
            #argument is a channel snowflake
            found_channel = channel_arg
            found_channel = found_channel.replace('<#','')
            found_channel = found_channel.replace('>','')
        else:
            #argument is a string
            found_channel = await channel_id_from_name(server_obj,channel_arg)

        if(found_channel != False and get_obj == True):
            found_channel = await channel_name_from_id(server_obj,found_channel,True)

        return found_channel


async def bot_use_channel(server=None,plugin='bot',channel_name='log_channel'):
    if(server != None):
        use_channel = False
        channel_dir = await get_config('channel_dir',server,plugin)
        if(channel_dir != False):
            if(channel_name not in channel_dir):
                channel_dir = False
            else:
                find_channel_obj = await find_channel_arg(server,'<#'+channel_dir[channel_name]+'>',True)
                if(find_channel_obj == False): channel_dir = False

        if(channel_dir == False):
            channel_name = 'log_channel'
            channel_dir = await get_config('channel_dir',server,'bot')
            if(channel_dir != False):
                if(channel_name not in channel_dir):
                    channel_dir = False
                else:
                    find_channel_obj = await find_channel_arg(server,'<#'+channel_dir[channel_name]+'>',True)
                    if(find_channel_obj == False): channel_dir = False

        if(channel_dir != False):
            return find_channel_obj
        else: return server.owner
    else: return False


async def bot_set_channel(server=None,plugin=None,channel_name=None,new_val=False):
    if(server != None and plugin != None and channel_name != None):
        channel_dir = await get_config('channel_dir',server,plugin)
        if(channel_dir == False): channel_dir = {}
        channel_dir[channel_name] = new_val
        await set_config('channel_dir',server,plugin,channel_dir)
        return True
    else: return False



async def channel_update_db(context=None,channel=None):
    if(context != None and channel != None and channel.is_private == False):

        '''
        CONTEXTS
        update - updated details
        new - new channel created
        delete - channel deleted
        start - bot startup update
        '''
        use_server_id = await hash_server_id(channel.server.id)
        use_channel_id = await hash_member_id(channel.server.id,channel.id)

        time_now = await current_timestamp()
        chan_type = 'unknown'
        if(str(channel.type) == "text"): chan_type = "text"
        if(str(channel.type) == "voice"): chan_type = "voice"

        load_chan = db.cursor()
        load_chan.execute("SELECT * FROM channels WHERE channel_id=? AND server_id=?",(use_channel_id,use_server_id,))
        load_chan_count = 0
        load_chan_name = ''
        for row in load_chan:
            load_chan_count = load_chan_count + 1
            load_chan_name = await decrypt_data(row['name'])

        if(load_chan_count == 0):
            #new channel not seen before, create record
            if(verbose_out == True): await log_entry("New "+chan_type+" channel \""+channel.name+"\" detected on server \""+channel.server.name+"\"",channel.server)
            if(context == "delete"):
                chan_del = time_now
            else:
                chan_del = 0

            save_chan_type = await encrypt_data(chan_type)
            save_chan_name = await encrypt_data(channel.name)
            save_chan_id = await encrypt_data(channel.id)

            new_chan = db.cursor()
            new_chan.execute("INSERT INTO channels (server_id,stored_channel_id,channel_id,name,type,deleted) VALUES (?,?,?,?,?,?)",(use_server_id,save_chan_id,use_channel_id,save_chan_name,save_chan_type,chan_del,))
            db.commit()

        else:
            #channel record already exists
            if(load_chan_name != channel.name or context == "delete"):
                save_chan_name = await encrypt_data(channel.name)

                if(context == "delete"):
                    chan_del = time_now
                    if(verbose_out == True): await log_entry("Detected deletion of "+chan_type+" channel \""+channel.name+"\" on server \""+channel.server.name+"\"",channel.server)
                else:
                    chan_del = 0
                    if(verbose_out == True): await log_entry("Detected channel name change from \""+load_chan_name+"\" to \""+channel.name+"\" on server \""+channel.server.name+"\"",channel.server)

                upd_chan = db.cursor()
                upd_chan.execute("UPDATE channels SET name=?, deleted=? WHERE channel_id=? AND server_id=?",(save_chan_name,chan_del,use_channel_id,use_server_id,))
                db.commit()

#===================================================================================================================
#Setting functions

async def get_config(get_field=None,server_obj=None,plugin='bot'):
    if(get_field != None and server_obj != None):
        if(plugin in config[server_obj.id] and get_field in config[server_obj.id][plugin]):
            if(config[server_obj.id][plugin][get_field] != None and config[server_obj.id][plugin][get_field] != ""):
                return config[server_obj.id][plugin][get_field]
            else: return False
        else: return False

async def set_config(get_field=None,server_obj=None,plugin='bot',new_val=None):
    if(get_field != None and server_obj != None and new_val != None):
        if(plugin not in config[server_obj.id]): config[server_obj.id][plugin] = {}
        config[server_obj.id][plugin][get_field] = new_val
        save_config = await encrypt_data(json.dumps(config[server_obj.id]))

        use_server_id = await hash_server_id(server_obj.id)

        cfdb = db.cursor()
        cfdb.execute("UPDATE servers SET settings=? WHERE server_id=?",(save_config,use_server_id,))
        db.commit()


async def setting_change(message):
    if(message != None):
        proc_msg = await get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)
        if(proc_msg_length >= 3):

            if(proc_msg[1] == "mod_role"): await setting_change_role('mod_role','mod role',message)
            if(proc_msg[1] == "mod_channel"): await setting_change_channel('mod_channel','mod channel',message)



#===================================================================================================================
#Help functions

async def help_menu(message):
    member_of = await get_user_groups(message.server,message.author.id)
    if('members' in member_of):
        proc_msg = await get_cmd_args(message.content)
        proc_msg_length = len(proc_msg)

        build_help = {}

        build_help['bot'] = {}
        build_help['bot']['menu'] = await bot_help_menu()
        build_help['bot']['sections'] = await bot_help_section()

        for plugin in plugins:
            plg_active = await is_plugin(message.server,plugin)
            if(plg_active == True):
                build_help[plugin] = {}
                build_help[plugin]['menu'] = await trigger_active_plugin(message.server,'help_menu',plugin)
                build_help[plugin]['sections'] = await trigger_active_plugin(message.server,'help_section',plugin)


        if(proc_msg_length >= 2):
            #load a command menu
            icon_url = client.user.avatar_url
            if(icon_url == None or icon_url == ""): icon_url = client.user.default_avatar_url

            if(proc_msg[1] in build_help):

                em = discord.Embed(title=build_help[proc_msg[1]]['menu']['title'], description=build_help[proc_msg[1]]['menu']['description'], colour=3447003)
                em.set_author(name=client.user.display_name, icon_url=icon_url)
                to_show = False

                for cmd in build_help[proc_msg[1]]['sections']:

                    if(cmd.endswith('_continued') == True):
                        use_cmd = cmd.replace("_continued","")
                    else: use_cmd = cmd

                    sub_perms_present = False
                    for cmd_entry in build_help[proc_msg[1]]['sections'][cmd]:
                        if(cmd_entry['perm_name'] != ""): sub_perms_present = True

                    if(sub_perms_present == False): chk_global_perm = await has_perm_to_run(message.server,None,message.author.id,proc_msg[1],None,False)

                    if(sub_perms_present == True or chk_global_perm == True):
                        build_cmd_list = ''
                        for cmd_entry in build_help[proc_msg[1]]['sections'][cmd]:

                            if(cmd_entry['perm_name'] == ""):
                                chk_sub_perm = True
                            else: chk_sub_perm = await has_perm_to_run(message.server,None,message.author.id,proc_msg[1],cmd_entry['perm_name'],False)

                            if(chk_sub_perm == True):
                                to_show = True
                                if(cmd_entry['command'] != ""): cmd_entry['command'] = ' '+cmd_entry['command']
                                build_cmd_list = build_cmd_list+'**'+bot_cmd_char+use_cmd+cmd_entry['command']+'** '+cmd_entry['args']+'\n'+cmd_entry['description']+'\n\n'

                        if(cmd.endswith('_continued') == True):
                            use_title = use_cmd.capitalize()+' (continued)'
                        else: use_title = use_cmd.capitalize()

                        em.add_field(name='__**'+use_title+'**__',value=build_cmd_list,inline=False)

                if(to_show == True):await client.send_message(message.author, embed=em)

            else: await client.send_message(message.author,'Sorry <@'+message.author.id+'>, I couldn\'t find a help section called "'+proc_msg[1]+'".')


        else:
            #load the main menu
            icon_url = client.user.avatar_url
            if(icon_url == None or icon_url == ""): icon_url = client.user.default_avatar_url

            em = discord.Embed(title='Help main menu', description='Here is a list of all the help sections', colour=3447003)
            em.set_author(name=client.user.display_name, icon_url=icon_url)
            to_show = False

            for plg in build_help:

                show_section = False
                for cmd in build_help[plg]['sections']:
                    sub_perms_present = False
                    for cmd_entry in build_help[plg]['sections'][cmd]:
                        if(cmd_entry['perm_name'] != ""): sub_perms_present = True
                    if(sub_perms_present == False): chk_global_perm = await has_perm_to_run(message.server,None,message.author.id,plg,None,False)
                    if(sub_perms_present == True or chk_global_perm == True):
                        for cmd_entry in build_help[plg]['sections'][cmd]:
                            if(cmd_entry['perm_name'] == ""):
                                chk_sub_perm = True
                            else: chk_sub_perm = await has_perm_to_run(message.server,None,message.author.id,plg,cmd_entry['perm_name'],False)
                            if(chk_sub_perm == True): show_section = True

                if(show_section == True):
                    to_show = True
                    em.add_field(name=build_help[plg]['menu']['title'],value=build_help[plg]['menu']['description']+'\n_To view this help section run_ `'+bot_cmd_char+'help '+plg+'`',inline=False)

            if(to_show == True): await client.send_message(message.author, embed=em)



#===================================================================================================================
#Task clock

async def remove_server_tasks(server_obj):
    task_list_length = len(tasklist)
    if(task_list_length > 0):
        task_list_length = task_list_length - 1
        tl_run = 0
        while(tl_run <= task_list_length):
            if(tasklist[tl_run]['server'] == server_obj):
                del tasklist[tl_run]
                task_list_length = len(tasklist) - 1
            tl_run = tl_run + 1

    if(verbose_out == True): await log_entry('Removed all pending tasks for '+server_obj.name,server_obj)


async def add_task(server_obj=None,trig_time=None,trig_plugin='bot',trig_func=None,arg_obj={}):
    if(trig_time != None and trig_func != None):
        tasklist_len = len(tasklist)
        add_task = True

        if(tasklist_len > 0):
            for task in tasklist:
                if(task['plugin'] == trig_plugin and task['func'] == trig_func and task['arg'] == arg_obj and task['server'] == server_obj): add_task = False

        if(add_task == True):
            #await log_entry("Adding task "+trig_func+" to task clock, recall time "+str(trig_time))
            tasklist.append({'time': trig_time,'plugin': trig_plugin,'func': trig_func,'arg': arg_obj,'server': server_obj})
        #else: print("Adding task "+trig_func+" failed because it is already in the queue.")


async def task_clock():
    await client.wait_until_ready()
    while not client.is_closed:
        time_now = await current_timestamp()
        task_list_length = len(tasklist)
        if(task_list_length > 0):
            task_list_length = task_list_length - 1
            tl_run = 0
            while(tl_run <= task_list_length):
                if(tasklist[tl_run]['time'] <= time_now):
                    call_plugin = tasklist[tl_run]['plugin']
                    call_func = tasklist[tl_run]['func']
                    call_arg = tasklist[tl_run]['arg']
                    call_server = tasklist[tl_run]['server']
                    #print("Task "+call_func+" is due, triggering it now.")
                    del tasklist[tl_run]
                    task_list_length = len(tasklist) - 1
                    if(call_plugin == "bot"):
                        await globals()[call_func](call_server,call_arg)
                    else:
                        await trigger_active_plugin(call_server,call_func,call_plugin,call_server,call_arg)
                tl_run = tl_run + 1

        await asyncio.sleep(10)

#===================================================================================================================
#ROLE FUNCTIONS

@client.event
async def on_server_role_create(role):
    if(startup_complete == True):
        await trigger_active_plugins(role.server,'role_create',role)

@client.event
async def on_server_role_delete(role):
    if(startup_complete == True):
        await trigger_active_plugins(role.server,'role_delete',role)

@client.event
async def on_server_role_update(before,after):
    if(startup_complete == True):
        await trigger_active_plugins(before.server,'role_update',before,after)


async def has_role(user_id=None,role_id=None,server_obj=None):
    if(user_id != None and role_id != None and server_obj != None):
        get_member = discord.utils.find(lambda m: m.id == user_id, server_obj.members)
        if(get_member != None):
            find_role = discord.utils.find(lambda m: m.id == role_id, get_member.roles)
            if(find_role != None):
                return True
            else: return False
        else: return False
    else: return False


async def find_role_arg(server_obj,role_name):
    if(role_name != None and server_obj != None):
        role_name = role_name.lower()
        basic_role = await role_id_from_name(role_name,server_obj)
        if(basic_role == False):
            rn_max_ind = len(role_name) - 1
            found_roles = []

            for this_role in server_obj.roles:
                this_role_name = this_role.name.lower()
                cr_run = 0
                match_count = 0
                while(cr_run <= rn_max_ind):
                    this_char = role_name[cr_run]

                    two_chars_found = True
                    if(cr_run > 0):
                        last_run = cr_run - 1
                        last_char = role_name[last_run]
                        two_chars = last_char+this_char
                        if(two_chars not in this_role_name): two_chars_found = False

                    if(this_char in this_role_name and two_chars_found): match_count = match_count + 1
                    cr_run = cr_run + 1

                add_eval = {}
                add_eval['match'] = ((match_count / len(this_role_name)) + (match_count / len(role_name))) / 2
                add_eval['id'] = this_role.id
                #print(this_role_name+' '+str(add_eval['match']))
                if(add_eval['match'] >= 0.1): found_roles.append(add_eval)

            if(len(found_roles) > 0):
                last_max = 0
                max_id = False
                for this_found in found_roles:
                    if(this_found['match'] > last_max):
                        max_id = this_found['id']
                        last_max = this_found['match']
                return max_id
            else: return False
        else: return basic_role
    else:
        return False

async def role_id_from_name(role_name=None,server_obj=None):
    if(role_name != None and server_obj != None):
        find_role = discord.utils.find(lambda m: m.name.lower() == role_name.lower(), server_obj.roles)
        if(find_role == None):
            return False
        else:
            return find_role.id
    else:
        return False

async def role_name_from_id(role_id=None,server_obj=None):
    if(role_id != None and server_obj != None):
        role_id = str(role_id)
        find_role = discord.utils.find(lambda m: m.id == role_id, server_obj.roles)
        if(find_role == None):
            return False
        else:
            return find_role.name

async def user_add_role(user_id=None,role_id=None,server_obj=None):
    if(user_id != None and role_id != None and server_obj != None):
        get_member = discord.utils.find(lambda m: m.id == user_id, server_obj.members)
        role_id = str(role_id)
        find_role = discord.utils.find(lambda m: m.id == role_id, server_obj.roles)
        if(find_role == None):
            return False
        else:
            await client.add_roles(get_member,find_role)
            return True

async def user_remove_role(user_id=None,role_id=None,server_obj=None):
    if(user_id != None and role_id != None and server_obj):
        get_member = discord.utils.find(lambda m: m.id == user_id, server_obj.members)
        role_id = str(role_id)
        find_role = discord.utils.find(lambda m: m.id == role_id, server_obj.roles)
        if(find_role == None):
            return False
        else:
            await client.remove_roles(get_member,find_role)
            return True

#===================================================================================================================
#Misc system functions


async def attachment_file_type(embed=None):
    if(embed != None):
        file_name = embed['filename'].lower()
        file_type = 'unknown'
        if(file_name.endswith('.jpg') == True): file_type = 'image'
        if(file_name.endswith('.jpeg') == True): file_type = 'image'
        if(file_name.endswith('.png') == True): file_type = 'image'
        if(file_name.endswith('.gif') == True): file_type = 'image'

        return file_type


async def create_alert(server_obj=None,alert_role_id=None,append_str=""):
    mod_list = ''
    if(server_obj != None and alert_role_id != None and alert_role_id != False):
        role_exists = await role_name_from_id(alert_role_id,server_obj)
        if(role_exists != False):
            for member in server_obj.members:
                chk_for_role = await has_role(member.id,alert_role_id,server_obj)
                if(chk_for_role == True):
                    if(str(member.status) == "online" or str(member.status) == "idle"):
                        if(mod_list != ""): mod_list = mod_list+', '
                        mod_list = mod_list+'<@'+member.id+'>'

            mod_role = await get_config('mod_role',server_obj)

            if(mod_list == ""): mod_list = '<@&'+alert_role_id+'>'
            mod_list = '**Alert ('+mod_list+')**\n'+append_str

    return mod_list


async def convert_seconds_to_time_string(seconds=0):
    seconds = int(seconds)
    seconds = math.ceil(seconds)
    time_str = ''

    unit_time = 31536000
    unit_name = 'year(s)'
    if(seconds >= unit_time):
        if(time_str != ""): time_str = time_str+' '
        this_unit = math.floor(seconds / unit_time)
        seconds = seconds - (this_unit * unit_time)
        time_str = time_str+str(this_unit)+' '+unit_name

    unit_time = 2592000
    unit_name = 'month(s)'
    if(seconds >= unit_time):
        if(time_str != ""): time_str = time_str+' '
        this_unit = math.floor(seconds / unit_time)
        seconds = seconds - (this_unit * unit_time)
        time_str = time_str+str(this_unit)+' '+unit_name

    unit_time = 604800
    unit_name = 'week(s)'
    if(seconds >= unit_time):
        if(time_str != ""): time_str = time_str+' '
        this_unit = math.floor(seconds / unit_time)
        seconds = seconds - (this_unit * unit_time)
        time_str = time_str+str(this_unit)+' '+unit_name

    unit_time = 86400
    unit_name = 'day(s)'
    if(seconds >= unit_time):
        if(time_str != ""): time_str = time_str+' '
        this_unit = math.floor(seconds / unit_time)
        seconds = seconds - (this_unit * unit_time)
        time_str = time_str+str(this_unit)+' '+unit_name

    unit_time = 3600
    unit_name = 'hour(s)'
    if(seconds >= unit_time):
        if(time_str != ""): time_str = time_str+' '
        this_unit = math.floor(seconds / unit_time)
        seconds = seconds - (this_unit * unit_time)
        time_str = time_str+str(this_unit)+' '+unit_name

    unit_time = 60
    unit_name = 'minute(s)'
    if(seconds >= unit_time):
        if(time_str != ""): time_str = time_str+' '
        this_unit = math.floor(seconds / unit_time)
        seconds = seconds - (this_unit * unit_time)
        time_str = time_str+str(this_unit)+' '+unit_name

    unit_time = 1
    unit_name = 'second(s)'
    if(seconds >= unit_time):
        if(time_str != ""): time_str = time_str+' '
        this_unit = math.floor(seconds / unit_time)
        seconds = seconds - (this_unit * unit_time)
        time_str = time_str+str(this_unit)+' '+unit_name

    return time_str


async def cmd_time_args(time_int=None,time_scale=None):
    if(time_int != None and time_scale != None):

        use_time_scale = ''
        time_int = int(time_int)

        if(time_scale == "sec" or time_scale == "secs" or time_scale == "second" or time_scale == "seconds"): use_time_scale = 'secs'
        if(time_scale == "min" or time_scale == "mins" or time_scale == "minute" or time_scale == "minutes"): use_time_scale = 'mins'
        if(time_scale == "hour" or time_scale == "hours"): use_time_scale = 'hours'
        if(time_scale == "day" or time_scale == "days"): use_time_scale = 'days'
        if(time_scale == "week" or time_scale == "weeks"): use_time_scale = 'weeks'
        if(time_scale == "month" or time_scale == "months"): use_time_scale = 'months'
        if(time_scale == "year" or time_scale == "years"): use_time_scale = 'years'
        if(use_time_scale != ""):
            time_modif = 0;
            if(use_time_scale == "secs"): time_modif = 1
            if(use_time_scale == "mins"): time_modif = 60
            if(use_time_scale == "hours"): time_modif = 60 * 60
            if(use_time_scale == "days"): time_modif = (60 * 60) * 24
            if(use_time_scale == "weeks"): time_modif = ((60 * 60) * 24) * 7
            if(use_time_scale == "months"): time_modif = ((60 * 60) * 24) * 30
            if(use_time_scale == "years"): time_modif = ((60 * 60) * 24) * 365
            time_calc = time_int * time_modif
            return time_calc
        else: return False;

async def get_cmd_char(server_obj=None):
    if(server_obj != None):
        check_ov = await get_config('cmd_char',server_obj,'bot')
    else: check_of = False

    if(check_ov == False):
        return bot_cmd_char
    else: return check_ov

async def get_cmd_args(cmd_str=None,limit=None):
    #limit 3 gets first three arguments and returns rest of string as single argument
    if(cmd_str != None):
        if(limit != None): limit = limit - 1
        build_args = {}
        ba_run = 0
        cmd_str = '#^#'+cmd_str
        work_cmd = cmd_str.replace('#^#'+bot_cmd_char,"")
        trim_cmd = work_cmd

        cs_len = len(work_cmd) - 1
        cs_run = 0
        this_arg = ''
        open_quote = False
        open_double = False
        open_single = False
        while(cs_run <= cs_len):
            #if(work_cmd[cs_run] == ' ' or work_cmd[cs_run] == '"' or work_cmd[cs_run] == "'"):
            add_char = True

            if(work_cmd[cs_run] == "'"):
                if(open_quote == False):
                    open_quote = True
                    open_single = True
                    add_char = False
                elif(open_single == True):
                    build_args[ba_run] = this_arg
                    ba_run = ba_run + 1
                    trim_cmd = '#^#'+trim_cmd
                    trim_cmd = trim_cmd.replace("#^#'"+this_arg+"'",'')
                    this_arg = ''
                    open_quote = False
                    open_single = False
                    add_char = False
                    #cs_run = cs_run + 1
            elif(work_cmd[cs_run] == '"'):
                if(open_quote == False):
                    open_quote = True
                    open_double = True
                    add_char = False
                elif(open_double == True):
                    build_args[ba_run] = this_arg
                    ba_run = ba_run + 1
                    trim_cmd = '#^#'+trim_cmd
                    trim_cmd = trim_cmd.replace('#^#"'+this_arg+'"','')
                    this_arg = ''
                    open_quote = False
                    open_double = False
                    add_char = False
                    #cs_run = cs_run + 1
            elif(work_cmd[cs_run] == " " and open_quote == False):
                if(len(this_arg) > 0):
                    build_args[ba_run] = this_arg
                    ba_run = ba_run + 1
                    trim_cmd = '#^#'+trim_cmd
                    trim_cmd = trim_cmd.replace('#^#'+this_arg+' ','')
                    this_arg = ''
                else:
                    trim_cmd = '#^#'+trim_cmd
                    trim_cmd = trim_cmd.replace('#^# ','')

                add_char = False


            if(add_char == True):
                this_arg = this_arg+str(work_cmd[cs_run])

            if(limit == None or ba_run <= limit):
                cs_run = cs_run + 1
                if(cs_run > cs_len):
                    build_args[ba_run] = this_arg
                    ba_run = ba_run + 1
            else:
                #if(trim_cmd != None and len(trim_cmd) > 0): build_args[ba_run] = trim_cmd
                build_args[ba_run] = trim_cmd
                cs_run = cs_len + 1

        return build_args


async def timestamp_to_date(timestamp=None,hour_break=False):
    if(timestamp != None):
        if(hour_break == True):
            h_break = '\n'
        else: h_break = ' '
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%a %d %b %Y'+h_break+'%H:%M UTC 0')
    else: return False

async def timestamp_to_date_short(timestamp=None):
    if(timestamp != None):
        return datetime.datetime.fromtimestamp(int(timestamp)).strftime('%d %b %Y %H:%M:%S')
    else: return False

async def current_timestamp():
    time_now = datetime.datetime.now().timestamp()
    time_now = int(time_now)
    if(utc_time_modifier != 0): time_now = time_now + utc_time_modifier
    return time_now


async def log_entry(message=None,server_obj=None):
    if(message != None):
        #message = message.decode("ascii","ignore")
        date_stamp = await current_timestamp()
        date_stamp = await timestamp_to_date_short(date_stamp)
        date_stamp = '['+date_stamp+'] '
        message = date_stamp+message
        message = message.encode("utf-8").decode("ascii","ignore")
        print(message)


async def async_check_internet():
    await log_entry("Checking internet connection...\n")
    hostname = "google.com"
    if os.name != "nt":
        response = os.system("ping -c 1 " + hostname)
    else:
        response = os.system("ping -n 1 " + hostname)
    if(response == 0):
        await log_entry("\nInternet connection is active\n")
        return True
    else:
        await log_entry("\nInternet connection failure\n")
        return False

def check_internet():
    print("Checking internet connection...\n")
    hostname = "google.com"
    if os.name != "nt":
        response = os.system("ping -c 1 " + hostname)
    else:
        response = os.system("ping -n 1 " + hostname)
    if(response == 0):
        print("\nInternet connection is active\n")
        return True
    else:
        print("\nInternet connection failure\n")
        return False


async def set_status(stat=None,playing_ov=None):

    playing_now = bot_playing_tag
    if(playing_ov != None): playing_now = playing_ov
    if(playing_now != None and playing_now != ""):
        playing = discord.Game(name=playing_now)
    else:
        playing = None

    if(stat != None):
        if(stat == "dnd"): stat = discord.Status.dnd
        if(stat == "online"): stat = None
        if(stat == "idle"): stat = discord.Status.idle
        if(stat == "offline" or stat == "invisible"): stat = discord.Status.invisible

    await client.change_presence(game=playing,status=stat)

#===================================================================================================================
#Startup bot

print('\nStarted Kit10 Discord Bot by Kieron "madmachinations" O\'Brien.')
print('Version '+bot_version)
print('https://github.com/madmachinations/kit10_discord_bot\n')

print("Checking encryption...")
chk_enc_start = enc_startup()
if(chk_enc_start == True):

    print("\nAccessing DB: "+db_path+"\n")
    print("Comparing database schematic with database structure")
    dbschema_file = open(bot_abs_path+'dbschema','r')
    dbschema = json.loads(dbschema_file.read())
    dbschema_file.close()
    if(len(dbschema) > 0):

        exist_schema = {}
        deleted_cols = {}
        get_tables = db.cursor()
        get_tables.execute("SELECT * FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'")
        for dbtab in get_tables:
            exist_schema[dbtab['name']] = {}
            deleted_cols[dbtab['name']] = {}
            get_cols = db.cursor()
            get_cols.execute("pragma table_info("+dbtab['name']+")")
            for col in get_cols:
                exist_schema[dbtab['name']][col[1]] = {}
                exist_schema[dbtab['name']][col[1]]['type'] = col[2]
                exist_schema[dbtab['name']][col[1]]['null'] = col[3]
                exist_schema[dbtab['name']][col[1]]['def'] = col[4]
                exist_schema[dbtab['name']][col[1]]['pk'] = col[5]

        for table in exist_schema:
            if(table in dbschema):
                for col in exist_schema[table]:
                    if(col in dbschema[table]):
                        del dbschema[table][col]
                    else:
                        print("Delete column "+table+"."+col+" from database")
                        other_cols = ''
                        for othcol in exist_schema[table]:
                            if(othcol != col and othcol not in deleted_cols[table]):
                                if(other_cols != ""): other_cols = other_cols+", "
                                other_cols = other_cols+othcol

                        adj_db = db.cursor()
                        adj_db.execute("CREATE TABLE "+table+"_backup AS SELECT "+other_cols+" FROM "+table)
                        adj_db.execute("DROP TABLE "+table)
                        adj_db.execute("ALTER TABLE "+table+"_backup RENAME TO "+table)
                        db.commit()
                        deleted_cols[table][col] = {}

                if(len(dbschema[table]) > 0):
                    for col in dbschema[table]:
                        print("Add column "+table+"."+str(col)+" to database")

                        if(dbschema[table][col]['type'] == "text"):
                            use_type = ' TEXT'
                        else: use_type = ' INTEGER'

                        if(dbschema[table][col]['null'] == False):
                            use_null = ' NOT NULL'
                        else: use_null = ''

                        if(dbschema[table][col]['def'] != None and dbschema[table][col]['def'] != ""):
                            use_def = dbschema[table][col]['def']
                            if(use_type == " INTEGER"):
                                use_def = " DEFAULT "+str(use_def)
                            else:
                                use_def = " DEFAULT '"+str(use_def)+"'"
                        else: use_def = ''

                        if(dbschema[table][col]['pk'] == True):
                            use_pk = ' PRIMARY KEY'
                            if(dbschema[table][col]['ai'] == True): use_pk = use_pk+' AUTOINCREMENT'
                        else: use_pk = ''

                        adj_db = db.cursor()
                        adj_db.execute("ALTER TABLE "+table+" ADD "+str(col)+use_type+use_null+use_def+use_pk)
                        db.commit()

                del dbschema[table]

            else:
                print("Delete table "+table+" from database");
                adj_db = db.cursor()
                adj_db.execute("DROP TABLE "+table)
                db.commit()

        if(len(dbschema) > 0):
            for table in dbschema:
                print("Add table "+table+" to database")

                create_table = ''

                for col in dbschema[table]:

                    if(dbschema[table][col]['type'] == "text"):
                        use_type = ' TEXT'
                    else: use_type = ' INTEGER'

                    if(dbschema[table][col]['null'] == False):
                        use_null = ' NOT NULL'
                    else: use_null = ''

                    if(dbschema[table][col]['def'] != None and dbschema[table][col]['def'] != ""):
                        use_def = dbschema[table][col]['def']
                        if(use_type == " INTEGER"):
                            use_def = " DEFAULT "+str(use_def)
                        else:
                            use_def = " DEFAULT '"+str(use_def)+"'"
                    else: use_def = ''

                    if(dbschema[table][col]['pk'] == True):
                        use_pk = ' PRIMARY KEY'
                        if(dbschema[table][col]['ai'] == True): use_pk = use_pk+' AUTOINCREMENT'
                    else: use_pk = ''

                    if(create_table != ""): create_table = create_table+', '
                    create_table = create_table+col+use_type+use_null+use_def+use_pk
                    print("Add column "+table+"."+str(col)+" to database")

                adj_db = db.cursor()
                adj_db.execute("CREATE TABLE "+table+" ("+create_table+")")
                db.commit()

        del dbschema
        del exist_schema
        del deleted_cols



        network_active = check_internet()
        if(network_active == True):
            if(bot_token != None and bot_token != ""):
                print("Connecting to Discord...")
                client.loop.create_task(task_clock())
                client.run(bot_token)
            else: print("Error, no bot token specified")
        else: print("Internet connection appears to be down")
    else: print("Error, DB schematic file is missing or empty")
else: print("An encryption error occurred.")
