import discord, os, sys, filter_module
from logging import FileHandler
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import slash_commands as slash
from typing import Literal

print("Starting the script...\n")


# Load the environment variables
try:
    load_dotenv()
    print("Environment variables loaded\n")
except Exception as e:
    print(f"Error loading environment variables: {e}\n")
    sys.exit(1)


# Set up the bot's intents
try:
    intents = discord.Intents.default()
    intents.messages = True
    intents.message_content = True
    intents.members = True
    intents.reactions = True
    print("Bot's intents have been set\n")
except Exception as e:
    print(f"Error setting intents: {e}\n")
    sys.exit(1)


# Create a bot instance
try:
    client = commands.Bot(command_prefix='ang!', intents=intents)
    print("Bot's instance has been created\n")
except Exception as e:
    print(f"Error creating bot instance: {e}\n")
    sys.exit(1)


# setup logging
try:
    handler = FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    print("Logging has been setup\n")
except Exception as e:
    print(f"Error setting up logging: {e}\n")
    handler = None


# Share the client instance with the slash_commands module
slash.set_client(client)


# start the bot
@client.event
async def on_ready():
    print(f'Successfully logged in as {client.user.name}.\n')

    # sync commands with discord
    try:
        print("Attempting to sync commands...\n")
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands.")
        for cmd in synced:
            print(f"  - Synced: {cmd.name}.")
    except Exception as error:
        print(f"Failed to sync commands: {error}.")
    finally:
        print("\nBot is now operational")


# Event listener to handle messages
@client.event
async def on_message(message):
    # Skip messages from the bot itself
    if message.author == client.user:
        return
    
    # Process commands
    await client.process_commands(message)
    
    # Use the NSFW filter module
    await filter_module.on_message_filter(message, client)

# rock, paper, scissors

@client.tree.command(name="rps", description="Play a game of rock, paper, scissors.")
async def rps(
    interaction: discord.Interaction,
    option: Literal["Rock", "Paper", "Scissors"]
    ):
    await slash.rps(interaction, option)

# clean command
@client.tree.command(name="clean", description="Clean a certain amount of messages")
async def clean(interaction: discord.Interaction, amount: int):
    await slash.clean(interaction, amount)

# coinflip command
@client.tree.command(name="coinflip", description="Flip a coin! Let destiny decide.")
async def coin(interaction: discord.Interaction):
    await slash.coin(interaction)


# exchange rate command
@client.tree.command(name="exchange", description="Convert an amount from EUR to a target currency.")
@app_commands.describe(amount="The amount of EUR you want to convert", target_currency="The 3-letter currency code (e.g., USD, GBP, JPY)")
async def get_exchange_rate(interaction: discord.Interaction, amount: float, target_currency: str):
    await slash.get_exchange_rate_implementation(interaction, amount, target_currency)


# ping and RAM
@client.tree.command(name="stats", description="Shows latency and RAM usage")
async def stats(interaction: discord.Interaction):
    await slash.stats(interaction, client)


# token command
@client.tree.command(name="token", description="Displays the bot's token.")
async def token(interaction: discord.Interaction):
    await slash.token(interaction)


# donate command
@client.tree.command(name="donate", description="Toss me a euro or two if you want.")
async def donate(interaction: discord.Interaction):
    await slash.donate(interaction)


# weather command
@client.tree.command(name="weather", description="Get info about the weather.")
@app_commands.describe(location="The desired city")
async def weather(interaction: discord.Interaction, location: str):
    await slash.weather(interaction, location)


# credits the developer
@client.tree.command(name="owner", description="Get info about me, the developer.")
async def owner(interaction: discord.Interaction):
    await slash.owner(interaction)


# magic 8 ball
@client.tree.command(name="magic_8_ball", description="Get predictions about the future, 100% trustworthy")
@app_commands.describe(message="What would you like to know?")
async def magic8ball(interaction: discord.Interaction, message: str):
    await slash.magic8ball(interaction, message)


# ask command
@client.tree.command(name="ask", description="Ask and receive an AI response.")
@app_commands.describe(question="Ask and ye shall receive!")
async def ask(interaction: discord.Interaction, question: str):
    await slash.ask(interaction, question)


# send a joke
@client.tree.command(name="joke", description="Wanna hear a joke?.")
async def joke(interaction: discord.Interaction):
    await slash.joke(interaction)


# send a list of commands
@client.tree.command(name="help", description="Shows a list of commands.")
async def helpme(interaction: discord.Interaction):
    await slash.helpme(interaction)


# Run the bot
def main():
    try:
        bot_token = os.getenv("TOKEN")
        if not bot_token:
            print("Error: No Discord token found. Please set TOKEN environment variable.")
            sys.exit(1)

        client.run(bot_token, log_handler=handler)

    except Exception as error:
        print(f"An error occurred: {error}.")
        sys.exit(1)


# make sure the bot is run directly
if __name__ == '__main__':
    main()
else:
    print("Please run the Angela.py file directly.")