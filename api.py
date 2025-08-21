import os
import time
import requests
import pyttsx3
import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from dotenv import load_dotenv  

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # Token del bot de Discord

# Inicializar el motor de texto a voz (TTS)
engine = pyttsx3.init()

# Función para convertir texto a voz
def speak(text: str):
    engine.say(text)       # Encola el texto a reproducir
    engine.runAndWait()    # Reproduce el audio

# Función para obtener un dato curioso desde una API externa
def fetch_random_fact() -> str:
    url = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
    # Se hace la petición HTTP GET con timeout de 12 segundos
    r = requests.get(url, timeout=12, headers={"Cache-Control": "no-cache"})
    r.raise_for_status()   # Lanza error si la respuesta no fue exitosa
    return r.json()["text"]  # Devuelve solo el texto del dato

# Función para traducir un texto (inglés → español)
def translate_to_spanish(text_en: str) -> str:
    return GoogleTranslator(source="auto", target="es").translate(text_en)

# Configuración de permisos (intents) para el bot
intents = discord.Intents.default()
intents.message_content = True  # Permitir leer el contenido de los mensajes

# Crear la instancia del bot con prefijo "*"
bot = commands.Bot(command_prefix="*", intents=intents)

# Evento que se ejecuta cuando el bot está listo y conectado
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# Comando del bot: *dato / *fact / *random / *consejo
@bot.command(name="dato", aliases=["fact", "random", "consejo"])
async def fact_command(ctx: commands.Context):
    try:
        # Obtener un dato curioso y traducirlo
        original = fetch_random_fact()
        traducido = translate_to_spanish(original)

        # Enviar el mensaje traducido + el texto original
        await ctx.send(f"Dato curioso: {traducido}\n*(Original: {original})*")

        # Decir el dato traducido en voz alta
        speak(traducido)
    except Exception as e:
        # Manejo de errores: enviar el error al chat
        await ctx.send(f"Error: `{e}`")

# Punto de entrada principal del programa
if __name__ == "__main__":
    if TOKEN is None:  # Validar que el token exista
        raise ValueError("No se encontró el token")
    bot.run(TOKEN)     # Iniciar el bot con el token
