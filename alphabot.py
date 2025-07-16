import discord
from discord.ext import commands
import os

# Activer tous les intents
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong !")

# Tu pourras ajouter ici d'autres commandes comme /groupe_creer

bot.run(TOKEN)
