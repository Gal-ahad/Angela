import discord, asyncio, datetime, requests, os, random, psutil, time
from typing import Optional, Dict
from dotenv import load_dotenv


# Load environment variables to ensure they're available
load_dotenv()


# Global client reference (to be set from the main file)
_client = None


def set_client(client):

    # Set the client reference from the main file
    global _client
    _client = client


# Try to import OpenAI - with fallback if not available
try:
    import openai
    # Set up the OpenAI API client with the key from the environment

    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai_available = True

except ImportError:
    import openai
    openai_available = False
    print("OpenAI package not installed - /ask command will be unavailable")


# the joke token command
async def token(interaction: discord.Interaction):
    await asyncio.sleep(2)
    await interaction.response.send_message("https://tenor.com/biqA0.gif")


# credits the developer
async def owner(interaction: discord.Interaction):

    embed = discord.Embed(
        title="Credits",
        description="Some places where you can contact me.",
        color=discord.Color.teal(),
        timestamp=datetime.datetime.now()
    )

    embed.add_field(name="Github", value="https://github.com/Gal-ahad", inline=False)
    embed.add_field(name="Discord", value="Username: ga1_ahad.", inline=False)
    embed.add_field(name="Twitter", value="https://x.com/_Gal_ahad", inline=False)
    embed.add_field(name="Bluesky", value="https://bsky.app/profile/lolishojo.bsky.social", inline=False)
    embed.add_field(name="Mastodon", value="https://mastodon.social/@Sir_Ga1ahad", inline=False)
    embed.add_field(name="Reddit", value="https://www.reddit.com/user/Storyshifting/", inline=False)

    await interaction.response.send_message(embed=embed)


# currency exchange
async def fetch_exchange_rate(target_currency: str) -> Optional[float]:

    api_key = os.getenv("fixer_api")
    if not api_key:
        return None

    base_url = "http://data.fixer.io/api/latest"
    params = {
        "access_key": api_key,
        "symbols": target_currency
    }

    try:
        response = requests.get(base_url, params=params)
        data = response.json()

        if not data.get("success", False):
            return None

        rates = data.get("rates", {})
        target_rate = rates.get(target_currency)

        if target_rate is None:
            return None

        # Since Fixer always returns EUR as base, EUR ➔ target rate is direct
        return target_rate

    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None

