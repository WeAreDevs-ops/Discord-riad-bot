import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

# Retrieve the token from environment variables (Secrets)
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Sync slash commands **globally**
        await self.tree.sync(guild=None)  # <-- THIS MAKES THEM GLOBAL
        print(f"Synced global slash commands for {self.user}")

bot = MyBot()

# Simple storage for user messages (in-memory)
user_messages = {}

class SpamView(discord.ui.View):
    def __init__(self, message_content, user_id):
        super().__init__(timeout=None)
        self.message_content = message_content
        self.user_id = user_id

    @discord.ui.button(label="Activate", style=discord.ButtonStyle.green)
    async def activate(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Ephemeral messages are already private, but we acknowledge the action
        await interaction.response.send_message("Starting to send messages...", ephemeral=True)
        
        for _ in range(10):
            await interaction.channel.send(self.message_content)
            await asyncio.sleep(0.5)  # Slight delay to avoid aggressive rate limiting

@bot.tree.command(name="setmessage", description="Setup the message to be spammed")
@app_commands.describe(message="The message you want to spam")
async def setmessage(interaction: discord.Interaction, message: str):
    user_messages[interaction.user.id] = message
    
    embed = discord.Embed(
        title="Message Setup Complete",
        description=f"Your message is set to: **{message}**\n\nClick the button below to send it 10 times in this channel.",
        color=discord.Color.blue()
    )
    
    view = SpamView(message, interaction.user.id)
    
    # Send as ephemeral so only the user sees it
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables.")
    else:
        bot.run(TOKEN)
