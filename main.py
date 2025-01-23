from builtins import str
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

# Initialize the bot with no command prefix (we'll use slash commands)
client = commands.Bot(command_prefix="", intents=intents, application_id=1330186696091897908)

# ID of the specific channel
TARGET_CHANNEL_ID = 1330191585190875136  # Replace with your channel's ID

DISCORD_TOKEN_BOT = ""  # Replace with your bot's token

# Tehran timezone
tehran_tz = timezone("Asia/Tehran")

# Dictionary to store user session details
online_times = {}


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
    now = datetime.now(tehran_tz)

    # Get the target channel
    channel = client.get_channel(TARGET_CHANNEL_ID)

    if not channel:
        print(f"Could not find the channel with ID {TARGET_CHANNEL_ID}")
        return

    # Embed colors for statuses
    status_color = {
        discord.Status.online: discord.Color.green(),
        discord.Status.idle: discord.Color.gold(),
        discord.Status.dnd: discord.Color.red(),
        discord.Status.offline: discord.Color.light_grey(),
    }.get(after.status, discord.Color.default())

    # Get the user's avatar URL
    avatar_url = after.avatar.url if after.avatar else after.default_avatar.url

    # Convert the status to a string and capitalize it
    status_string = str(after.status).capitalize()

    # Create an embed
    embed = discord.Embed(description=f"Status: {status_string}", color=status_color)
    embed.set_author(name=f"User {after.name}", icon_url=avatar_url)
    embed.set_thumbnail(url=avatar_url)

    # Initialize session for the user if not already tracked
    if after.id not in online_times:
        online_times[after.id] = {
            "status": after.status,
            "online_since": now,
            "activities": []
        }

    # Record the current activities
    current_activities = [activity.name for activity in after.activities if activity.name]
    if current_activities:
        online_times[after.id]["activities"].extend(current_activities)
        online_times[after.id]["activities"] = list(set(online_times[after.id]["activities"]))

    # Handle status transitions
    if before.status == discord.Status.offline and after.status == discord.Status.online:
        online_times[after.id]["online_since"] = now
        embed.description = f"User {after.name} is now online!"
        await channel.send(embed=embed)

    elif after.status == discord.Status.idle and before.status != discord.Status.idle:
        embed.description = f"User {after.name} is now away."
        await channel.send(embed=embed)

    elif before.status == discord.Status.idle and after.status == discord.Status.online:
        embed.description = f"User {after.name} is back online."
        await channel.send(embed=embed)

    elif after.status == discord.Status.dnd and before.status != discord.Status.dnd:
        embed.description = f"User {after.name} is now in Do Not Disturb (DND) mode."
        await channel.send(embed=embed)

    elif before.status == discord.Status.dnd and after.status == discord.Status.online:
        embed.description = f"User {after.name} is no longer in Do Not Disturb (DND) mode."
        await channel.send(embed=embed)

    elif before.status != discord.Status.offline and after.status == discord.Status.offline:
        session = online_times.pop(after.id, None)
        if session:
            online_duration = now - session["online_since"]
            duration_str = str(online_duration).split(".")[0]
            activities_str = ", ".join(session["activities"]) or "No recorded activities."

            embed.description = (
                f"User {after.name} is now offline.\n"
                f"Time spent online: {duration_str}\n"
                f"Activities during session: {activities_str}"
            )
            await channel.send(embed=embed)


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


# Run the bot
client.run(DISCORD_TOKEN_BOT)
