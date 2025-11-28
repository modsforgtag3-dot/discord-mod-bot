import discord
from discord import app_commands
from discord.ext import commands
import requests
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
APP_URL = os.getenv("http://127.0.0.1:5000")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

def check_connection():
    try:
        return requests.get(f"{APP_URL}/status", timeout=2).status_code == 200
    except:
        return False

def validate_package(package_name):
    try:
        response = requests.get(f"{APP_URL}/library")
        if response.status_code != 200:
            return False
        return package_name.lower() in [p.lower() for p in response.json()]
    except:
        return False

@bot.event
async def on_ready():
    await tree.sync()
    print(f"{bot.user} is online and slash commands synced!")

# ---- Slash Commands ----

@tree.command(name="vrlibrary", description="Show VR game package names")
async def vrlibrary(interaction: discord.Interaction):
    if not check_connection():
        await interaction.response.send_message("Companion app not connected.", ephemeral=True)
        return
    try:
        response = requests.get(f"{APP_URL}/library")
        packages = response.json()
        if packages:
            await interaction.response.send_message("**VR Library Packages:**\n" + "\n".join(packages))
        else:
            await interaction.response.send_message("No games found in the VR library.")
    except Exception as e:
        await interaction.response.send_message(f"Error fetching library: {e}", ephemeral=True)

@tree.command(name="launch", description="Launch a VR game by package name")
@app_commands.describe(package_name="Package name of the game to launch")
async def launch(interaction: discord.Interaction, package_name: str):
    if not check_connection():
        await interaction.response.send_message("Companion app not connected.", ephemeral=True)
        return

    if not validate_package(package_name):
        await interaction.response.send_message("Invalid game package.", ephemeral=True)
        return

    try:
        response = requests.post(f"{APP_URL}/launch", json={"package": package_name})
        if response.status_code == 200:
            await interaction.response.send_message(f"Launching **{package_name}**...")
        else:
            await interaction.response.send_message(f"Failed to launch **{package_name}**.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@tree.command(name="endgame", description="End a VR game by package name")
@app_commands.describe(package_name="Package name of the game to end")
async def endgame(interaction: discord.Interaction, package_name: str):
    if not check_connection():
        await interaction.response.send_message("Companion app not connected.", ephemeral=True)
        return

    if not validate_package(package_name):
        await interaction.response.send_message("Invalid game package.", ephemeral=True)
        return

    try:
        response = requests.post(f"{APP_URL}/end", json={"package": package_name})
        if response.status_code == 200:
            await interaction.response.send_message(f"Ended **{package_name}**.")
        else:
            await interaction.response.send_message(f"Failed to end **{package_name}**.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@tree.command(name="member", description="Manage server members")
@app_commands.describe(
    action="Action to perform (kick, ban, unban, info)",
    member="Target member (required for kick/ban/info)",
    reason="Reason for kick or ban (optional)"
)
async def member(interaction: discord.Interaction, action: str, member: discord.Member = None, reason: str = None):
    if not interaction.user.guild_permissions.kick_members and action.lower() in ["kick", "ban"]:
        await interaction.response.send_message("You don't have permission to manage members.", ephemeral=True)
        return

    action = action.lower()

    try:
        if action == "kick":
            if member is None:
                await interaction.response.send_message("You must specify a member to kick.", ephemeral=True)
                return
            await member.kick(reason=reason)
            await interaction.response.send_message(f"Member {member} has been kicked.")
        
        elif action == "ban":
            if member is None:
                await interaction.response.send_message("You must specify a member to ban.", ephemeral=True)
                return
            await member.ban(reason=reason)
            await interaction.response.send_message(f"Member {member} has been banned.")

        elif action == "unban":
            if member is None:
                await interaction.response.send_message("You must specify a member to unban.", ephemeral=True)
                return
            banned_users = await interaction.guild.bans()
            user_to_unban = discord.utils.get(banned_users, user__name=member.name)
            if user_to_unban is None:
                await interaction.response.send_message(f"Member {member} is not banned.", ephemeral=True)
                return
            await interaction.guild.unban(user_to_unban.user)
            await interaction.response.send_message(f"Member {member} has been unbanned.")

        elif action == "info":
            if member is None:
                await interaction.response.send_message("You must specify a member to view info.", ephemeral=True)
                return
            embed = discord.Embed(title=f"Info for {member}", color=discord.Color.blue())
            embed.add_field(name="ID", value=member.id, inline=False)
            embed.add_field(name="Joined Server", value=member.joined_at, inline=False)
            embed.add_field(name="Roles", value=", ".join([role.name for role in member.roles if role.name != "@everyone"]), inline=False)
            await interaction.response.send_message(embed=embed)

        else:
            await interaction.response.send_message("Invalid action. Use kick, ban, unban, or info.", ephemeral=True)
    
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

bot.run(TOKEN)
