
# Angela

A simple discord bot with a mix of functional and humorous commands. The project was born as an exercise to practice programming, so i wouldn't get rusty after not opening an IDE for too long.
## Authors

- [@Gal-ahad](https://www.github.com/Gal-ahad)


## Requirements

- Python 3.13.3 or later
- Dependencies and API keys (see more in the [Run Locally](#run-locally) section)
## Run Locally

1. Clone the repository

    ```
    gh repo clone Gal-ahad/Angela
    ```

2. Create a `.env` file containing the following API keys in the root folder:
    ```
    TOKEN = your bot's token
    weather = your api key
    OPENAI_API_KEY = your api key
    fixer_api = your api key
    ```
The keys can be found at: [Discord's Developer portal](https://discord.com/developers/applications), [Weatherstack](https://weatherstack.com/), [OpenAI](https://platform.openai.com/docs/overview) and [Fixer.io](https://fixer.io/)

3. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

4. Run from an IDE or type `py Angela.py` in a terminal window
## Usage

In a channel where the bot has write and slash commands permissions, type:
```
/help
```
For a list of commands.

## Features

- Retrieve weather for a given city
- Use AI to answer queries
- Exchange EUR into other currencies
- Filter and purge capabilities
- Channel and media specific filtering

And more!

## License

[GNU General Public License v3.0](https://github.com/Gal-ahad/Angela/blob/main/LICENSE)


## Screenshots

![App Screenshot](https://files.catbox.moe/d772sq.png)
![App Screenshot](https://files.catbox.moe/85nmmb.png)
## Planned Features

- [ ]  Ban, kick, mute and timeout users
- [ ]  Get reminders from inside Discord
- [ ]  Create polls
- [ ]  Assign roles thru reactions
- [ ]  Choice picker
- [ ]  Fortune cookies
- [ ]  Rock Paper Scissors
## Support

For support, please head over to my [profile's readme](https://github.com/Gal-ahad/Gal-ahad?tab=readme-ov-file#-find-me-elsewhere).
Or you can [buy me a coffee](https://ko-fi.com/ga1_ahad)
