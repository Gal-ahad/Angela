import discord, json, os
from discord import app_commands

# Directories
media_filter_DIR = 'media_filters'
FILTER_DIR = 'filter_lists'

# Ensure the directories exist
if not os.path.exists(media_filter_DIR):
    os.makedirs(media_filter_DIR)

if not os.path.exists(FILTER_DIR):
    os.makedirs(FILTER_DIR)

# Media types that can be filtered
MEDIA_TYPES = ['images', 'videos', 'links', 'files', 'embeds']

# Dictionary to store filter lists for each server
guild_filter_lists = {}

# Dictionary to store media filter settings for each server
guild_media_filters = {}

# Get the path for a specific server's media filter settings
def get_media_filter_path(guild_id):
    return os.path.join(media_filter_DIR, f'media_filter_{guild_id}.json')

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


# Set up moderation commands
def setup_moderation_commands(moderation_group, client):
    
    # Command to toggle media filters for a channel
    @client.tree.command(name="media_filter", description="Toggle filtering of specific media types in this channel.")
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

    # Register the commands with the client
    client.tree.add_command(moderation_group)
    
    return moderation_group

# Event listener to filter media based on settings
async def on_message_filter(message, client):
    # Skip messages from the bot itself
    if message.author == client.user:
        return
    
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

# Separate function to handle word filtering
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
