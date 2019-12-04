import datetime
from eng_bot.bot_settings import tables
from eng_bot.bot_settings import DX
test_mode = 0;

def check_db_exists(db, db_name):
	db.execute("SHOW DATABASES");
	res = db.fetchall();
	for x in res:
		if(x[0] == db_name):
			return True;
	return False;

def check_table_exists(db, tablename):
	db.execute("""
	SELECT COUNT(*)
	FROM information_schema.tables
	WHERE table_name = '{0}'
	""".format(tablename.replace('\'', '\'\'')))
	
	if db.fetchone()[0] == 1:
		return True

	return False

def save_open(db, x, instr):
	if(check_table_exists(db, x)):
		return 0;
	try:
		db.execute(instr); 
	except:
		return 2;
	return 1;

def set_db(db, tables):	
	db_name = "eng_bot"
	try:
		if(not check_db_exists(db, db_name)):
			db.execute("CREATE DATABASE " + db_name);
			print("Created database eng_bot");

		db.execute("USE " + db_name);
	except:
		print("Couldn't create database '" + db_name +  "'");	
		exit(1);

	for x in tables:
		state = save_open(db, x, tables[x])
		if(state == 2):
			print("Couldn't create table '" + x + "'");
			exit(1);
		elif(state):
			print("Created table", x, " (", tables[x], ") ");
			print()

def group_exists(user_id, group_id, db):
	sql = "SELECT * FROM groups WHERE user_id=" + str(user_id);		
	db.execute(sql)
	result = db.fetchall();
	for row in result:
		if(row[1] == group_id):
			return 1;

	return 0;


def create_group(user_id, group_id, conn, db):
	if(group_exists(user_id, group_id, db)):
		return 0;

	sql = "INSERT INTO groups(user_id, group_id) VALUES(" + str(user_id) + ", " + str(group_id) + ")";
	try:
		db.execute(sql);
		conn.commit();
	except:
		return 1;
	
	return 0;

	
def has_groups(user_id):
	sql = "SELECT * FROM groups WHERE user_id=" + str(user_id);		
	db.execute(sql)
	if(len(db.fetchall()) > 0):
		return 1;
	
	return 0;


def del_nones(lst):
	ret = []
	for x in lst:
		if(x != None):
			ret.append(x)

	return ret;

def set_to_dict(res):
	ret = {}
	for x in res:
		if(None in x):
			continue;

		entry = x[1:]

		if(len(entry) == 0):
			continue;

		entry = list(entry);

		if(len(entry) == 1):
			ret[x[0]] = str(entry[0]);
		else:
			ret[x[0]] = entry;

	return ret

def set_to_list(res):
	ret = []
	for x in res:
		if(None in x):
			continue;

		if(len(x) == 0):
			continue;

		x = list(x);
		if(len(x) == 1):
			ret.append(x[0]);
		else:
			ret.append(x);

	return ret;

def get_list(db, table, cust=[]):
	global test_mode;

	t = type(cust);
	if(t != list and t != dict):
		return -1;

	if(test_mode == 1):
		if(t == dict):
			return {};
		else:
			return [];

	db.execute("SELECT * FROM " + table);
	res = db.fetchall();
	
	if(t == dict):
		return set_to_dict(res);
	else:
		return set_to_list(res);


def get_main_lst(db):
	return get_list(db, "main_lst", []);

def get_likes(db):
	return get_list(db, "likes", {});

def get_done(db):
	global test_mode;
	if(test_mode == 1):
		return {};


	db.execute("SELECT * FROM done");
	res = db.fetchall();
	
	ret = {}
	for x in res:
		if(x[0] == None):
			continue;

		x = del_nones(x);
		if(len(x) == 1):
			continue;
		entry = x[1:];

		x = list(x);
		if(len(entry) == 1):
			ret[x[0]] = entry[0];
		else:
			ret[x[0]] = entry;

	return ret

def get_ban_lst(db):
	return get_list(db, "ban_lst", []);

def get_debtors(db):
	return get_list(db, "debtors", []);

def get_groups(db):
	global test_mode;
	if(test_mode == 1):
		return [];	

	ret = [];

	db.execute("SELECT * FROM groups");
	res = db.fetchall();
	
	for x in res:
		if(x[0] == None or x[1] == None or x[2] == None):
			continue;
		ret.append(list(x));

	return ret

def get_sent_lst(db):
	global test_mode;
	if(test_mode == 1):
		return {};

	ret = {};
	keys_instr = "SELECT user_id FROM sent_lst";

	sent_lst_instr = "SELECT ";
	for i in range(DX):
		sent_lst_instr += " link_" + str(i) + ", likes_" + str(i) + ",";
	sent_lst_instr = sent_lst_instr[0:-1]
	sent_lst_instr += " FROM sent_lst";

	time_instr = "SELECT start_at FROM sent_lst";
	
	db.execute(keys_instr);
	keys = db.fetchall();
	db.execute(sent_lst_instr);
	data = db.fetchall();
	db.execute(time_instr);
	time = db.fetchall();

	for i in range(len(data)):
		
		if(keys[i][0] == None or time[i][0] == None):
			continue;
			
		tmp = []
		y = 0; 
		while(y < len(data[i])):
			data[i] = list(data[i]);
			if(data[i][y + 1] != None and data[i][y] != None):
				tmp.append([data[i][y], data[i][y + 1]]);
			y += 2;

		if(len(tmp) == 0):
			continue;

		ret[keys[i][0]] =[tmp ,time[i][0]];

	return ret;



