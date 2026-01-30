import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

user_messages = {}

class SpamView(discord.ui.View):
    def __init__(self, message):
        super().__init__(timeout=900)
        self.message = message

    @discord.ui.button(label="Activate", style=discord.ButtonStyle.green)
    async def activate(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message(
            "Spamming started...",
            ephemeral=True
        )

        # Spam using INTERACTION RESPONSES, not channel messages
        for _ in range(10):
            try:
                await interaction.followup.send(self.message)
                await asyncio.sleep(0.2)
            except Exception as e:
                print("Spam error:", e)
                break


@bot.tree.command(name="setmessage", description="Setup the message to spam")
@app_commands.describe(message="The message you want to spam")
async def setmessage(interaction: discord.Interaction, message: str):

    user_messages[interaction.user.id] = message

    embed = discord.Embed(
        title="Message Set",
        description=f"Your message:\n**{message}**\n\nClick activate to spam.",
        color=discord.Color.blue()
    )

    view = SpamView(message)

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
