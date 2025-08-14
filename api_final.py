import os
import requests
import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

def fetch_random_fact() -> str:
    url = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
    r = requests.get(url, timeout=12, headers={"Cache-Control": "no-cache"})
    r.raise_for_status()
    return r.json()["text"]

def translate_to_spanish(text_en: str) -> str:
    return GoogleTranslator(source="auto", target="es").translate(text_en)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="*", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

@bot.command(name="dato", aliases=["fact", "random"])
async def fact_command(ctx: commands.Context):
    try:
        original = fetch_random_fact()
        traducido = translate_to_spanish(original)

        await ctx.send(f"**Dato curioso:** {traducido}\n*(Original: {original})*")

        if ctx.author.voice is None:
            await ctx.send("Debes estar en un canal de voz para escuchar el audio.")
            return

        voice_channel = ctx.author.voice.channel
        vc = await voice_channel.connect()

        tts = gTTS(text=traducido, lang="es")
        audio_path = "dato.mp3"
        tts.save(audio_path)

        vc.play(discord.FFmpegPCMAudio(audio_path))

        while vc.is_playing():
            await discord.utils.sleep_until(discord.utils.utcnow())

        await vc.disconnect()

    except Exception as e:
        await ctx.send(f"❌ Error: `{e}`")

if __name__ == "__main__":
    if TOKEN is None:
        raise ValueError("⚠ No se encontró el token en .env")
    bot.run(TOKEN)