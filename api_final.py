import os
import requests
import discord
from discord.ext import commands
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from gtts import gTTS  # Librería para convertir texto a voz y guardarlo en un archivo .mp3

# Cargar las variables de entorno desde el archivo .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")  # Token del bot de Discord

# Función para obtener un dato curioso desde la API "uselessfacts"
def fetch_random_fact() -> str:
    url = "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en"
    r = requests.get(url, timeout=12, headers={"Cache-Control": "no-cache"})
    r.raise_for_status()   # Lanza un error si la respuesta no es exitosa
    return r.json()["text"]  # Devuelve el texto del dato curioso

# Función para traducir un texto automáticamente al español
def translate_to_spanish(text_en: str) -> str:
    return GoogleTranslator(source="auto", target="es").translate(text_en)

# Configuración de permisos (intents) para el bot
intents = discord.Intents.default()
intents.message_content = True  # Permite acceder al contenido de los mensajes

# Crear la instancia del bot con prefijo "*"
bot = commands.Bot(command_prefix="*", intents=intents)

# Evento que se ejecuta cuando el bot se conecta correctamente
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# Comando: *dato / *fact / *random
@bot.command(name="dato", aliases=["fact", "random"])
async def fact_command(ctx: commands.Context):
    try:
        # Obtener y traducir un dato curioso
        original = fetch_random_fact()
        traducido = translate_to_spanish(original)

        # Enviar el dato traducido junto con el original
        await ctx.send(f"**Dato curioso:** {traducido}\n*(Original: {original})*")

        # Validar si el usuario está en un canal de voz
        if ctx.author.voice is None:
            await ctx.send("Debes estar en un canal de voz para escuchar el audio.")
            return

        # Conectarse al canal de voz del usuario
        voice_channel = ctx.author.voice.channel
        vc = await voice_channel.connect()

        # Convertir el texto traducido a voz y guardarlo como archivo MP3
        tts = gTTS(text=traducido, lang="es")
        audio_path = "dato.mp3"
        tts.save(audio_path)

        # Reproducir el archivo de audio en el canal de voz con FFmpeg
        vc.play(discord.FFmpegPCMAudio(audio_path))

        # Esperar hasta que termine de reproducirse el audio
        while vc.is_playing():
            await discord.utils.sleep_until(discord.utils.utcnow())

        # Desconectarse del canal de voz después de reproducir
        await vc.disconnect()

    except Exception as e:
        # Enviar un mensaje en caso de error
        await ctx.send(f"❌ Error: `{e}`")

# Punto de entrada del programa
if __name__ == "__main__":
    if TOKEN is None:  # Verificar que el token exista en .env
        raise ValueError("⚠ No se encontró el token en .env")
    bot.run(TOKEN)     # Iniciar el bot de Discord
