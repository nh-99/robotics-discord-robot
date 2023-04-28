from typing import Optional

from timeloop import Timeloop
from datetime import timedelta
import discord
import settings
import tiktok_video_scraper
import youtube_video_scraper
import os
import re
import asyncio
import openai
from discord import app_commands


MY_GUILD = discord.Object(id=settings.GUILD_ID)  # replace with your guild id
tl = Timeloop()
openai.api_key = settings.OPENAI_API_KEY


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author.id == self.user.id:
            return

        if client.user in message.mentions:
            content_filtered = re.search(r'<[@0-9]+> (.*)', message.content)
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
                {"role": "system", "content": "From now on, you are going to act like the famous painter Bob Ross. Thank you."},
                {"role": "user", "content": content_filtered.group(1).strip()},
                {"role": "system", "content": "Keep the response size to a short paragraph."},
            ])
            await message.reply(completion.choices[0].message.content, mention_author=True)


intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

    # Set bot status
    await client.change_presence(activity=discord.Game(name="oil paints on canvas"))


@client.tree.command()
@app_commands.describe(
    social_media='The social media (either youtube or tiktok)',
    username='The value you want to add to the first value (for youtube use channel ID)',
)
async def subscribe(interaction: discord.Interaction, social_media: str, username: str, channel: discord.TextChannel):
    """Subscribe to socials"""

    # Open file for storing data, or send error
    if social_media != 'tiktok' and social_media != 'youtube':
        interaction.response.send_message(f'Invalid social media {social_media}', ephemeral=True)
    
    datafile = open(f"./data/subscribed_{social_media}_{username}_{channel.id}.txt", "w+")

    # Cache data in file
    datafile.write(" ")
    datafile.close()

    await interaction.response.send_message(f'Subscribed to {username} on {social_media} in #{channel}', ephemeral=True)


# A Context Menu command is an app command that can be run on a member or on a message by
# accessing a menu within the client, usually via right clicking.
# It always takes an interaction as its first parameter and a Member or Message as its second parameter.

# This context menu command only works on members
@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}', ephemeral=True)


@tl.job(interval=timedelta(minutes=10))
def check_videos():
    subscribed_channel_files = os.listdir('./data')

    # tiktok
    subscribed_tiktok_channel_files = list(filter(lambda x: x.startswith('subscribed_tiktok_'), subscribed_channel_files))
    for channel_file in subscribed_tiktok_channel_files:
        filename_regex = r'(.*)_(.*)_(.*)_(.*).txt'
        datafile = open('./data/' + channel_file, "r")
        match = re.search(filename_regex, channel_file)
        username = match.group(3)
        discord_channel_id = match.group(4)
        latest_video_url = tiktok_video_scraper.get_latest_video_url(username=username)
        last_video_url = datafile.read()
        datafile.close()

        if latest_video_url != last_video_url:
            datafile = open('./data/' + channel_file, "w")
            print(f'[tiktok] New video url: {latest_video_url}')
            # Cache url
            datafile.write(latest_video_url)
            datafile.close()
            
            channel = client.get_channel(int(discord_channel_id))
            client.loop.create_task(channel.send(f"{latest_video_url}"))

    # youtube
    subscribed_youtube_channel_files = list(filter(lambda x: x.startswith('subscribed_youtube_'), subscribed_channel_files))
    for channel_file in subscribed_youtube_channel_files:
        filename_regex = r'subscribed_youtube_(.*)_(.*).txt'
        datafile = open('./data/' + channel_file, "r")
        match = re.search(filename_regex, channel_file)
        channel_id = match.group(1)
        discord_channel_id = match.group(2)
        latest_video_url = youtube_video_scraper.get_latest_video_url(channel_id=channel_id)
        last_video_url = datafile.read()
        datafile.close()

        if latest_video_url != last_video_url:
            datafile = open('./data/' + channel_file, "w")
            print(f'[youtube] New video url: {latest_video_url}')
            # Cache url
            datafile.write(latest_video_url)
            datafile.close()
            
            channel = client.get_channel(int(discord_channel_id))
            client.loop.create_task(channel.send(f"{latest_video_url}"))


while True:
    try:
        tl.start()
        client.run(settings.BOT_TOKEN)
    except:
        tl.stop()
        break
