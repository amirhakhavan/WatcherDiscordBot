import os
import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone

# Enable intents
intents = discord.Intents.default()
intents.presences = True  # Enable presence update events
intents.members = True    # Enable member-related events
intents.messages = True   # Enable reading messages
intents.typing = True     # Enable typing events
intents.voice_states = True  # Enable voice state events

# Initialize the bot
client = commands.Bot(command_prefix="", intents=intents, application_id=1330186696091897908)

# ID of the specific channel
TARGET_CHANNEL_ID = 1330191585190875136  # Replace with your channel's ID

# Tehran timezone
tehran_tz = timezone("Asia/Tehran")

# Dictionary to store the time when a user becomes online and their activities
online_times = {}
user_activities = {}

@client.event
async def on_ready():
    try:
        # Sync slash commands with Discord's API
        await client.tree.sync()
        print("The bot is now ready for use!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print("-----------------------------")

@client.event
async def on_presence_update(before, after):
    current_time_tehran = datetime.now(tehran_tz).strftime("%Y-%m-%d %H:%M:%S")
    channel = client.get_channel(TARGET_CHANNEL_ID)

    if not channel:
        print(f"Could not find the channel with ID {TARGET_CHANNEL_ID}")
        return

    avatar_url = after.avatar.url if after.avatar else after.default_avatar.url
    status_string = str(after.status).capitalize()

    embed = discord.Embed(
        description=f"Time (Tehran): {current_time_tehran}\nStatus: {status_string}",
        color=discord.Color.green() if after.status == discord.Status.online else discord.Color.red()
    )
    embed.set_author(name=f"User `{after.name}`", icon_url=avatar_url)
    embed.set_thumbnail(url=avatar_url)

    if before.status != discord.Status.online and after.status == discord.Status.online:
        online_times[after.id] = datetime.now(tehran_tz)
        user_activities[after.id] = []
        if after.activity:
            user_activities[after.id].append((after.activity.name, datetime.now(tehran_tz)))

        await channel.send(embed=embed)
        print(f"Notification sent in channel: {channel.name} for user {after.name}")

    elif before.status != discord.Status.offline and after.status == discord.Status.offline:
        online_duration = datetime.now(tehran_tz) - online_times.pop(after.id, datetime.now(tehran_tz))
        online_duration_str = str(online_duration).split(".")[0]

        activities = user_activities.pop(after.id, [])
        activity_summary = ""
        for activity_name, start_time in activities:
            activity_duration = datetime.now(tehran_tz) - start_time
            activity_duration_str = str(activity_duration).split(".")[0]
            activity_summary += f"\n- Activity: {activity_name} | Time spent: {activity_duration_str}"

        embed.description += f"\nTime spent online: {online_duration_str}"
        embed.description += f"\nActivities:{activity_summary}"

        await channel.send(embed=embed)
        print(f"Notification sent in channel: {channel.name} for user {after.name}")

@client.tree.command(name="onlinelist", description="Shows a list of online users with their statuses")
async def onlinelist(interaction: discord.Interaction):
    current_time_tehran = datetime.now(tehran_tz).strftime("%Y-%m-%d %H:%M:%S")
    online_members = []
    for member in interaction.guild.members:
        if member.status == discord.Status.online:
            online_members.append(f"{member.name} 🟢")
        elif member.status == discord.Status.idle:
            online_members.append(f"{member.name} 🟡")
        elif member.status == discord.Status.dnd:
            online_members.append(f"{member.name} 🔴")

    online_count = len(online_members)
    if online_count == 0:
        await interaction.response.send_message(f"No one is currently online as of {current_time_tehran}.")
    else:
        await interaction.response.send_message(
            f"Currently online ({online_count} users) as of {current_time_tehran}:\n" + "\n".join(online_members)
        )

# Retrieve the token from environment variables
Token = os.getenv("DISCORD_BOT_TOKEN")

if not Token:
    raise ValueError("DISCORD_BOT_TOKEN is not set in environment variables!")

# Run the bot
client.run(Token)
