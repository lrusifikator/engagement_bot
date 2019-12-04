#!/usr/bin/python
import logging
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)
import telegram
import mysql.connector

from threading import Thread
import signal

import time
import datetime
import requests
import sys

from eng_bot.bot_settings import botname, insta_login, insta_pass, telegram_token
from eng_bot.bot_settings import DX, error_rate, warning_time, warnings_for_ban
from eng_bot.bot_settings import local_add_insctuction, get_list_inctruciton
from eng_bot.bot_settings import bot_admin_instruction, instruction_continue, start_message
from eng_bot.bot_settings import mysql_host, mysql_user, mysql_passwd
from eng_bot.bot_db import tables as db_tables

import eng_bot.insta as insta
import eng_bot.bot_db as bot_db

updater = Updater(token=telegram_token, use_context=True);
dispatcher = updater.dispatcher;
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
				level=logging.INFO);

pseudo_context = telegram.ext.callbackcontext.CallbackContext(dispatcher);

conn = mysql.connector.connect(
  host=mysql_host,
  user=mysql_user,
  passwd=mysql_passwd
)

db = conn.cursor();
if (db):
	print("Connected to the MySQL server")
else:
	print("Faild to connect to the MySQL server")

session = insta.insta_session(insta_login, insta_pass);
bot_db.set_db(db, db_tables);

#----------------------------------------------------------------------------------------------------------------#

def initial_lists():
	global main_lst, ban_lst, debtors, likes, done, sent_lst;
	global bot_db, db;

	main_lst = bot_db.get_main_lst(db); # [user_id, link]					
	debtors = bot_db.get_debtors(db);   # [user_id, debt]										
	ban_lst = bot_db.get_ban_lst(db) 	# [user_id, warnings, ban_start]
	likes =	bot_db.get_likes(db);     	# user_id : 'likes'
	done = bot_db.get_done(db);      	# link : [user_id_1, user_id_2, user_id_3, ... , user_id_DX] 		
	sent_lst = bot_db.get_sent_lst(db);	# user_id : [[link, likes], [link, likes], ...], datetime.now()
	
lst_index = 0;	
initial_lists();

backup_functoins = {
	bot_db.set_main_lst:main_lst,  
	bot_db.set_likes:likes, 
	bot_db.set_debtors:debtors, 
	bot_db.set_ban_lst:ban_lst, 
	bot_db.set_done:done, 
	bot_db.set_sent_lst:sent_lst
}
	
#----------------------------------------------------------------------------------------------------------------#

def get_likes_number(link):
	global session
	answ = insta.get_likes_number(session, link);	
	if(answ == -1):
		if(insta.is_instalink(link)):
			session.close();
			session = insta.insta_session(insta_login, insta_pass);
			return insta.get_likes_number(session, link);

	return answ

def drop_lists():
	global main_lst, ban_lst, debtors, likes, done, sent_lst;
	main_lst = [];
	debtors = [];
	ban_lst = [];
	likes = {};
	done = {};
	sent_lst = {};

def get_cur_time():
	return datetime.datetime.now().strftime('%y-%m-%d %H:%M:%S');

def form_list(msg, lst):
	msg += "\n";
	i = 1;
	for x in lst: 
		msg += str (i) + ") "+ str(x[0]) + "\n";
		i += 1;
	return msg;

def is_dx(mess):
	if(not ' ' in mess):
		return 0;
	dx = mess[0:mess.find(' ')]
	if(dx == "DX" + str(DX) or dx == "dx" + str(DX) or dx == "Dx" + str(DX) or dx == "dX" + str(DX)):
		return 1;
	return 0;

def has_list(user_id):
	global sent_lst;
	try: 
		sent_lst[user_id]
		return 1
	except:
		return 0;

def dct_sum(dct, ind, val):	
	try: 
		tmp = dct[ind] ;
		val += int(tmp);
		dct[ind] = str(val)
	except KeyError:
		dct[ind] = str(val);
	return val;

