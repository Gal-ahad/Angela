import discord, os, sys
from logging import FileHandler
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import slash_commands as slash

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


# filter
import json

# Directories
MEDIA_FILTER_DIR = 'media_filters'
FILTER_DIR = 'filter_lists'

# Ensure the directories exist
if not os.path.exists(MEDIA_FILTER_DIR):
    os.makedirs(MEDIA_FILTER_DIR)

if not os.path.exists(FILTER_DIR):
    os.makedirs(FILTER_DIR)

# Media types that can be filtered
MEDIA_TYPES = ['images', 'videos', 'links', 'files', 'embeds']

# Get the path for a specific server's media filter settings
def get_media_filter_path(guild_id):
    return os.path.join(MEDIA_FILTER_DIR, f'media_filter_{guild_id}.json')

# Get the path for a specific server's filter list
def get_filter_path(guild_id):
    return os.path.join(FILTER_DIR, f'filter_list_{guild_id}.json')

# Load or create the media filter settings for a specific server
def load_media_filters(guild_id):
    file_path = get_media_filter_path(guild_id)
    
    try:
        with open(file_path, 'r') as f:
            media_filters = json.load(f)
            print(f"Media filter settings for server {guild_id} loaded successfully.\n")

    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Media filter settings for server {guild_id} not found or corrupted. Creating new settings.\n")
        # Default structure: {channel_id: {media_type: is_filtered}}
        media_filters = {}

        with open(file_path, 'w') as f:
            json.dump(media_filters, f, indent=2)

    return media_filters

# Load or create the filter list for a specific server
def load_filter_list(guild_id):
    file_path = get_filter_path(guild_id)
    
    try:
        with open(file_path, 'r') as f:
            filter_list = json.load(f)
            print(f"Filter list for server {guild_id} loaded successfully.\n")

    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Filter list for server {guild_id} not found or corrupted. Creating a new one.\n")
        filter_list = []

        with open(file_path, 'w') as f:
            json.dump(filter_list, f, indent=2)

    return filter_list

# Dictionary to store filter lists for each server
guild_filter_lists = {}

# Dictionary to store media filter settings for each server
guild_media_filters = {}

# Command to toggle media filters for a channel
@client.tree.command(name="media-filter", description="Toggle filtering of specific media types in this channel.")
@app_commands.describe(media_type="The type of media to filter (images, videos, links, files, embeds)",action="Turn the filter on or off")
@app_commands.choices(media_type=[
        app_commands.Choice(name="Images", value="images"),
        app_commands.Choice(name="Videos", value="videos"),
        app_commands.Choice(name="Links", value="links"),
        app_commands.Choice(name="Files", value="files"),
        app_commands.Choice(name="Embeds", value="embeds")
    ],action=[app_commands.Choice(name="On", value="on"),app_commands.Choice(name="Off", value="off")])

async def media_filter(interaction: discord.Interaction, media_type: str, action: str):
    # Check if the user has the admin role or is the server owner

    admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
    is_admin = (admin_role and admin_role in interaction.user.roles)
    is_owner = (interaction.user.id == interaction.guild.owner_id)
    
    if not (is_admin or is_owner):
        await interaction.response.send_message("You need to be the server owner or have the Admin role to use this command.", ephemeral=True)
        return

    # Validate media type
    if media_type not in MEDIA_TYPES:
        await interaction.response.send_message(f"Invalid media type. Choose from: {', '.join(MEDIA_TYPES)}", ephemeral=True)
        return

    # Get or load media filter settings for this server
    guild_id = interaction.guild.id

    if guild_id not in guild_media_filters:
        guild_media_filters[guild_id] = load_media_filters(guild_id)
    
    media_filters = guild_media_filters[guild_id]
    
    # Convert channel ID to string for JSON compatibility
    channel_id = str(interaction.channel.id)
    
    # Initialize channel settings if needed
    if channel_id not in media_filters:
        media_filters[channel_id] = {}
    
    # Set the filter status
    is_filtered = action.lower() == "on"
    media_filters[channel_id][media_type] = is_filtered
    
    # Save the settings
    with open(get_media_filter_path(guild_id), 'w') as f:
        json.dump(media_filters, f, indent=2)
    
    status = "enabled" if is_filtered else "disabled"
    await interaction.response.send_message(f"{media_type.capitalize()} filtering has been {status} in this channel.", ephemeral=False)

