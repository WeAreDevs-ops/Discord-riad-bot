import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")

# ✅ FIXED INTENT WARNING
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_messages = {}  # Store user messages
auto_spam_tasks = {}  # Store running auto spam tasks


class SpamView(discord.ui.View):
    def __init__(self, message, interval_seconds=0.2):
        """
        message: str -> message to spam
        interval_seconds: float -> delay between messages
        """
        super().__init__(timeout=None)
        self.message = message
        self.interval = interval_seconds

    @discord.ui.button(label="Activate", style=discord.ButtonStyle.green)
    async def activate(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "✅ Spamming started...",
            ephemeral=True
        )

        # Send exactly 6 messages reliably
        for i in range(6):
            try:
                await interaction.followup.send(self.message)
                await asyncio.sleep(self.interval)
            except discord.HTTPException as e:
                print(f"Message {i+1} failed:", e)
                continue


# =========================
# EXISTING COMMAND (UNCHANGED)
# =========================
@bot.tree.command(name="setmessage", description="Setup the message to spam")
@app_commands.describe(message="The message you want to spam")
async def setmessage(interaction: discord.Interaction, message: str):
    user_messages[interaction.user.id] = message

    embed = discord.Embed(
        title="Message Set",
        description=f"Your message:\n**{message}**\n\nClick Activate to spam.",
        color=discord.Color.blue()
    )

    view = SpamView(message, interval_seconds=0.2)

    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )


# =========================
# NEW AUTO SPAM SYSTEM
# =========================
async def auto_spam_loop(channel, message, user_id):
    while user_id in auto_spam_tasks:
        try:
            await channel.send(message)
            await asyncio.sleep(0.5)  # safer delay
        except Exception as e:
            print("Auto spam error:", e)
            break


# START AUTO SPAM
@bot.tree.command(name="autospam", description="Automatically keep sending your saved message")
async def autospam(interaction: discord.Interaction):

    message = user_messages.get(interaction.user.id)

    if not message:
        await interaction.response.send_message(
            "⚠️ Set a message first using /setmessage",
            ephemeral=True
        )
        return

    if interaction.user.id in auto_spam_tasks:
        await interaction.response.send_message(
            "⚠️ Auto spam already running.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "✅ Auto spam started.",
        ephemeral=True
    )

    task = asyncio.create_task(
        auto_spam_loop(interaction.channel, message, interaction.user.id)
    )

    auto_spam_tasks[interaction.user.id] = task


# STOP AUTO SPAM
@bot.tree.command(name="stopspam", description="Stop automatic spam")
async def stopspam(interaction: discord.Interaction):

    task = auto_spam_tasks.pop(interaction.user.id, None)

    if task:
        task.cancel()
        await interaction.response.send_message(
            "🛑 Auto spam stopped.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "No auto spam running.",
            ephemeral=True
        )


# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(status=discord.Status.online)
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)