def get_list(user_id, get_likes_number = get_likes_number): 
	global main_lst;
	global lst_index;
	global sent_lst;
	global likes;
	global session;

	dct_sum(likes, user_id, 0);

	try:
		return sent_lst[user_id][0];
	except:
		pass;

	ret = []
	counter = 0;
	main_copy =  main_lst[lst_index:] + main_lst[0:lst_index];
	
	for x in main_copy:
		if(lst_index >= len(main_lst)):
			lst_index = 0;

		if(counter >= DX):
			break;
		try:
			if(user_id in done[x[1]]):
				in_done = 1;
			else:
				in_done = 0;
		except:
			in_done = 0;
	
		if(x[0] == user_id or in_done):
			lst_index += 1;
			continue;
		else:
			likes_number = get_likes_number(x[1]);
			if(likes_number == -1):
				continue
			ret.append([x[1], likes_number]);
		counter += 1
		lst_index += 1

	if(ret == []):
		return [];
	sent_lst[user_id] = [ret, get_cur_time()];
	return ret;

def add_dx(user_id, link):
	global main_lst;	
	for x in main_lst:
		if(x[1] == link):
			return 1

	main_lst.append([user_id, link])
	return 0

def get_insta_link(mess):
	ret = mess[mess.find(' ') + 1:len(mess)];
	if(insta.is_instalink(ret)):
		return ret
	return "";

def is_banned(user_id): #to test
	global ban_lst;
	for x in ban_lst:
		if(x[0] == user_id and x[1] >= 3):
			return 1;
	return 0;

#----------------------------------------------------------------------------------------------------------------#

