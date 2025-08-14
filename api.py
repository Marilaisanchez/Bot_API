import os
import time
import requests
import pyttsx3
import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from dotenv import load_dotenv  

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

engine = pyttsx3.init()

def speak(text: str):
    engine.say(text)
    engine.runAndWait()

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

@bot.command(name="dato", aliases=["fact", "random", "consejo"])
async def fact_command(ctx: commands.Context):
    try:
        original = fetch_random_fact()
        traducido = translate_to_spanish(original)
        await ctx.send(f"Dato curioso: {traducido}\n*(Original: {original})*")
        speak(traducido)
    except Exception as e:
        await ctx.send(f"Error: `{e}`")

if __name__ == "__main__":
    if TOKEN is None:
        raise ValueError("No se encontró el token")
    bot.run(TOKEN)
