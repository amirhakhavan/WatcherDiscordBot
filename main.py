import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone
# Import pytz for time zone support

# Enable intents
intents = discord.Intents.default()
intents.presences = True  # Enable presence update events
intents.members = True    # Enable member-related events
intents.messages = True   # Enable reading messages
intents.typing = True     # Enable typing events
intents.voice_states = True  # Enable voice state events

# Initialize the bot with no command prefix (we'll use slash commands)
client = commands.Bot(command_prefix="", intents=intents, application_id=1330186696091897908)

# ID of the specific channel
TARGET_CHANNEL_ID = 1330191585190875136  # Replace with your channel's ID

# Tehran timezone
tehran_tz = timezone("Asia/Tehran")

# Dictionary to store the time when a user becomes online and the activities they are doing
online_times = {}
user_activities = {}

@client.event
async def on_ready():
    try:
        # Sync slash commands with Discord's API
        await client.tree.sync()  # Sync all commands globally
        print("The bot is now ready for use!")
    except Exception as e:
        print(f"Error syncing commands: {e}")
    print("-----------------------------")

@client.event
async def on_presence_update(before, after):
    # Get the current time in Tehran timezone
    current_time_tehran = datetime.now(tehran_tz).strftime("%Y-%m-%d %H:%M:%S")

    # Get the target channel
    channel = client.get_channel(TARGET_CHANNEL_ID)

    if not channel:
        print(f"Could not find the channel with ID {TARGET_CHANNEL_ID}")
        return

    # Get the user's avatar URL
    avatar_url = after.avatar.url if after.avatar else after.default_avatar.url

    # Convert the status to a string and capitalize it
    status_string = str(after.status).capitalize()

    # Create an embed for the profile picture
    embed = discord.Embed(
        description=f"Time (Tehran): {current_time_tehran}\nStatus: {status_string}",
        color=discord.Color.green() if after.status == discord.Status.online else discord.Color.red()
    )
    embed.set_author(name=f"User `{after.name}`", icon_url=avatar_url)
    embed.set_thumbnail(url=avatar_url)

    # Check if the user's status changed to online
    if before.status != discord.Status.online and after.status == discord.Status.online:
        # Store the time when the user goes online
        online_times[after.id] = datetime.now(tehran_tz)
        user_activities[after.id] = []  # Initialize an empty list to store activities

        # Store the initial activity when the user goes online
        if after.activity:
            user_activities[after.id].append((after.activity.name, datetime.now(tehran_tz)))

        await channel.send(embed=embed)  # Send the embed when the user is online
        print(f"Notification sent in channel: {channel.name} for user {after.name}")

    # Check if the user's activity has changed (i.e., they switched apps or activities)
    if after.activity:
        # Only update if the activity has changed
        current_activity = (after.activity.name, datetime.now(tehran_tz))
        if after.id in user_activities:
            # If there are no activities recorded yet, initialize the list with the first activity
            if not user_activities[after.id]:
                user_activities[after.id].append(current_activity)
            else:
                last_activity = user_activities[after.id][-1]
                if current_activity != last_activity:
                    user_activities[after.id].append(current_activity)

    # Check if the user's status changed to offline
    elif before.status != discord.Status.offline and after.status == discord.Status.offline:
        # Calculate the total time spent online
        online_duration = datetime.now(tehran_tz) - online_times.pop(after.id, datetime.now(tehran_tz))
        online_duration_str = str(online_duration).split(".")[0]  # Format as HH:MM:SS

        # Get the activities and time spent on each
        activities = user_activities.pop(after.id, [])
        activity_summary = ""

        for activity_name, start_time in activities:
            # Calculate the duration of each activity
            activity_duration = datetime.now(tehran_tz) - start_time
            activity_duration_str = str(activity_duration).split(".")[0]
            activity_summary += f"\n- Activity: {activity_name} | Time spent: {activity_duration_str}"

        # Add the online duration and activity details to the embed description
        embed.description += f"\nTime spent online: {online_duration_str}"
        embed.description += f"\nActivities:{activity_summary}"

        await channel.send(embed=embed)  # Send the embed when the user is offline
        print(f"Notification sent in channel: {channel.name} for user {after.name}")

# Slash command to show the list of all online users with status emojis
@client.tree.command(name="onlinelist", description="Shows a list of online users with their statuses")
async def onlinelist(interaction: discord.Interaction):
    # Get the current time in Tehran timezone
    current_time_tehran = datetime.now(tehran_tz).strftime("%Y-%m-%d %H:%M:%S")

    # Get the list of online members in the server
    online_members = []
    for member in interaction.guild.members:
        if member.status == discord.Status.online:
            online_members.append(f"{member.name} 🟢")
        elif member.status == discord.Status.idle:
            online_members.append(f"{member.name} 🟡")
        elif member.status == discord.Status.dnd:
            online_members.append(f"{member.name} 🔴")

    # Count the number of online members
    online_count = len(online_members)

    # Send a message with the list of online users
    if online_count == 0:
        await interaction.response.send_message(f"No one is currently online as of {current_time_tehran}.")
    else:
        await interaction.response.send_message(
            f"Currently online ({online_count} users) as of {current_time_tehran}:\n" + "\n".join(online_members)
        )

# Replace 'your-bot-token' with the actual token of your bot


client.run("MTMzMDE4NjY5NjA5MTg5NzkwOA.GloBYh.eq9xvc13MaQuDIbj3-RnlfjmahUvvuyipjwDjM")