def ban_time(user_id, t_minutes):
	global ban_lst
	for x in ban_lst:
		if(x[0] == user_id):
			answ = datetime.datetime.strptime(x[2], '%y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=t_minutes);		
			return answ.strftime('%y-%m-%d %H:%M:%S')

def forward_message(update, context, text, parse=0):
	if(parse):
		context.bot.send_message(
			chat_id=update.message.chat_id,
			reply_to_message_id=update.message.message_id,
			text=text,
			parse_mode=telegram.ParseMode.HTML,
			disable_web_page_preview=True)
	else:	
		context.bot.send_message(
			chat_id=update.message.chat_id,
			reply_to_message_id=update.message.message_id,
			text=text,
			disable_web_page_preview=True)

def send_message(chat_id, text, parse=0):
	global pseudo_context;
	if(parse):
		pseudo_context.bot.send_message(
			chat_id=chat_id,
			text=text,
			parse_mode=telegram.ParseMode.HTML,
			disable_web_page_preview=True)
	else:	
		pseudo_context.bot.send_message(
			chat_id=chat_id,
			text=text,
			disable_web_page_preview=True)

def get_creator_id(update, context):
	for i in context.bot.get_chat_administrators(update.message.chat.id):
		if(i['status'] == 'creator'):
			return i['user']['id']; 
	return -1;

def start(update, context):
	if(update.message.chat.type == "private"):
		msg = str();
		if(has_list(update.message.from_user.id)):
			msg = form_list("📋 Here are the current links that you need to like for that group:\n", sent_lst[update.message.from_user.id][0])
			send_message(update.effective_chat.id, msg);			
		else:
			send_message(update.effective_chat.id, start_message);


def list_handl(update, context):
	global main_lst;
	lst_len = len(main_lst);
	self_n = 0;
	for i in main_lst: 
		if(i[0] == update.message.from_user.id):
			lst_len -= 1;
			self_n = 1

	if(update.message.chat.type != "supergroup"):
		return 0;	
	
	if(lst_len == 0):
		if(self_n):
			forward_message(update, context, "I don't have anything for you yet")
		else:
			forward_message(update, context, "Nothing yet. Be the first one and send me your post");
	else:
		if(lst_len < DX):	
			forward_message(update, context, "Click <a style=\"color:blue\"href=\"https://t.me/insta_leechingbot?start=-1001386730703\">here</a> and then click 'start' to get the latest list for the group", parse=1);		
		else:
			forward_message(update, context, "Click <a style=\"color:blue\"href=\"https://t.me/insta_leechingbot?start=-1001386730703\">here</a> and then click 'start' to get the latest list for the group", parse=1)
		
		msg = str()
		msg = form_list(msg, get_list(update.message.from_user.id))
		send_message(update.message.from_user.id, msg);

def add_hand(update, context):
	global db; 
	global conn;

	if(update.message.chat.type == "private"):
		return 0;

	if(get_creator_id(update,context) == update.message.from_user.id):
		if(update.message.chat.type != "supergroup"):
			forward_message(update, context, bot_admin_instruction);
		else:
			if(not bot_db.group_exists(update.message.from_user.id, update.effective_chat.id, db)): 
				err = bot_db.create_group(update.message.from_user.id, update.effective_chat.id, db, conn)
				if(err == 0):
					forward_message(update, context, "Greate! The group has been created");
				else:
					forward_message(update, context, "Couldn't add the group");
			else:
				forward_message(update, context, "The group is already added");


def mesgs_hand(update, context): 
	global main_lst;
	global likes; 

	if(update.message.chat.type == "private"):
		if(is_banned(update.message.from_user.id)):
			send_message(update.effective_chat.id, "You are banned until" + ban_time(update.message.from_user.id, warning_time * 2));
		else:	
			send_message(update.effective_chat.id, start_message)
	elif(is_banned(update.message.from_user.id)):
		forward_message(update, context, "You are banned until" + ban_time(update.message.from_user.id, warning_time * 2));
	else:
		if(is_dx(update.message.text)):
			link = get_insta_link(update.message.text);
			if(link == ""):
				forward_message(update, context, "Invalid link")				
				return 0;
			
			if(get_creator_id(update,context) == update.message.from_user.id):
				if(add_dx(update.message.from_user.id, link)):
					forward_message(update, context, "This link is already in the system")
				else:
					forward_message(update, context, "Droped successfully");
			elif(
					(len(main_lst) < DX and dct_sum(likes, update.message.from_user.id, 0) >= 0) or
					dct_sum(likes, update.message.from_user.id, 0) >= DX
				):
			
				dct_sum(likes, update.message.from_user.id, -DX);
				
				if(add_dx(update.message.from_user.id, link)):
					forward_message(update, context, "This link is already in the system")
				else: 
					forward_message(update, context, "Droped successfully");
			else:
				forward_message(update, context, "You have to engage first. Type '/list' into the chat")
		else:
			if(not get_creator_id(update, context) == update.message.from_user.id):
				context.bot.deleteMessage(chat_id=update.message.chat.id, message_id=update.message.message_id)

#----------------------------------------------------------------#    
def get_info(update, context):
	pass;

info_handler = CommandHandler('info', get_info);
dispatcher.add_handler(info_handler)
#----------------------------------------------------------------#


start_handler = CommandHandler('start', start);
dispatcher.add_handler(start_handler);
list_handler = CommandHandler('list', list_handl);
dispatcher.add_handler(list_handler);
add_handl = CommandHandler('add', add_hand);
dispatcher.add_handler(add_handl);
messages_handler = MessageHandler(Filters.text, mesgs_hand)
dispatcher.add_handler(messages_handler)


def bot():
	updater.start_polling();

#----------------------------------------------------------------------------------------------------------------#

def warning_for_id(user_id):
	global ban_lst;
	for i in ban_lst:
		if(i[0] == user_id):
			i[1] += 1;
			i[2] = get_cur_time();
			return 0;

	ban_lst.append([user_id, 1, bot.get_cur_time()]);
	return 0;

def unban(user_id): 
	global ban_lst;
	i = 0
	while(i < len(ban_lst)):
		if(ban_lst[i][0] == user_id):
			break;
		i += 1 
	if(i == len(ban_lst)):
		return -1

	del ban_lst[i];
	return 0;

def reverse_dict(inp):
	keys = reversed(list(inp.keys()));
	return {i:inp[i] for i in keys};

def mark_as_done(user_id, link):
	global done;
	try: 
		done[link] = done[link].append(user_id);
	except:
		done[link] = [user_id]

def give_like_to(user_id):
	if(user_id < 0):
		return 0;
	global likes;
	dct_sum(likes, user_id, 1);


def check_once():
	global sent_lst;
	global debtors;
	global warning_time;
	global error_rate;
	global DX;
	global db;
	global session;
	global ban_lst;
	global pseudo_context;

	liked_posts = {}; # user_id : [link1, link2, link...]

	timeout = []; #late
		
	for x, y in sent_lst.items(): 	
		nearest_future = datetime.datetime.now() + datetime.timedelta(minutes=warning_time, seconds=5)
		if(nearest_future < datetime.datetime.strptime(y[1], '%y-%m-%d %H:%M:%S') ):
			timeout.append(x);
		
	for i in timeout:
		del sent_lst[i];

	liked_posts = {}; # user_id : [link1, link2, link...]
	p_sent_lst = reverse_dict(sent_lst);

	for x, y in p_sent_lst.items():						#liked posts
		for i in y[0]:
			if(get_likes_number(i[0]) > i[1]): 
				try: 
					tmp_lst = liked_posts[x];	  #id of the person that liked the post
					tmp_lst.append(i[0]);
					liked_posts[x] = tmp_lst;
				except:
					liked_posts[x] = [i[0]];
	
	liked_posts = reverse_dict(liked_posts);

	del_sent_lst = [];
	for x in liked_posts: 	#proc
		i = 0;
		undeb_lst = [];
		while(i < len(debtors)):
			if(x == debtors[i][0] and liked_posts[x] == debtors[i][1]):
				mark_as_done(x, debtors[i][0]);
				undeb_lst.append(i);
			i += 1;

		for y in undeb_lst:
			del debtors[y];

		for y in liked_posts[x]:
			mark_as_done(x, y);
			give_like_to(x);
			z = 0;
			while(z < len(p_sent_lst[x][0])):
				if(p_sent_lst[x][0][z][0] == y):
					del p_sent_lst[x][0][z];
					if(p_sent_lst[x][0] == []):
						del_sent_lst.append(x)
				z += 1;

	for x in del_sent_lst:
		del p_sent_lst[x];

	done_del = []
	for x in done:
		if(len(done[x]) >= DX):
			done_del.append(x)
	
	for x in done_del:
		del done[x];

	for i in timeout:
		warning_for_id(i);

	timeout = []
	for x in ban_lst:
		nearest_future = datetime.datetime.now() + datetime.timedelta(minutes=warning_time * 2, seconds=5)
		if(nearest_future < datetime.datetime.strptime(y[2], '%y-%m-%d %H:%M:%S') ):
			timeout.append(x[0]);
	
	for x in timeout:
		unban(x)

	sent_lst = reverse_dict(p_sent_lst)

def checker():
	while(True):
		check_once();
		time.sleep(1);

#----------------------------------------------------------------------------------------------------------------#

def make_backup():
	global db;
	global conn;
	global backup_functoins;
	for x in backup_functoins:
		res = x(db, conn, backup_functoins[x])
		if(type(res) != int):
			print("You have a fatal error!")
			print("MySQL: database: 'eng_bot': couldn't write table : ")
			print(backup_functoins[x])
		else:
			print(backup_functoins[x], ": backuped")

def stop_thread(thrd):
	Thread(target=thrd).join

def signal_handler(sig, frame):
	stop_thread(checker);
	stop_thread(bot);
	make_backup()

	print('\nBay')
	sys.exit(0);
