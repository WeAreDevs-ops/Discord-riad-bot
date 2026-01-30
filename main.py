import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

user_messages = {}  # Store user messages

class SpamView(discord.ui.View):
    def __init__(self, message, interval_seconds=0.2):
        """
        message: str -> message to spam
        interval_seconds: float -> delay between messages (default 0.2s)
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


@bot.tree.command(name="setmessage", description="Setup the message to spam")
@app_commands.describe(message="The message you want to spam")
async def setmessage(interaction: discord.Interaction, message: str):
    user_messages[interaction.user.id] = message

    embed = discord.Embed(
        title="Message Set",
        description=f"Your message:\n**{message}**\n\nClick Activate to spam.",
        color=discord.Color.blue()
    )

    # Create the view without automation
    view = SpamView(message, interval_seconds=0.2)

    await interaction.response.send_message(
        embed=embed,
        view=view,
        ephemeral=True
    )


@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(status=discord.Status.online)
    print(f"Logged in as {bot.user}")


bot.run(TOKEN)
