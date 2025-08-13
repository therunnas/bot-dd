import os
import sys
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# ========= Saída UTF-8 para rodar como serviço (NSSM) =========
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

load_dotenv()  # carrega variáveis do .env

# ========= Config =========
DISCORD_TOKEN = (os.getenv("DISCORD_TOKEN") or "").strip()
GUILD_ID = os.getenv("GUILD_ID")  # opcional: sync rápida por servidor

# IDs fixos dos canais
WELCOME_CHANNEL_ID = 834195950284177468
GOODBYE_CHANNEL_ID = 834196171495964682

# Caminho da fonte
FONT_PATH_ANTON = "fonts/Anton-Regular.ttf"

# ========= Intents / Bot =========
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========= Util =========
def log(msg: str):
    # imprime sem quebrar caso haja caractere fora da codepage
    try:
        print(f"[BOT] {msg}")
    except UnicodeEncodeError:
        print("[BOT] " + msg.encode("ascii", "replace").decode("ascii"))

# ========= Fontes =========
try:
    ImageFont.truetype(FONT_PATH_ANTON, 20)
    log("[OK] Fonte Anton carregada com sucesso.")
except Exception as e:
    log(f"[ERRO] Erro ao carregar Anton: {e}")

# ========= Emojis (Twemoji) =========
def baixar_emoji(emoji_char: str):
    try:
        codepoint = "-".join(f"{ord(c):x}" for c in emoji_char)
        url = f"https://twemoji.maxcdn.com/v/latest/72x72/{codepoint}.png"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return Image.open(BytesIO(r.content)).convert("RGBA")
    except Exception as e:
        log(f"Erro ao baixar emoji: {e}")
    return None

# ========= Geração da imagem =========
def create_image(event_type: str, member: discord.Member) -> str:
    username = (member.name or "USER").upper()
    avatar_url = member.display_avatar.url if member.display_avatar else member.default_avatar.url

    # Fundo
    bg = Image.new("RGBA", (800, 500), (0, 0, 0, 0))

    # Avatar circular
    avatar_bytes = requests.get(avatar_url, timeout=15).content
    avatar = Image.open(BytesIO(avatar_bytes)).resize((200, 200)).convert("RGBA")
    mask = Image.new("L", (200, 200), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 200, 200), fill=255)
    avatar = ImageOps.fit(avatar, (200, 200), centering=(0.5, 0.5))
    avatar.putalpha(mask)
    bg.paste(avatar, ((bg.width - 200) // 2, 40), avatar)

    # Fontes
    font_title = ImageFont.truetype(FONT_PATH_ANTON, 70)
    font_user  = ImageFont.truetype(FONT_PATH_ANTON, 42)
    font_sub   = ImageFont.truetype(FONT_PATH_ANTON, 26)

    # Texto
    draw = ImageDraw.Draw(bg)
    title = "WELCOME" if event_type == "welcome" else "GOODBYE"
    subtext = (
        f"BEM VINDO {username} AO INFERNO, LUGAR ONDE VOCÊ MENOS QUERIA ESTAR!"
        if event_type == "welcome"
        else f"{username} SAIU, VAI TOMAR TRAVA"
    )
    draw.text((bg.width // 2, 270), title,    font=font_title, anchor="mm", fill="white")
    draw.text((bg.width // 2, 340), username, font=font_user,  anchor="mm", fill="red")
    draw.text((bg.width // 2, 400), subtext,  font=font_sub,   anchor="mm", fill="white")

    # Emoji decorativo (na imagem pode!)
    emoji_img = baixar_emoji("⚔️")
    if emoji_img:
        emoji_img = emoji_img.resize((40, 40))
        bg.paste(emoji_img, (bg.width // 2 + 140, 335), emoji_img)
        bg.paste(emoji_img, (bg.width // 2 + 250, 390), emoji_img)

    # Salvar
    os.makedirs("output", exist_ok=True)
    output_path = f"output/{event_type}_{member.id}.png"
    bg.save(output_path, optimize=True)
    return output_path

# ========= Eventos =========
@bot.event
async def on_ready():
    log(f"[OK] Logado como {bot.user}")

    # ---- Sync de slash commands ----
    try:
        if GUILD_ID:
            guild = discord.Object(id=int(GUILD_ID))
            synced = await bot.tree.sync(guild=guild)
            log(f"[SYNC] Slash (guild {GUILD_ID}) sincronizados: {len(synced)}")
        else:
            synced = await bot.tree.sync()
            log(f"[SYNC] Slash (global) sincronizados: {len(synced)}")
    except Exception as e:
        # se aparecer WARNING de Interaction Endpoint URL, limpe o campo no Developer Portal
        log(f"[ERRO] Ao sincronizar slash: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        image_path = create_image("welcome", member)
        await channel.send(file=discord.File(image_path))
        os.remove(image_path)

@bot.event
async def on_member_remove(member: discord.Member):
    channel = bot.get_channel(GOODBYE_CHANNEL_ID)
    if channel:
        image_path = create_image("goodbye", member)
        await channel.send(file=discord.File(image_path))
        os.remove(image_path)

# ========= Comandos prefixados =========
@bot.command()
async def testar(ctx):
    image_path = create_image("welcome", ctx.author)
    await ctx.send(file=discord.File(image_path))
    os.remove(image_path)

# ========= Slash commands =========
@bot.tree.command(name="ping", description="Mostra a latência do bot")
async def ping(interaction: discord.Interaction):
    # enviar emoji no Discord é ok; problema era no console
    await interaction.response.send_message(f"🏓 {round(bot.latency*1000)} ms", ephemeral=True)

@bot.tree.command(name="testar", description="Gera imagem de boas-vindas (teste)")
async def slash_testar(interaction: discord.Interaction):
    await interaction.response.defer(thinking=True)
    try:
        image_path = create_image("welcome", interaction.user)
        await interaction.followup.send(file=discord.File(image_path))
    except Exception as e:
        await interaction.followup.send(f"Erro: {e}")
    finally:
        try:
            os.remove(image_path)
        except Exception:
            pass

# ========= Rodar =========
if not DISCORD_TOKEN:
    log("[ERRO] DISCORD_TOKEN não definido. Configure e rode novamente.")
else:
    bot.run(DISCORD_TOKEN)
