import discord
from discord.ext import commands
import threading
import asyncio
from flask import Flask, render_template, request, redirect
import os

# Define intents (these determine which events your bot can receive)
intents = discord.Intents.default()
intents.messages = True  # Enable receiving messages
intents.guilds = True  # Enable receiving guild events (server events)
intents.members = True  # Enable receiving member events (required for mute/warn)
intents.message_content = True  # To access message content

# Create the bot instance with the intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Flask App Initialization
app = Flask(__name__)

# Load warns for the admin panel
def load_warns():
    if os.path.exists("warns.txt"):
        with open("warns.txt", "r") as f:
            warns = [line.strip().split(":", 3) for line in f.readlines()]
        return warns
    return []

# Route to display the admin panel with a list of servers
@app.route('/')
def dashboard():
    guilds = [{'id': 1234567890, 'name': 'Server 1'}, {'id': 9876543210, 'name': 'Server 2'}]  # Example
    return render_template('admin.html', guilds=guilds)

# Route to show server details and warnings
@app.route('/server/<int:guild_id>')
def server_details(guild_id):
    warns = load_warns()
    server_warns = [w for w in warns if w[0] == str(guild_id)]
    return render_template('server_details.html', guild_id=guild_id, warns=server_warns)

# Route to clear a specific warning via admin panel
@app.route('/server/<int:guild_id>/clearwarn', methods=['POST'])
def clear_warn_web(guild_id):
    user_id = request.form['user_id']
    warn_number = int(request.form['warn_number'])

    warns = load_warns()
    server_warns = [w for w in warns if w[0] == str(guild_id) and w[1] == user_id]
    if 0 < warn_number <= len(server_warns):
        warn_indices = [i for i, w in enumerate(warns) if w[0] == str(guild_id) and w[1] == user_id]
        warn_index = warn_indices[warn_number - 1]
        remove_warn(guild_id, user_id, warn_index)
        return redirect(f'/server/{guild_id}')
    else:
        return "Invalid warning number."

# Helper function to remove a specific warn
def remove_warn(server_id, user_id, warn_index):
    warns = load_warns()
    warns_to_keep = [w for i, w in enumerate(warns) if not (w[0] == str(server_id) and w[1] == str(user_id) and i == warn_index)]
    with open("warns.txt", "w") as f:
        for w in warns_to_keep:
            f.write(f"{w[0]}:{w[1]}:{w[2]}\n")

# Function to run Flask app in a separate thread
def run_flask():
    app.run(debug=True, use_reloader=False)

# Helper function to load warns from the text file for the bot
def load_warns_for_bot():
    if os.path.exists("warns.txt"):
        with open("warns.txt", "r") as f:
            warns = [line.strip().split(":", 3) for line in f.readlines()]
        return warns
    return []

# Helper function to save a warn to the text file for the bot
def save_warn(server_id, user_id, reason):
    with open("warns.txt", "a") as f:
        f.write(f"{server_id}:{user_id}:{reason}\n")

# Helper function to remove a specific warn for the bot
def remove_warn_for_bot(server_id, user_id, warn_index):
    warns = load_warns_for_bot()
    warns_to_keep = [w for i, w in enumerate(warns) if not (w[0] == str(server_id) and w[1] == str(user_id) and i == warn_index)]
    with open("warns.txt", "w") as f:
        for w in warns_to_keep:
            f.write(f"{w[0]}:{w[1]}:{w[2]}\n")

# Command to warn a user with a reason
@bot.command()
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    if ctx.author.guild_permissions.kick_members:
        save_warn(ctx.guild.id, member.id, reason)
        await ctx.send(f"{member.mention} has been warned. Reason: {reason}")

        warns = load_warns_for_bot()
        user_warns = [w for w in warns if w[0] == str(ctx.guild.id) and w[1] == str(member.id)]
        warn_count = len(user_warns)

        if warn_count == 2:
            mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
            if not mute_role:
                permissions = discord.Permissions(send_messages=False, speak=False)
                mute_role = await ctx.guild.create_role(name="Muted", permissions=permissions)
                for channel in ctx.guild.channels:
                    await channel.set_permissions(mute_role, send_messages=False, speak=False)

            await member.add_roles(mute_role, reason="Reached 2 warnings")
            await ctx.send(f"{member.mention} has been muted for 5 minutes due to receiving 2 warnings.")
            await asyncio.sleep(300)
            await member.remove_roles(mute_role, reason="Temporary mute expired")
            await ctx.send(f"{member.mention} has been unmuted.")
    else:
        await ctx.send("You don't have permission to use this command!")

# Command to list all warnings of a user
@bot.command()
async def warnlist(ctx, member: discord.Member):
    warns = load_warns_for_bot()
    user_warns = [w for w in warns if w[0] == str(ctx.guild.id) and w[1] == str(member.id)]
    if user_warns:
        warn_messages = [f"{idx+1}. Reason: {w[2]}" for idx, w in enumerate(user_warns)]
        warn_list = "\n".join(warn_messages)
        embed = discord.Embed(title=f"Warnings for {member}", description=warn_list, color=0xff0000)
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"{member.mention} has no warnings.")

# Command to clear a specific warning
@bot.command()
async def clearwarn(ctx, member: discord.Member, warn_number: int):
    if ctx.author.guild_permissions.kick_members:
        warns = load_warns_for_bot()
        user_warns = [w for w in warns if w[0] == str(ctx.guild.id) and w[1] == str(member.id)]
        if 0 < warn_number <= len(user_warns):
            warn_indices = [i for i, w in enumerate(warns) if w[0] == str(ctx.guild.id) and w[1] == str(member.id)]
            warn_index = warn_indices[warn_number - 1]
            remove_warn_for_bot(ctx.guild.id, member.id, warn_index)
            await ctx.send(f"Warning {warn_number} for {member.mention} has been cleared.")
        else:
            await ctx.send(f"{member.mention} does not have a warning number {warn_number}.")
    else:
        await ctx.send("You don't have permission to use this command!")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Function to start the bot and Flask app together
def run_bot_and_flask():
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Start the Discord bot
    bot.run('MTI4NjY5NTk2NTI4MTA5MTcwNg.G8tEcx.2FjT6OybJnEha63E9kfErGSC6N48DSu0BkUqvk')

if __name__ == "__main__":
    run_bot_and_flask()
