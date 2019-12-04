
#--------------------------------------------------SETUP---------------------------------------------------------#

telegram_token = ""

insta_login = ""
insta_pass =  ""

mysql_passwd=""
mysql_host="localhost"
mysql_user="root"

#----------------------------------------------------------------------------------------------------------------#

# It is always better to set a lower dx. Because the bot will make fewer mistakes 
# at the start and when the group is not active enough. 
# Once it has enough active users it'll work stable 
DX = 5

# 0, 1 - no one is getting extra likes
# 2 - half is getting extra likes
# 3 - third is getting extra likes
# etc
error_rate = 3 

warning_time = 5 # minutes #time before getting a warning for not engaging
warnings_for_ban = 3

done_instr = "CREATE TABLE done(link TEXT";
for i in range(DX):
	done_instr += ", user_id_" + str(i) + " INT";
done_instr += ")";

sent_lst_instr = "CREATE TABLE sent_lst(user_id INT";
for i in range(DX):
	sent_lst_instr += ", link_" + str(i) + " TEXT, likes_" + str(i) + " INT";
sent_lst_instr += ", start_at DATETIME)";

tables = {
	"groups"   : "CREATE TABLE groups(user_id INT, group_id BIGINT, DX INT, w_time INT, er_rate INT, w_for_ban INT, group_name TEXT)",
	"likes"    : "CREATE TABLE likes(user_id INT, likes_number INT)",
	"main_lst" : "CREATE TABLE main_lst(user_id INT, link TEXT)",
	"debtors"  : "CREATE TABLE debtors(user_id INT, debt INT)",
	"ban_lst"  : "CREATE TABLE ban_lst(user_id INT, warnings INT, ban_start DATETIME)",
	"done"     : done_instr,
	"sent_lst" : sent_lst_instr
}

botname = "insta_leechingbot"


#-------------------------------------------------BOT MESSAGES--------------------------------------------------#

local_add_insctuction = "local_add_insctuction"
get_list_inctruciton = 'To get the list send message "/list" to me';

bot_admin_instruction = "Make me admin";
instruction_continue = "Furder instruction";
start_message = """
Hi! I'm @insta_leechingbot and I can get you the list of links for the group managet by me. 

All you need to do is send '/list' in the group
""";

#----------------------------------------------------------------------------------------------------------------#
