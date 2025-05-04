# Angela

An open source Discord bot built with a mix of functionality and fun.

# Features

As of 30/04/2025, the available commands are:

+ **`/help`** - Shows a list of commands
+ **`/weather`** - Gives info on the weather in a given city.
+ **`/ask`** - Uses AI to answer your questions (ChatGPT only)
+ **`/exchange`** - Converts EUR into other currencies
+ **`/clean`** - Purge a given number of messages
+ **`/filter_add`** - Add a given word to the filter list
+ **`/filter_remove`** - Remove a given word from the filter list
+ **`/filter_list`** - Displays the server's filter list
+ **`/mediafilter`** - Toggles media filtering settings for the channel you're currently viewing
+ **`/mediafilter_show`** - Displays the filtering settings for the channel you're currently viewing
+ **`/token`** - Displays the bot's token ;)
+ **`/joke`** - The bot will tell you a joke
+ **`/coinflip`** - Tosses a coin
+ **`/magic_8_ball`** - Get predictions about the future (source: trust me bro)
+ **`/owner`** - Get in contact with the developer
+ **`/donate`** - Receive a link to my ko-fi page
+ **`/stats`** - Returns bot's latency and RAM usage

# Requirements

1. [Python](https://www.python.org/) 3.13.3 or later with pip
2. [Github CLI](https://cli.github.com/)
3. The necessary python modules (see more in the installation guide)
4. Your own application in the [Developer portal](https://discord.com/developers/applications)
	- This is necessary so you can get a bot token to pair with the code. Keep the token well hidden, it's like the house keys to the bot
5. A .env file containing:
	1. the bot's token
	2. an api key from [Weatherstack](https://weatherstack.com/)
	3. an api key from [Fixer.io](https://fixer.io/)
	4. an api key from [OpenAI](https://openai.com/index/openai-api/)

# Planned Features

- [x] Added a server specific filter
- [x] AI Powered answers to your questions
- [x] Added channel-specific media filtering
- [x] Bulk delete messages
- [x] Fetch jokes from an API
- [ ] Reminders from inside Discord
- [ ] Poll creation
- [ ] Fortune cookies
- [ ] Fuck, Marry, Kill game
- [ ] Rock, Paper, Scissors

And more! I have a board on Trello for this thing, and i feel like it's unnecessary to just copy everything that's there.
Some ideas might get scrapped in the process, so no promises!

# Installation

1. **Clone the Repository**: Make sure you have the [GitHub CLI](https://cli.github.com/) installed 
2. **Open a terminal window:** On windows, hold shift and right click inside your desired folder, click "open in terminal" and run the following command:
```
gh repo clone Gal-ahad/Angela
```
  - on Mac, Right-click inside the Angela folder and select "New Terminal at Folder."
  - On Linux, Right-click inside the Angela folder and choose "Open in Terminal."
3. **Create a .env file:** Open Notepad (or your preferred text editor), and save a new file named `.env` inside of the main `Angela` folder
4. Add your API keys in the following format: `VARIABLENAME = value` (spaces are optional)
    Navigate to the main folder:
```
cd Angela
```
6. **Install Dependencies:** Make sure you have Python and pip installed, then run:
```
pip install -r requirements.txt
```
7. type `python Angela.py` or `py Angela.py` and enter
	- if you already have a code editor you can also run the main script from there.
  - It's not necessary since you can do all this with just the terminal and notepad, but if you insist, popular choices include [Visual Studio Code](https://code.visualstudio.com/) and [Sublime Text](https://www.sublimetext.com/)

If everything was done correctly you should be able to host the bot on your machine! If the guide is incorrect let me know.

# Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Clone the repository
2. Create your own branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

Additionally (or if you can't code) you can help financially with a donation on [Ko-Fi](https://ko-fi.com/ga1_ahad). No pressure though!

# License

This project is licensed under the GNU Public General License - see the LICENSE file for details.

# Support

To get in contact with me either run the /owner command from the bot or contact me on the following:

- [Twitter](https://x.com/_Ga1ahad)
- [Bluesky](https://bsky.app/profile/lolishojo.bsky.social)
- [Mastodon](https://mastodon.social/@Sir_Ga1ahad)
- Discord: ga1_ahad
