import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
from discord.ext import commands, tasks
from discord import app_commands, Embed, Colour
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

BOOST_ANNOUNCE_CHANNELS = {
    1387099994351468654: 1387112604677443615,
}

ADMIN_ROLES = {
    1387099994351468654: [1387099994351468655, 1387103255183753236, 1387099994351468661, 1387099994351468663],
}

LOG_CHANNELS = {
    1387099994351468654: 1395180508509507785,
}

DISCORD_LINK_CHANNELS = {
    1387099994351468654: [1318165877350338612, 1313203999004164230],
}


intents = discord.Intents.all()

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await set_bot_status()
    print(f"Connecté en tant que {bot.user} (ID: {bot.user.id})")
    
    try:
        synced = await bot.tree.sync()
        print(f"Commandes slash synchronisées : {len(synced)}")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")

    vote_14h.start()
    vote_20h20.start()

async def set_bot_status():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(type=discord.ActivityType.watching, name="ZERO ALPHA | 🧟")
    )

def user_is_admin(interaction):
    guild_id = interaction.guild.id
    allowed_role_ids = ADMIN_ROLES.get(guild_id, [])
    return any(role.id in allowed_role_ids for role in interaction.user.roles)

def get_log_channel(interaction: discord.Interaction):
    log_channel_id = LOG_CHANNELS.get(interaction.guild_id)
    return interaction.guild.get_channel(log_channel_id) if log_channel_id else None


@bot.event
async def on_member_update(before, after):
    if before.premium_since is None and after.premium_since is not None:
        guild_id = after.guild.id
        channel_id = BOOST_ANNOUNCE_CHANNELS.get(guild_id)

        if channel_id:
            channel = after.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="🚀 Merci pour le boost !",
                    description=f"{after.mention} vient de booster **{after.guild.name}** ! 💜",
                    color=discord.Color.purple()
                )
                embed.set_thumbnail(url=after.display_avatar.url)
                await channel.send(embed=embed)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if '@everyone' in message.content or '@here' in message.content:
        guild_id = message.guild.id
        allowed_role_ids = ADMIN_ROLES.get(guild_id, [])

        if not any(role.id in allowed_role_ids for role in message.author.roles):
            try:
                await message.delete()
            except discord.NotFound:
                pass
            await message.channel.send(
                "Ton message contenant 'everyone' ou 'here' a été supprimé car tu n'as pas les permissions.",
                delete_after=30
            )

            log_channel_id = LOG_CHANNELS.get(guild_id)
            log_channel = message.guild.get_channel(log_channel_id) if log_channel_id else None
            if log_channel:
                embed = Embed(
                    title="🔒 Message supprimé",
                    description=f"**Auteur :** {message.author.mention}\n"
                                f"**Contenu :**\n```{message.content}```",
                    color=0xFF0000
                )
                embed.set_footer(text=f"Salon : #{message.channel.name} • ID : {message.channel.id}")
                embed.timestamp = message.created_at
                await log_channel.send(embed=embed)

    guild_id = message.guild.id
    allowed_role_ids = ADMIN_ROLES.get(guild_id, [])
    log_channel_id = LOG_CHANNELS.get(guild_id)
    log_channel = message.guild.get_channel(log_channel_id) if log_channel_id else None
    

    await bot.process_commands(message)




# ===============================
# ========= COMMANDES ===========
# ===============================