def test_write(db, conn, table, field):
	db.execute("DELETE FROM " + table + " WHERE " + field + "=-1");
	db.execute("INSERT INTO " + table + "(" + field + ") VALUES(-1)");
	db.execute("SELECT * FROM " + table + " WHERE " + field + "=-1");
	if(len(db.fetchall()) > 0):
		db.execute("DELETE FROM " + table + " WHERE " + field + "=" + str(-1));
		return 0
	
	return 1;

def lst_to_table(lst, lst_type = 0):
	return [];

def safe_write2(db, conn, table, f_field, s_field, first, second):
	first = str(first)
	second = str(second)

	if(type(first) != int):
		first = "'" + first + "'"; 

	if(type(second) != int):
		second = "'" + second + "'";

	try:
		db.execute("INSERT INTO " + table + " VALUES(" + first + "," + second + ")");
		conn.commit();	
	except:
		pass



def set_lst(db, conn, table, f_field, s_field, lst):
	for x in lst:	
		safe_write2(db, conn, table, f_field, s_field, x[0], x[1]);

def set_dct(db, conn, table, f_field, s_field, lst):
	for x in lst:	
		safe_write2(db, conn, table, f_field, s_field, x, lst[x]);


def set_list(db, conn, table, f_field, s_field, lst):
	global test_mode;
	if(test_mode == 1):
		return 0;

	if(len(lst) == 0):
		return 0;

	db.execute("DROP TABLE " + table);
	if(save_open(db, table, tables[table]) == 2):
		return lst_to_table(lst);

	if(test_write(db, conn, table, "user_id")):
		return lst_to_table(lst);

	t = type(lst)
	if(t == dict):
		set_dct(db, conn, table, f_field, s_field, lst);
	elif(t == list):
		set_lst(db, conn, table, f_field, s_field, lst);
	else:
		return 1;

	return 0;

def set_main_lst(db, conn, lst):
	return set_list(db, conn, "main_lst", "user_id", "link", lst);

def set_likes(db, conn, lst):
	return set_list(db, conn, "likes", "user_id", "likes_number", lst);	

def set_debtors(db, conn, lst):
	return set_list(db, conn, "debtors", "user_id", "debt", lst);

def set_ban_lst(db, conn, lst):
	global test_mode;
	if(test_mode == 1):
		return 0;

	db.execute("DROP TABLE ban_lst");
	if(save_open(db, "ban_lst", tables["ban_lst"]) == 2):
		return lst_to_table(lst);

	if(test_write(db, conn, "ban_lst", "user_id")):
		return lst_to_table(lst);

	for x in lst:
		x[0] = str(x[0]);
		x[1] = str(x[1]);
		x[2] = str(x[2]);

		try:
			db.execute("INSERT INTO ban_lst VALUES(" + x[0] + ",'" + x[1] + "', '" + x[2] + "')");
			conn.commit();
		except:
			continue
	return 0;

def set_done(db, conn, lst):
	global test_mode;
	if(test_mode == 1):
		return 0;
	
	db.execute("DROP TABLE done");
	if(save_open(db, "done", tables["done"]) == 2):
		return lst_to_table(lst);

	if(test_write(db, conn, "done", "user_id_0")):
		return lst_to_table(lst);

	for x in lst:

		ind = 0
		insert_instr_1 = "(link";
		insert_instr_2 = ") VALUES('" + str(x) + "'";
		
		for i in lst[x]:
			insert_instr_1 += ", user_id_" + str(ind)
			insert_instr_2 += "," + str(i);	
			ind += 1
		try:
			db.execute("INSERT INTO done " + insert_instr_1 + insert_instr_2 + ")");
			conn.commit();
		except:
			continue
	return 0


def set_sent_lst(db, conn, lst):
	global test_mode;
	if(test_mode == 1):
		return 0;

	db.execute("DROP TABLE sent_lst");
	if(save_open(db, "sent_lst", tables["sent_lst"]) == 2):
		print("save_open")
		return lst_to_table(lst, 1);

	if(test_write(db, conn, "sent_lst", "user_id")):
		print("test_write")
		return lst_to_table(lst, 1);

	for x in lst:
		insert_instr_1 = "(user_id";
		insert_instr_2 = ") VALUES(" + str(x);
		
		ind = 0;
		for i in range(len(lst[x][0])):
			insert_instr_1 += ", link_" + str(ind) + ", likes_" + str(ind) ;
			ind += 1;

		insert_instr_1 += ", start_at";
		
		for i in lst[x][0]:
			if(type(i[0]) == str and type(i[1]) == int):
				insert_instr_2 += ", '" + str(i[0]) + "', " + str(i[1]);

		try:
			db.execute("INSERT INTO sent_lst " + insert_instr_1 + insert_instr_2 + ", '" + lst[x][1] + "')");
			conn.commit();
		except:
			continue

	return 0