import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import aiosqlite
import os

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

async def setup_database():
async with aiosqlite.connect("pulse.db") as db:
await db.execute(
"""
CREATE TABLE IF NOT EXISTS messages (
message_id INTEGER PRIMARY KEY,
user_id INTEGER NOT NULL,
guild_id INTEGER NOT NULL,
channel_id INTEGER NOT NULL,
timestamp TEXT NOT NULL
)
"""
)

await db.execute(  
        """  
        CREATE TABLE IF NOT EXISTS server_settings (  
        guild_id INTEGER PRIMARY KEY,  
        server_type TEXT,  
        analytics_enabled INTEGER  
        )  
        """)  
      
    await db.commit()  

    print("Database tables created successfully!")

@bot.event
async def on_ready():
await setup_database()
synced = await bot.tree.sync()
print(f'Synced {len(synced)} commands!')
print(f'Pulse is online! Logged in as {bot.user}')

@bot.tree.command(name = "dashboard", description = "Show members, messages, topusers and active channels")
async def dashboard(interaction:discord.Interaction):
async with aiosqlite.connect("pulse.db") as db:
cursor = await db.execute("SELECT COUNT(*) FROM messages")
total_messages = (await cursor.fetchone())[0]

cursor = await db.execute("SELECT COUNT(DISTINCT user_id) FROM messages")  
    unique_users = (await cursor.fetchone())[0]  

    cursor =await db.execute("SELECT COUNT(DISTINCT channel_id) FROM messages")  
    active_channels = (await cursor.fetchone())[0]  

    await interaction.response.send_message(  
        f"📊 **Pulse Dashboard**\n\n"  
        f"💬 Messages : {total_messages}\n"  
        f"👥 Users : {unique_users}\n"  
        f"📺 Channels : {active_channels}"  
    )

@bot.tree.command(name = "userinfo", description = "View a users stats")
async def userinfo(interaction:discord.Interaction, member: discord.Member):
async with aiosqlite.connect("pulse.db") as db:
cursor = await db.execute("""
SELECT COUNT(*)
FROM messages
WHERE user_id = ?""", (member.id,))

message_count = (await cursor.fetchone())[0]  

    await interaction.response.send_message(  
        f"👤 **USER INFO**\n\n"  
        f"🏷 Name : {member.name}\n"  
        f"🆔 ID : {member.id}\n"  
        f"💬 Messages : {message_count}"  
    )

@bot.tree.command(name = "activity", description = "View activity statistics")
async def activity(interaction:discord.Interaction):
async with aiosqlite.connect("pulse.db") as db:
cursor = await db.execute(
"SELECT COUNT(*) FROM messages"
)

total = (await cursor.fetchone())[0]  

    await interaction.response.send_message(  
        f"**Activity Report**\n\n"  
        f"Total Messages : {total}"  
    )

@bot.tree.command(name = "leaderboard", description = "View server leaderboard")
async def leaderboard(interaction:discord.Interaction):
async with aiosqlite.connect("pulse.db") as db:
cursor = await db.execute("""
SELECT user_id,
COUNT(*) as count
FROM messages
GROUP BY user_id
ORDER BY count DESC
LIMIT 5
""")

results = await cursor.fetchall()  

    text = "🏆**Leaderboard**\n\n"  

    for i, (user_id, count) in enumerate(results, start=1):  
        user = interaction.guild.get_member(user_id)  
        name = user.display_name if user else f"User {user_id}"  

        text += (  
            f"{i}. {name} - {count} messages\n"  
        )  

    await interaction.response.send_message(text)

@bot.tree.command(name = "stats", description = "Show server statistics")
async def stats(interaction:discord.Interaction):
async with aiosqlite.connect("pulse.db") as db:
cursor = await db.execute("SELECT COUNT(*) FROM messages")
total_messages = (await cursor.fetchone())[0]

cursor = await db.execute("SELECT COUNT(DISTINCT user_id) FROM messages")  
    unique_users = (await cursor.fetchone())[0]  
      
    cursor = await db.execute("SELECT COUNT(DISTINCT channel_id) FROM messages")  
    active_channels = (await cursor.fetchone())[0]  

