<h1 align="center">
    Instagram Engagement Bot<br>
        <br>
    <img src="https://github.com/lrusifikator/engagement_bot/blob/master/img/boticon.jpg">
        <br>
</h1>
<br>

## Introduction
An engagement bot is a bot for administrating your engagement group, where people can exchange likes with each other.  It will send lists with links that the user must engage and then the user can send his request for engagement in the group.

The bot can: 
- Detect and mute/ban leechers
- Detecting leechers every 5 minutes (not hourly like the other bots) 
- Detect if the user took his like back after a while
- Delete spam and unrelated messages
- Extra privileges for the creator of the group for dropping links without engaging 
- Free 

---

<br>

## Instructions

### Create your first bot

1. Message [`@BotFather`](https://telegram.me/BotFather) with the following text: `/newbot`
   
   If you don't know how to message by username, click the search field on your Telegram app and type `@BotFather`, where you should be able to initiate a conversation. Be careful not to send it to the wrong contact, because some users have similar usernames to `BotFather`.

   ![BotFather initial conversation](https://github.com/lrusifikator/engagement_bot/blob/master/img/create_bot1.png)

2. `@BotFather` replies with:

    ```
    Alright, a new bot. How are we going to call it? Please choose a name for your bot.
    ```

3. Type whatever name you want for your bot.

4. `@BotFather` replies with:
    
    ```
    Good. Now let's choose a username for your bot. It must end in `bot`. Like this, for example: TetrisBot or tetris_bot.
    ```

5. Type whatever username you want for your bot, minimum 5 characters, and must end with `bot`. For example: `telesample_bot`

6. `@BotFather` replies with:

    ```
    Done! Congratulations on your new bot. You will find it at
    telegram.me/telesample_bot. You can now add a description, about
    section and profile picture for your bot, see /help for a list of
    commands.

    Use this token to access the HTTP API:
    123456789:AAG90e14-0f8-40183D-18491dDE

    For a description of the Bot API, see this page:
    https://core.telegram.org/bots/api
    ```



Set the bot privacy:

1. Send `/setprivacy` to `@BotFather`.

   ![BotFather later conversation](https://github.com/lrusifikator/engagement_bot/blob/master/img/create_bot2.png)

2. `@BotFather` replies with:

    ```
    Choose a bot to change group messages settings.
    ```

3. Type (or select) `@telesample_bot` (change to the username you set at step 5
above, but start it with `@`)

4. `@BotFather` replies with:

    ```
    'Enable' - your bot will only receive messages that either start with the '/' symbol or mention the bot by username.
    'Disable' - your bot will receive all messages that people send to groups.
    Current status is: ENABLED
    ```

5. Type (or select) `Disable` to let your bot receive all messages sent to a group.

6. `@BotFather` replies with:

    ```
    Success! The new status is: DISABLED. /help
    ```


Congratulations, you've created your own bot!

<br>

---

## Now it's time to setup your bot
The main setting file is 'eng_bot/settings.py'.

1. Type in the terminal
`git clone https://github.com/lrusifikator/engagement_bot` 
`cd engagement_bot`

2. First, you have to get you bot token: 
Send `/token` to `@BotFather`.
`@BotFather` replies with:


    ```
    You can use this token to access HTTP API:
    YOUR_TOKEN

    For a description of the Bot API, see this page: https://core.telegram.org/bots/api
    ```

Copy and paste in the settings.py in the variable 'telegram_token'.

3. Fill the Instagram login and password variables in the settings.py file. 

*It's needed for the bot to login and check the like counts of the users. You'll get notifications from Instagram that someone from your citie of from the nearest cities has logged into your account from different operating systems. It's the bot logging in. Don't worry, it's absolutely private and this information won't be sent to anyone*

4. Fill the fields for the MySQL server.
If you don't have one, here is how to install it on Windows: <br> 
https://www.liquidweb.com/kb/install-mysql-windows/ <br>
Linux: <br>
https://support.rackspace.com/how-to/installing-mysql-server-on-ubuntu/
Note:  In the same file you can change the DX rete and other settings

5. Type in the terminal: 
`bash install` for linux and `python3 setup.py install --record files.txt` for windows

6. Type in the terminal: 
`eng_bot`

7. To change settings edit file 'eng_bot/settings.py' and go to point 5
 
8. To delete the bot run command: `bash delete` for linux or if you're running Windows, use Powershell: 
`Get-Content files.txt | ForEach-Object {Remove-Item $_ -Recurse -Force}`


---
 
### You have to run the bot constantly or it won't work, for this reason you might want to get a <a href="https://www.ovh.com/world/vps/">VPS host</a>

<br>

---

## Contacts
Email: yakushev.rusl101@gmail.com