async def get_exchange_rate_implementation(
    interaction: discord.Interaction,
    amount: float,
    target_currency: str
):
    await interaction.response.defer(ephemeral=False)

    target = target_currency.upper()
    source = "EUR"  # Fixed source currency

    # Get the rate from EUR to target
    rate = await fetch_exchange_rate(target)

    if rate is not None:
        converted_amount = amount * rate

        embed = discord.Embed(
            title="Currency Conversion",
            description=f"Conversion from {source} to {target}",
            color=discord.Color.yellow(),
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(name="Amount", value=f"{amount:,.2f} {source}", inline=True)
        embed.add_field(name="Exchange Rate", value=f"1 {source} = {rate:,.4f} {target}", inline=True)
        embed.add_field(name="Converted Amount", value=f"{converted_amount:,.2f} {target}", inline=True)

        embed.set_footer(text=f"Requested by {interaction.user.name}")

        await interaction.followup.send(embed=embed)

    else:
        await interaction.followup.send(f"Failed to get exchange rate for {target}. Please check the currency code and try again.")


# donate command
async def donate(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Tip the developer.",
        description="Support the bot's development! If you can.",
        color=discord.Color.red()
    )

    embed.add_field(name="Buy me a coffee.", value="https://ko-fi.com/ga1_ahad", inline=False)

    await interaction.response.send_message(embed=embed)


# ping and RAM
async def stats(interaction: discord.Interaction, client=None):

    # Use the global client if one wasn't provided
    if client is None:
        client = _client
    
    # Calculate latency
    start_time = time.time()
    await interaction.response.defer(ephemeral=False)
    end_time = time.time()
    
    # Calculate API latency
    api_latency = round((end_time - start_time) * 1000)
    
    # Safely handle WebSocket latency (handle NaN case)
    try:
        if client and client.latency and not (client.latency != client.latency):  # Check if not NaN
            websocket_latency = f"{round(client.latency * 1000)} ms"
        else:
            websocket_latency = "Calculating..."

    except TypeError as type_error:
        websocket_latency = f"Unavailable: {type_error}"
    except AttributeError as attribute_error:
        websocket_latency = f"Unavailable: {attribute_error}"
    
    # Get memory usage
    process = psutil.Process(os.getpid())
    memory_usage = process.memory_info().rss / 1024 / 1024  # Convert to MB
    
    # Create embed
    embed = discord.Embed(
        title="Bot Stats",
        description="Current performance statistics",
        color=discord.Color.light_grey()
    )
    
    embed.add_field(name="API Latency", value=f"{api_latency} ms", inline=True)
    embed.add_field(name="WebSocket Latency", value=websocket_latency, inline=True)
    embed.add_field(name="Memory Usage", value=f"{memory_usage:.2f} MB", inline=True)
    
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    embed.timestamp = discord.utils.utcnow()
    
    await interaction.followup.send(embed=embed)


# coin flip command
async def coin(interaction: discord.Interaction):

    await interaction.response.send_message("🪙 Flipping a coin...")
    coin_to_toss = ["heads", "tails"]
    outcome = random.choice(coin_to_toss)
    await interaction.response.send_message(f"And the outcome was {outcome}!")


# joke command
async def joke(interaction: discord.Interaction):

    try:
        # Defer the response since we're making an API call
        await interaction.response.defer()
        
        # Make a direct HTTP request to the JokeAPI service
        joke_api_url = "https://v2.jokeapi.dev/joke/Any"
        
        # Use the request library to get a joke
        response = requests.get(joke_api_url)
        joke_data = response.json()
        
        if joke_data["type"] == "single":
            await interaction.followup.send(joke_data["joke"])

        else:
            setup = joke_data["setup"]
            delivery = joke_data["delivery"]
            await interaction.followup.send(f"{setup}\n\n{delivery}")
            
    except Exception as e:
        await interaction.followup.send(f"I couldn't fetch a joke right now: {str(e)}.")


# weather command
async def weather(interaction: discord.Interaction, location: str):

    # Defer the response since API calls might take some time
    await interaction.response.defer()

    weather_api_key = os.getenv("weather")
    if not weather_api_key:
        await interaction.followup.send("Weather API key not found. Please check your environment variables.")
        return

    weather_base_url = 'http://api.weatherstack.com/current'

    # Fetch and display the weather for a given location
    params = {'access_key': weather_api_key, 'query': location}

    try:
        # Make a request to the Weatherstack API
        response = requests.get(weather_base_url, params=params)
        data = response.json()

        # Check for an error from the API
        if 'error' in data:
            error_info = data['error']
            if error_info.get('code') == 104:  # Code 104 = Monthly quota reached
                weather_info = "I'm sorry, but I'm operating on a free plan and I have reached the limit for this month's requests."
            else:
                weather_info = f"Error fetching weather data: {error_info.get('info', 'Unknown error')}"

        elif 'current' in data and 'location' in data:
            current_weather = data['current']
            location_name = data['location']['name']
            temperature = current_weather['temperature']
            weather_descriptions = ', '.join(current_weather.get('weather_descriptions', ['Unknown']))
            humidity = current_weather.get('humidity', 'Unknown')
            wind_speed = current_weather.get('wind_speed', 'Unknown')

            # Create a response message
            weather_info = (f"Weather in {location_name}:\n"
                          f"Temperature: {temperature}°C\n"
                          f"Condition: {weather_descriptions}\n"
                          f"Humidity: {humidity}%\n"
                          f"Wind Speed: {wind_speed} km/h")
        else:
            weather_info = "Sorry, I couldn't retrieve the weather information. Please check the location and try again."
    
    except Exception as e:
        weather_info = f"Error processing weather data: {str(e)}"

    # Send the weather information back to the Discord channel
    await interaction.followup.send(weather_info)


# magic 8 ball
async def magic8ball(interaction: discord.Interaction, message: str = None):

    magicball_answers = [
        "It is certain.", "It is decidedly so.", "Without a doubt.", "Yes, definitely.", "You may rely on it.",
        "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", 
        "Don't count on it.", "My answer is no.", "My sources say no.", "Doubtful.", 
        "Ask me again.", "Can't right now, ask later.", "Meh. Maybe.", "Telling you would ruin the surprise.",
        "Nuh uh.", "Absolutely not.", "Not a chance.", "You sure you want to know?", 
        "Sure, I guess.", "What do you expect me to say?"
    ]
    
    # Acknowledge the user's question if provided
    if message:
        response = f"You asked: '{message}'\n\nMy answer: {random.choice(magicball_answers)}"
    else:
        response = random.choice(magicball_answers)
        
    await interaction.response.send_message(response)


# send the question to ChatGPT
async def ask(interaction: discord.Interaction, question: str):

    # Check if OpenAI is available
    if not openai_available:
        await interaction.response.send_message("Sorry, the OpenAI integration is not available. Please contact the bot administrator.")
        return
    
    # Defer the response since API calls might take some time
    await interaction.response.defer()
    
    try:
        # Get the API key from the environment variable
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            await interaction.followup.send("API key not found. Please check your environment variables.")
            return
            
        # Set the API key (in case it changed from module import)
        openai.api_key = api_key

        # Send the request to ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "You are a helpful assistant. Avoid using emojis and do not use more than 2k characters. Instead of writing a list, structure your response in a paragraph like you're personally talking to someone."
            }, {
                "role": "user",
                "content": question
            }],
            max_tokens=1000)

        # Extract the answer from the response
        answer = response.choices[0].message["content"]

        # Send the answer back to Discord
        await interaction.followup.send(answer)
        
        # Send the disclaimer as a follow-up message
        await asyncio.sleep(2)
        follow_up_message = "With that said, there is a non-zero possibility for errors. So please, take this with a grain of salt and fact-check your answers, thank you."
        await interaction.followup.send(follow_up_message)

    except Exception as e:
        await interaction.followup.send(f"Sorry, I encountered an error: {str(e)}.")
        