# Command to view current media filter settings for a channel
@client.tree.command(name="media_filter_status", description="Show the current media filter settings for this channel.")
async def media_filter_status(interaction: discord.Interaction):

    # Get or load media filter settings for this server
    guild_id = interaction.guild.id

    if guild_id not in guild_media_filters:
        guild_media_filters[guild_id] = load_media_filters(guild_id)
    
    media_filters = guild_media_filters[guild_id]
    
    # Convert channel ID to string for JSON compatibility
    channel_id = str(interaction.channel.id)
    
    embed = discord.Embed(
        title=f"Media Filter Status for #{interaction.channel.name}",
        description="Current media filter settings for this channel:",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    
    if channel_id not in media_filters:
        status_text = "No media filters are active in this channel."
    else:
        status_lines = []
        for media_type in MEDIA_TYPES:
            is_filtered = media_filters[channel_id].get(media_type, False)
            status = "🟢 Allowed" if not is_filtered else "🔴 Filtered"
            status_lines.append(f"**{media_type.capitalize()}**: {status}")
        status_text = "\n".join(status_lines)
    
    embed.add_field(name="Settings", value=status_text, inline=False)
    
    await interaction.response.send_message(embed=embed)

# Event listener to filter media based on settings
@client.event
async def on_message(message):
    # Skip messages from the bot itself

    if message.author == client.user:
        return
    
    # Process commands
    await client.process_commands(message)
    
    # Skip if not in a guild
    if not message.guild:
        return

    # Load media filter settings for this server if needed
    guild_id = message.guild.id

    if guild_id not in guild_media_filters:
        guild_media_filters[guild_id] = load_media_filters(guild_id)
    
    media_filters = guild_media_filters[guild_id]
    
    # Skip if no filter settings for this channel
    channel_id = str(message.channel.id)

    if channel_id not in media_filters:
        # Continue with word filtering
        await handle_word_filtering(message)
        return
    
    channel_settings = media_filters[channel_id]
    
    # Check for various media types
    should_delete = False
    filtered_types = []
    
    # Check for images
    if channel_settings.get('images', False) and message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                should_delete = True
                filtered_types.append('images')
                break
    
    # Check for videos
    if channel_settings.get('videos', False) and message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('video/'):
                should_delete = True
                filtered_types.append('videos')
                break
    
    # Check for links
    if channel_settings.get('links', False) and any(url in message.content for url in ['http://', 'https://']):
        should_delete = True
        filtered_types.append('links')
    
    # Check for files
    if channel_settings.get('files', False) and message.attachments:
        for attachment in message.attachments:
            if not (attachment.content_type and (attachment.content_type.startswith('image/') or attachment.content_type.startswith('video/'))):
                should_delete = True
                filtered_types.append('files')
                break
    
    # Check for embeds
    if channel_settings.get('embeds', False) and message.embeds:
        should_delete = True
        filtered_types.append('embeds')
    
    # Delete the message if it contains filtered media
    if should_delete:
        try:
            await message.delete()
            print(f"Server {guild_id}, Channel {channel_id}: Deleted message containing filtered media types: {', '.join(filtered_types)}")
            
            # Notify the user
            types_str = ', '.join(filtered_types)
            await message.channel.send(
                f"{message.author.mention}, your message was deleted because {types_str} are not allowed in this channel.", 
                delete_after=10
            )
        except Exception as error:
            print(f"Failed to delete message or send notification: {error}")
    else:
        # Continue with word filtering if media filtering didn't trigger
        await handle_word_filtering(message)

# Separate function to handle word filtering - with fixed await statements
async def handle_word_filtering(message):
    # Get or load the filter list for this server
    guild_id = message.guild.id
    if guild_id not in guild_filter_lists:
        guild_filter_lists[guild_id] = load_filter_list(guild_id)
    
    current_filter_list = guild_filter_lists[guild_id]
    
    # Check for banned words
    banned_words = [word for word in current_filter_list if word.lower() in message.content.lower()]
    if banned_words:
        try:
            await message.delete()
            print(f"Server {guild_id}: Deleted message containing banned words: {', '.join(banned_words)}")
        except Exception as error:
            print(f"Failed to delete message: {error}")
        try:
            await message.channel.send(
                f"{message.author.mention}, your message was deleted for containing the following banned word/s: {', '.join(banned_words)}", 
                delete_after=10
            )
        except Exception as error:
            print(f"Failed to send reply to offending user: {error}")


# add to filter
@client.tree.command(name="filter_add", description="Add a word to the list of filtered words.")
@app_commands.describe(word="The word to add to the filter list")
async def add_to_filter(interaction: discord.Interaction, word: str):

    # Check if the user has the admin role or is the server owner
    admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
    
    is_admin = (admin_role and admin_role in interaction.user.roles)
    is_owner = (interaction.user.id == interaction.guild.owner_id)
    
    if not (is_admin or is_owner):
        await interaction.response.send_message("You need to be the server owner or have the Admin role to use this command.", ephemeral=True)
        return

    # Get or load the filter list for this server
    guild_id = interaction.guild.id
    if guild_id not in guild_filter_lists:
        guild_filter_lists[guild_id] = load_filter_list(guild_id)
    
    current_filter_list = guild_filter_lists[guild_id]
    
    # Add the word
    if word.lower() in [w.lower() for w in current_filter_list]:
        await interaction.response.send_message("Word already in list.", ephemeral=True)
        return
    
    current_filter_list.append(word.lower())
    with open(get_filter_path(guild_id), 'w') as f:
        json.dump(current_filter_list, f, indent=2)
    
    await interaction.response.send_message(f"Added '{word}' to the filter list.", ephemeral=True)


# purge command
@client.tree.command(name="clean", description="Clean the channel from unwanted messages")
@app_commands.describe(amount="The amount of messages to purge (max 100)")
async def purge(interaction: discord.Interaction, amount: int):
    await slash.clean(interaction, amount)


@client.tree.command(name="filter_remove", description="Remove a word from the list of filtered words.")
@app_commands.describe(word="The word to remove from the filter list")
async def remove_from_filter(interaction: discord.Interaction, word: str):
    # Check if the user has the admin role or is the server owner
    admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
    is_admin = (admin_role and admin_role in interaction.user.roles)
    is_owner = (interaction.user.id == interaction.guild.owner_id)
    
    if not (is_admin or is_owner):
        await interaction.response.send_message("You need to be the server owner or have the Admin role to use this command.", ephemeral=True)
        return

    # Get or load the filter list for this server
    guild_id = interaction.guild.id
    if guild_id not in guild_filter_lists:
        guild_filter_lists[guild_id] = load_filter_list(guild_id)
    
    current_filter_list = guild_filter_lists[guild_id]
    
    # Find the word (case-insensitive)
    word_lower = word.lower()
    matching_words = [w for w in current_filter_list if w.lower() == word_lower]
    
    if not matching_words:
        await interaction.response.send_message("Word not found in list.", ephemeral=True)
        return

    # Remove the word
    for match in matching_words:
        current_filter_list.remove(match)
    
    with open(get_filter_path(guild_id), 'w') as f:
        json.dump(current_filter_list, f, indent=2)
    
    await interaction.response.send_message(f"Removed '{word}' from the filter list.", ephemeral=True)


@client.tree.command(name="filter_list", description="Show the current list of filtered words.")
async def show_filter(interaction: discord.Interaction):
    # Check if the user has the admin role or is the server owner
    admin_role = discord.utils.get(interaction.guild.roles, name="Admin")
    is_admin = (admin_role and admin_role in interaction.user.roles)
    is_owner = (interaction.user.id == interaction.guild.owner_id)
    
    if not (is_admin or is_owner):
        await interaction.response.send_message("You need to be the server owner or have the Admin role to view the filter list.", ephemeral=True)
        return

    # Get or load the filter list for this server
    guild_id = interaction.guild.id
    if guild_id not in guild_filter_lists:
        guild_filter_lists[guild_id] = load_filter_list(guild_id)
    
    current_filter_list = guild_filter_lists[guild_id]

    embed = discord.Embed(
        title="Filtered Words",
        description=f"These words are currently filtered from this server.",
        color=discord.Color.default(),
        timestamp=discord.utils.utcnow()
    )
    
    words_text = "\n".join(current_filter_list) if current_filter_list else "No filtered words"
    embed.add_field(name="Words", value=words_text, inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)


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