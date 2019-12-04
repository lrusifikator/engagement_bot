#!/usr/bin/python
from eng_bot import ban_lst, sent_lst, main_lst, debtors,  likes, done
import eng_bot as bot
from eng_bot.bot_settings import DX
import random
import datetime

def test_unban():
	global ban_lst
	user_id = random.randrange(0, 99999)
	tmp = [user_id, 5, bot.get_cur_time()]
	ban_lst = [tmp]

	assert bot.unban(random.randrange(0, 99999)) == -1
	assert ban_lst == [tmp]

	assert bot.unban(user_id) == 0;
	assert ban_lst == []
	
def test_warning_for_id():
	global ban_lst;
	user_id = random.randrange(0, 99999);
	bot.warning_for_id(user_id);
	assert ban_lst == [[user_id, 1, bot.get_cur_time()]]
	bot.warning_for_id(user_id);
	assert ban_lst == [[user_id, 2, bot.get_cur_time()]]

def test_ban_time():
	global ban_lst
	user_id = random.randrange(0, 99999);
	ban_lst.append([user_id, 3, bot.get_cur_time()]);
	t_minutes = 5

	answ = datetime.datetime.strptime(bot.get_cur_time(), '%y-%m-%d %H:%M:%S') + datetime.timedelta(minutes=t_minutes)
	answ = answ.strftime('%y-%m-%d %H:%M:%S')
	assert bot.ban_time(user_id, t_minutes) == answ;

def is_banned(user_id): 
	global ban_lst;
	for x in ban_lst:
		if(x[0] == user_id and x[1] >= 3):
			return 1;
	return 0;

def test_is_banned(): #suk
	global ban_lst;

	user_id = random.randrange(0, 99999);
	assert is_banned(user_id) == 0;
	ban_lst.append([user_id, 3, bot.get_cur_time()]);
	assert is_banned(user_id) == 1;

def pseudo_get_likes_number(sm, tng):
	pass;

def test_get_list():
	global sent_lst, main_lst;
	global lst_index;

	user_id = random.randrange(0, 999999);
	dt_1 = [[["link1", 1], ["link2", 2], ["link3", 3], ["link4", 4]], bot.get_cur_time()];
	sent_lst[user_id] = dt_1
	assert bot.get_list(user_id) == dt_1[0];
	
	lst_index = 0;
	'''main_lst = [
	[111, "link111"],  [1, "link1"],  [2, "link2"],  
	[3, "link3"],  [4, "link4"],  [5, "link5"],  
	[6, "link6"],  [7, "link7"],  [8, "link8"],  
	[9, "link9"],   [10, "link10"], [11, "link11"], 
	[12, "link12"], [13, "link13"], [14, "link14"], 
	[15, "link15"], [16, "link16"], [17, "link17"], 
	[18, "link18"], [19, "link19"], [20, "link20"],
	];

	assert bot.get_list(20, pseudo_get_likes_number) == [
	[111, "link111"],  [1, "link1"],  [2, "link2"],  
	[3, "link3"],  [4, "link4"]];
	'''
	
def test_mark_as_done():
	global done;
	bot.mark_as_done(890, "link123");	
	assert done["link123"] == [890]

def test_give_like_to():
	global likes;
	bot.give_like_to(678)
	assert likes[678] == "1";
	bot.give_like_to(678)
	assert likes[678] == "2";

def test_reverse_dict():
	assert bot.reverse_dict({1:"a", 2:"b", 3:"c", 4:"d"}) == {4:"d", 3:"c", 2:"b", 1:"a"};

def test_add_dx():
	global main_lst;

	assert bot.add_dx(123, "link41234") == 0;
	assert bot.add_dx(5432, "link41234") == 1;

def test_get_insta_link():
	assert bot.get_insta_link("s https://www.instagram.com/p/B41gXCvnbHM/") == "https://www.instagram.com/p/B41gXCvnbHM/"; 
	assert bot.get_insta_link("s s https://www.instagram.com/p/B41gXCvnbHM/") == "";
	assert bot.get_insta_link("s https://google.com") == "";

def test_dct_sum():
	dct = dict();

	bot.dct_sum(dct, 1, 1)
	bot.dct_sum(dct, 2, 0)
	bot.dct_sum(dct, 3, -1)

	assert dct[2] == "0";
	assert dct[1] == "1";
	assert dct[3] == "-1";

def test_form_list():
	lst = []
	lst.append("Hello");
	assert bot.form_list("", ["Hello"]) == "\n1) Hello\n"; 
	assert bot.form_list("Hi", ["Hello"]) == "Hi\n1) Hello\n";
	assert bot.form_list("Hi", ["Hello", "world", "!"]) == "Hi\n1) Hello\n2) world\n3) !\n";

def test_is_dx():
	assert bot.is_dx("dx" + str(DX) + " ") == 1;
	assert bot.is_dx("Dx" + str(DX) + " ") == 1;
	assert bot.is_dx("dX" + str(DX) + " ") == 1;
	assert bot.is_dx("DX" + str(DX) + " ") == 1;
	assert bot.is_dx("dx ") == 0;
	assert bot.is_dx("dx") == 0;
	assert bot.is_dx(" ") == 0;
	assert bot.is_dx("") == 0;

def test_has_list():
	global sent_lst;
	user_id = random.randrange(0,99999);	
	assert bot.has_list(user_id) == 0;

	sent_lst[user_id] = [ [["link1", "1"], ["link2", "2"]], bot.get_cur_time() ]
	assert bot.has_list(user_id) == 1;

