import discord
from discord.ext import commands
import os

# Activer tous les intents
intents = discord.Intents.all()

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong !")

# Tu pourras ajouter ici d'autres commandes comme /groupe_creer

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN is None:
        print("❌ DISCORD_TOKEN non défini dans les variables d'environnement.")
    else:
        bot.run(TOKEN)