stats_message = (  
    f"📊 **Server Stats\n\n**"  
    f"💬 Total Messages: {total_messages}\n"  
    f"👥 Unique Users: {unique_users}\n"  
    f"📺 Active Channels: {active_channels}"  
)  
await interaction.response.send_message(stats_message)

@bot.tree.command(name = "topusers", description ="Show the most active users")
async def topusers(interaction:discord.Interaction):
async with aiosqlite.connect("pulse.db") as db:
cursor = await db.execute(
"""
SELECT user_id, COUNT(*) as message_count
FROM messages
GROUP BY user_id
ORDER BY message_count DESC
LIMIT 3
"""
)

results = await cursor.fetchall()  

if not results:  
    await interaction.response.send_message("No message data available.")  
    return  
  
medals = ["🥇", "🥈", "🥉"]  

message = "🏆 **Top Users**\n\n"  

for i, (user_id, count) in enumerate(results):  
    user = await bot.fetch_user(user_id)  

    message += (f"{medals[i]}"  
                f"{user.name} - {count} messages\n")  
      
await interaction.response.send_message(message)

@bot.tree.command(name = "serverinfo", description ="Show information about this server")
async def serverinfo(interaction:discord.Interaction):
guild = interaction.guild

owner = guild.owner  
member_count = guild.member_count  
channel_count = len(guild.channels)  
online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)  
offline_members = member_count - online_members  

await interaction.response.send_message(  
    f"📔 **Server Info**\n\n"  
    f"🏷 Name : {guild.name}\n"  
    f"👑 Owner : {owner}\n"  
    f"👥 Members : {member_count}\n"  
    f"🟢 Online : {online_members}\n"  
    f"⚫ Offline : {offline_members}\n"  
    f"💬 Channels : {channel_count}\n"  
    f"🆔 Server ID : {guild.id}"  
)

@bot.tree.command(name = "topchannels", description = "Show the most active channels")
async def topchannels(interaction:discord.Interaction):
async with aiosqlite.connect("pulse.db") as db:
cursor = await db.execute(
"""
SELECT channel_id, COUNT(*) as message_count
FROM messages
GROUP BY channel_id
ORDER BY message_count DESC
LIMIT 3
"""
)

results = await cursor.fetchall()  

if not results:  
    await interaction.response.send_message("No message data available.")  
    return  
  
medals = ["🥇", "🥈", "🥉"]  

message = "🏆 **Top Channels**\n\n"  

for i, (channel_id, count) in enumerate(results):  
    channel = bot.get_channel(channel_id)  

    if channel is None:  
        continue  

    message += (f"{medals[i]}"  
                f"{channel.name} - {count} messages\n")  
      
await interaction.response.send_message(message)

@bot.tree.command(name = "about", description = "Features of PulseBOT")
async def about(interaction:discord.interactions):
await interaction.response.send_message(
"🤖 PulseBOT v0.1\n\n"
"👨‍💻 **Developed by : **  Chris Lepcha\n\n"
"**Features : **\n"
"✅ Analytics\n"
"✅ Welcome Messages\n"
"✅ Leaderboards\n"
"✅ Activity Tracking")

@bot.event
async def on_member_join(member):
channel = discord.utils.get(member.guild.channels, name="welcome")

if not channel:  
    return  
  
embed = discord.Embed(  
    title=f"Welcome {member.name}!",  
    description=f"Hey {member.mention}, welcome to {member.guild.name}!",  
    color=discord.Color.blurple()  
)  
embed.add_field(name="Members", value=f"{member.guild.member_count}", inline=False)  
embed.set_thumbnail(url=member.avatar.url if member.avatar else None)  
  
await channel.send(embed=embed)

@bot.event
async def on_message(message):
if message.author.bot:
return

if message.guild is None:  
    return  
  
async with aiosqlite.connect("pulse.db") as db:  
    await db.execute(  
        """  
        INSERT INTO messages (message_id,   
        user_id,   
        guild_id,   
        channel_id,   
        timestamp)  
        VALUES (?, ?, ?, ?, ?)  
        """,  
        (  
            message.id,  
            message.author.id,  
            message.guild.id,  
            message.channel.id,  
            str(message.created_at)  
        )  
    )  
    await db.commit()  
await bot.process_commands(message)

bot.run(BOT_TOKEN)