# purge command
async def clean(interaction: discord.Interaction, amount: int):
    
    if not isinstance(amount, int) or amount < 0:
        await interaction.response.send_message("Please enter a positive number.", ephemeral=True)
        return
    
    max_amount = 100
    
    if amount == 0:
        await interaction.response.send_message("No messages were deleted.", ephemeral=True)
        return
    
    if amount > max_amount:
        await interaction.response.send_message(f"Sorry, I can only purge up to {max_amount} messages at once.", ephemeral=True)
        return
    
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"Deleted {amount} message/s.", ephemeral=True)


# display the help list
async def helpme(interaction: discord.Interaction):
    
    embed = discord.Embed(
        title="Bot Commands",
        description="Here are all the available commands for this bot:",
        color=discord.Color.default(),
        timestamp=datetime.datetime.now()
    )

    # Add fields for each category of commands - updated for slash commands
    embed.add_field(
        name="💡 Helpful",
        value=
        "***`/help`*** - Shows this commands list.\n"
        "***`/weather`*** - Gives info on the weather in a given city.\n"
        "***`/ask`*** - Uses AI to answer your question.\n"
        "***`/exchange`*** - Converts EUR into other currencies\n",
        inline=False
    )

    embed.add_field(
        name="👮 Moderation",
        value=
        "***`/clean`*** - Purge a number of messages.\n"
        "***`/filter_add`*** - Add a word to the filter list.\n"
        "***`/filter_remove`*** - Remove a word from the filter list.\n"
        "***`/filter_list`*** - Display the current filter list.\n"
        "***`/mediafilter`*** - Toggle filtering settings for this channel.\n"
        "***`/mediafilter_show`*** - View filtering settings for this channel.",
        inline=False
    )

    embed.add_field(
        name="😆 Fun",
        value=
        "***`/token`*** - Displays the bot's token.\n"
        "***`/joke`*** - The bot will tell you a joke.\n"
        "***`/coinflip`*** - Tosses a coin.\n"
        "***`/magic_8_ball`*** - Get predictions about the future",
        inline=False
    )

    embed.add_field(
        name="🎲 Miscellaneous",
        value="***`/owner`*** - Get in contact with the developer.\n"
              "***`/donate`*** - Receive a link to my ko-fi page.\n"
              "***`/stats`*** - Returns bot's latency and RAM usage",
        inline=False
    )

    # Send the embed
    await interaction.response.send_message(embed=embed)