@bot.tree.command(name="purge", description="Supprime un nombre spécifié de messages.")
async def purge(interaction: discord.Interaction, number: int):
    if not user_is_admin(interaction):
        await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.", ephemeral=True)
        return

    if number <= 0:
        await interaction.response.send_message("Veuillez spécifier un nombre positif de messages à supprimer.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=number)
    await interaction.followup.send(f"{len(deleted)} messages ont été supprimés.", ephemeral=True)

    log_channel = get_log_channel(interaction)
    if log_channel:
        embed = Embed(title="🧹 Purge de messages",
                      description=f"{interaction.user.mention} a supprimé {len(deleted)} messages dans {interaction.channel.mention}.",
                      color=discord.Color.orange())
        await log_channel.send(embed=embed)

@bot.tree.command(name="avertir", description="Donne un avertissement à un membre.")
@app_commands.describe(membre="Le membre à avertir", raison="La raison de l'avertissement")
async def warn(interaction: discord.Interaction, membre: discord.Member, raison: str):
    if not user_is_admin(interaction):
        await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.", ephemeral=True)
        return

    await interaction.response.send_message(f"{membre.mention} a été averti pour : {raison}", ephemeral=True)

    log_channel = get_log_channel(interaction)
    if log_channel:
        embed = Embed(title="⚠️ Avertissement",
                      description=f"{membre.mention} a été averti par {interaction.user.mention}.",
                      color=discord.Color.yellow())
        embed.add_field(name="Raison", value=raison, inline=False)
        await log_channel.send(embed=embed)

@bot.tree.command(name="virer", description="Expulse un membre du serveur.")
async def kick(interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison fournie"):
    if not user_is_admin(interaction):
        await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.", ephemeral=True)
        return

    await membre.kick(reason=raison)
    await interaction.response.send_message(f"{membre.mention} a été expulsé.", ephemeral=True)

    log_channel = get_log_channel(interaction)
    if log_channel:
        embed = Embed(title="👢 Expulsion",
                      description=f"{membre.mention} a été expulsé par {interaction.user.mention}.",
                      color=discord.Color.red())
        embed.add_field(name="Raison", value=raison, inline=False)
        await log_channel.send(embed=embed)

@bot.tree.command(name="ban", description="Bannit un membre du serveur.")
async def ban(interaction: discord.Interaction, membre: discord.Member, raison: str = "Aucune raison fournie"):
    if not user_is_admin(interaction):
        await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.", ephemeral=True)
        return

    await membre.ban(reason=raison)
    await interaction.response.send_message(f"{membre.mention} a été banni.", ephemeral=True)

    log_channel = get_log_channel(interaction)
    if log_channel:
        embed = Embed(title="🔨 Bannissement",
                      description=f"{membre.mention} a été banni par {interaction.user.mention}.",
                      color=discord.Color.dark_red())
        embed.add_field(name="Raison", value=raison, inline=False)
        await log_channel.send(embed=embed)

@bot.tree.command(name="unban", description="Débannit un utilisateur via son ID Discord.")
@app_commands.describe(user_id="ID Discord de l'utilisateur à débannir", raison="Raison du débannissement")
async def unban(interaction: discord.Interaction, user_id: str, raison: str = "Aucune raison fournie"):
    if not user_is_admin(interaction):
        await interaction.response.send_message("Vous n'avez pas les permissions nécessaires pour utiliser cette commande.", ephemeral=True)
        return

    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=raison)
        await interaction.response.send_message(f"{user.mention} a été débanni.", ephemeral=True)

        log_channel = get_log_channel(interaction)
        if log_channel:
            embed = discord.Embed(
                title="🔓 Débannissement",
                description=f"{user.mention} a été débanni par {interaction.user.mention}.",
                color=discord.Color.green()
            )
            embed.add_field(name="Raison", value=raison, inline=False)
            await log_channel.send(embed=embed)

    except discord.NotFound:
        await interaction.response.send_message("❌ Cet utilisateur n'est pas dans la liste des bannis.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Je n'ai pas la permission de débannir cet utilisateur.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral=True)


@bot.tree.command(name="annonce", description="Envoie une annonce dans le salon actuel (réservé aux admins).")
@app_commands.describe(titre="Titre de l'annonce", message="Contenu de l'annonce")
async def annonce(interaction: discord.Interaction, titre: str, message: str):
    if not user_is_admin(interaction):
        await interaction.response.send_message("❌ Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    avatar_url = "https://cdn.discordapp.com/attachments/1166900878318510141/1395198250620813432/ChatGPT_Image_17_juil._2025_00_14_43.png?ex=68799320&is=687841a0&hm=74fab5365a5debff7eb0c7663e364a74f5c69e116ffa46a8a1701bcec301c8bc&"

    embed = discord.Embed(
        title=f"📢 {titre}",
        description=message,
        color=discord.Color.blurple()
    )
    embed.set_footer(text=f"Annonce par {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    embed.timestamp = discord.utils.utcnow()

    embed.set_thumbnail(url=avatar_url) 

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message("✅ Annonce envoyée avec succès.", ephemeral=True)

    # Logs
    log_channel = get_log_channel(interaction)
    if log_channel:
        log_embed = discord.Embed(
            title="📝 Annonce publiée",
            description=f"{interaction.user.mention} a publié une annonce dans {interaction.channel.mention}.",
            color=discord.Color.blue()
        )
        log_embed.add_field(name="Titre", value=titre, inline=False)
        log_embed.add_field(name="Message", value=message, inline=False)
        log_embed.set_footer(text=f"ID: {interaction.user.id}")
        log_embed.timestamp = discord.utils.utcnow()

        await log_channel.send(embed=log_embed)


@tasks.loop(hours=24)
async def vote_14h():
    await bot.wait_until_ready()
    now = datetime.now()
    target = now.replace(hour=14, minute=0, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())

    channel = bot.get_channel(1393782511380725883)
    if channel:
        await channel.send(
            "🎉 C’est le moment de faire la différence ! 🎉\n"
            "Fallzone a besoin de VOTRE soutien !\n"
            "Allez voter pour Fallzone et montrez que notre communauté est la meilleure 💪\n"
            "Chaque vote compte, alors prenez 2 minutes et faites entendre votre voix !\n"
            "👇 Cliquez ici pour voter : https://top-serveurs.net/gta/fallzone\n"
            "Merci à tous ! 🚀\n"
            "<@&1378463720090501150>"
        )

@tasks.loop(hours=24)
async def vote_20h20():
    await bot.wait_until_ready()
    now = datetime.now()
    target = now.replace(hour=20, minute=0, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    await asyncio.sleep((target - now).total_seconds())

    channel = bot.get_channel(1393782511380725883)
    if channel:
        await channel.send(
            "🎉 C’est le moment de faire la différence ! 🎉\n"
            "Fallzone a besoin de VOTRE soutien !\n"
            "Allez voter pour Fallzone et montrez que notre communauté est la meilleure 💪\n"
            "Chaque vote compte, alors prenez 2 minutes et faites entendre votre voix !\n"
            "👇 Cliquez ici pour voter : https://top-serveurs.net/gta/fallzone\n"
            "Merci à tous ! 🚀\n"
            "<@&1378463720090501150>"
        )



keep_alive()
bot.run(TOKEN)
