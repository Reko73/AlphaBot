import discord
from discord.ext import commands
from discord import app_commands
import os
from keep_alive import keep_alive
from discord.ext import commands, tasks
from discord import app_commands, Embed, Colour
from dotenv import load_dotenv
import datetime

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

async def set_bot_status():
    await bot.change_presence(
        status=discord.Status.dnd,
        activity=discord.Activity(type=discord.ActivityType.watching, name="Zero Alpha")
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

@tree.command(name="unban", description="Débannir un utilisateur via son ID Discord")
@app_commands.describe(user_id="ID Discord de l'utilisateur à débannir")
async def unban(interaction: discord.Interaction, user_id: str):
    # Permission : il faut que l'utilisateur ait le droit de bannir
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ Tu n'as pas la permission de débannir.", ephemeral=True)
        return

    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ {user} a été débanni avec succès.")
    except discord.NotFound:
        await interaction.response.send_message("❌ Utilisateur non trouvé dans la liste des bannis.", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Je n'ai pas la permission de débannir.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Une erreur est survenue : {e}", ephemeral=True)




keep_alive()
bot.run(TOKEN)
