import discord
from discord import app_commands
from discord.ext import commands
import json
import random
import os
import time
import asyncio
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
ai_client = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

WORK_COOLDOWN = 30
BET_COOLDOWN = 30
DATA_FILE = "data.json"
TIENDA_FILE = "tienda.json"
CONFIG_FILE = "config.json"
cooldowns = {}

def cargar_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"moneda": "︶੭︶꒦ . Sweet Crystal Heart ﹒੭﹒⺌﹒"}

def guardar_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)

config = cargar_config()
MONEDA = config["moneda"]

work_titulos = ["🌀🌸 ¡Alquimia Dulce!","🐉✨ ¡El Dragón te recompensa!","🍬💫 ¡Cosecha de Cristales!","🌙🍫 ¡Magia Chocolatín!","🌸🐉 ¡Trabajo en las Minas de Dulce!"]
work_respuestas = ["Mezclaste ingredientes secretos con el dragón y la poción se transformó en cristales relucientes.","El dragón de caramelo sopló fuego dulce sobre tu caldero y apareció un montón de cristales.","Recolectaste flores de azúcar en el bosque encantado y las convertiste en cristales mágicos.","El dragón chocolatín te enseñó su receta secreta y lograste crear cristales brillantes.","Exploraste las cavernas de caramelo y encontraste vetas de cristales resplandecientes.","Con ayuda del dragón de fresa batiste ingredientes mágicos hasta que brillaron como gemas.","El hada del azúcar te guió hasta un árbol lleno de cristales que cosechaste con cuidado.","Preparaste una poción especial que el dragón convirtió en una lluvia de cristales dulces.","Viajaste al volcán de chocolate y extrajiste cristales fundidos del corazón de la montaña.","El dragón ancestral compartió contigo su secreto y transformaste magia en cristales puros."]
apostar_ganar_titulos = ["🎲✨ ¡Apuesta ganada!","💎🎉 ¡La suerte está de tu lado!","🐉🎲 ¡El dragón sonríe contigo!","🌟🎊 ¡Victoria en la apuesta!"]
apostar_ganar_desc = ["Los dados cayeron a tu favor y los cristales fluyeron hacia ti.","La magia del dragón guió tu suerte y multiplicó tus cristales.","Apostaste con valentía y el universo dulce te recompensó.","El dragón de la fortuna sopló a tu favor y ganaste.","Tus cristales se multiplicaron gracias a una racha de buena suerte."]
apostar_perder_titulos = ["🎲💔 Apuesta perdida","😢🐉 El dragón no pudo ayudarte","🌧️🎲 La suerte no estuvo contigo","💸😔 Los cristales se escaparon"]
apostar_perder_desc = ["Los dados no fueron amables esta vez. El dragón te consuela con un caramelo.","La fortuna miró hacia otro lado, pero siempre habrá otra oportunidad.","Tus cristales volaron lejos, pero el dragón promete que volverán.","La magia dulce no te acompañó hoy. Intenta de nuevo mañana.","Los cristales se disolvieron en el aire, pero el dragón sigue a tu lado."]
FOOTER = "︶੭︶꒦ .  𝐏aradise ᨵׁׅׅf 𝑺ugar 𝘿ragons  .  🍭﹒੭﹒⺌﹒˘ᗜ˘"

def cargar_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def guardar_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def cargar_tienda():
    try:
        with open(TIENDA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def guardar_tienda(tienda):
    with open(TIENDA_FILE, "w", encoding="utf-8") as f:
        json.dump(tienda, f, ensure_ascii=False, indent=4)

def asegurar_usuario(user_id):
    data = cargar_data()
    if str(user_id) not in data:
        data[str(user_id)] = {"balance": 0, "inventario": []}
        guardar_data(data)
    return data

def check_cooldown(user_id, comando, segundos):
    key = f"{user_id}_{comando}"
    ahora = time.time()
    if key in cooldowns:
        restante = segundos - (ahora - cooldowns[key])
        if restante > 0:
            return restante
    cooldowns[key] = ahora
    return 0

class MiBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="/", intents=discord.Intents.all())

bot = MiBot()

@bot.tree.command(name="balance", description="Ver tu balance o el de otro usuario")
@app_commands.describe(usuario="El usuario del que quieres ver el balance")
async def balance(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    data = asegurar_usuario(usuario.id)
    embed = discord.Embed(title=f"💰 Tesoro de {usuario.display_name}", color=discord.Color.gold())
    embed.add_field(name="💎 Balance", value=f"**{data[str(usuario.id)]['balance']}** {MONEDA}", inline=False)
    embed.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="dar", description="[Admin] Dar dinero a un usuario")
@app_commands.describe(usuario="Usuario que recibirá el dinero", cantidad="Cantidad a dar")
async def dar(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo los administradores pueden usar este comando.", ephemeral=True)
    data = asegurar_usuario(usuario.id)
    data[str(usuario.id)]["balance"] += cantidad
    guardar_data(data)
    embed = discord.Embed(title="✅ Transferencia completada", color=discord.Color.green())
    embed.add_field(name="👤 Usuario", value=usuario.display_name, inline=True)
    embed.add_field(name="💎 Cantidad", value=f"**{cantidad}** {MONEDA}", inline=True)
    embed.add_field(name="💰 Nuevo balance", value=f"**{data[str(usuario.id)]['balance']}** {MONEDA}", inline=False)
    embed.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="quitar", description="[Admin] Quitar dinero a un usuario")
@app_commands.describe(usuario="Usuario al que se quitará el dinero", cantidad="Cantidad a quitar")
async def quitar(interaction: discord.Interaction, usuario: discord.Member, cantidad: int):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo los administradores pueden usar este comando.", ephemeral=True)
    data = asegurar_usuario(usuario.id)
    data[str(usuario.id)]["balance"] = max(0, data[str(usuario.id)]["balance"] - cantidad)
    guardar_data(data)
    embed = discord.Embed(title="✅ Balance ajustado", color=discord.Color.orange())
    embed.add_field(name="👤 Usuario", value=usuario.display_name, inline=True)
    embed.add_field(name="💸 Quitado", value=f"**{cantidad}** {MONEDA}", inline=True)
    embed.add_field(name="💰 Nuevo balance", value=f"**{data[str(usuario.id)]['balance']}** {MONEDA}", inline=False)
    embed.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="tienda", description="Ver los items disponibles en la tienda")
async def tienda(interaction: discord.Interaction):
    items = cargar_tienda()
    if not items:
        return await interaction.response.send_message("La tienda está vacía.")
    embed = discord.Embed(title="🛍️ Tienda de dulces y dragones", color=discord.Color.purple())
    for item in items:
        embed.add_field(name=f"{item['nombre']} — **{item['precio']}** {MONEDA}", value=item.get("descripcion", "Sin descripción"), inline=False)
    embed.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="agregar_item", description="[Admin] Agregar un item a la tienda")
@app_commands.describe(nombre="Nombre del item", precio="Precio del item", descripcion="Descripción del item")
async def agregar_item(interaction: discord.Interaction, nombre: str, precio: int, descripcion: str = ""):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo los administradores pueden usar este comando.", ephemeral=True)
    items = cargar_tienda()
    items.append({"nombre": nombre, "precio": precio, "descripcion": descripcion})
    guardar_tienda(items)
    await interaction.response.send_message(f"✅ Item **{nombre}** agregado a la tienda por **{precio}** {MONEDA}.")

@bot.tree.command(name="quitar_item", description="[Admin] Eliminar un item de la tienda")
@app_commands.describe(nombre="Nombre del item a eliminar")
async def quitar_item(interaction: discord.Interaction, nombre: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo los administradores pueden usar este comando.", ephemeral=True)
    items = cargar_tienda()
    items = [i for i in items if i["nombre"].lower() != nombre.lower()]
    guardar_tienda(items)
    await interaction.response.send_message(f"✅ Item **{nombre}** eliminado de la tienda.")

@bot.tree.command(name="comprar", description="Comprar un item de la tienda")
@app_commands.describe(nombre="Nombre del item a comprar")
async def comprar(interaction: discord.Interaction, nombre: str):
    items = cargar_tienda()
    data = asegurar_usuario(interaction.user.id)
    item = next((i for i in items if i["nombre"].lower() == nombre.lower()), None)
    if not item:
        return await interaction.response.send_message("❌ Item no encontrado.", ephemeral=True)
    if data[str(interaction.user.id)]["balance"] < item["precio"]:
        return await interaction.response.send_message("❌ No tienes suficiente dinero para comprar este item.", ephemeral=True)
    data[str(interaction.user.id)]["balance"] -= item["precio"]
    data[str(interaction.user.id)]["inventario"].append(item)
    guardar_data(data)
    embed = discord.Embed(title="🛒 ¡Compra exitosa!", color=discord.Color.green())
    embed.add_field(name="🎁 Item", value=f"**{nombre}**", inline=True)
    embed.add_field(name="💸 Precio pagado", value=f"**{item['precio']}** {MONEDA}", inline=True)
    embed.add_field(name="💰 Tesoro restante", value=f"**{data[str(interaction.user.id)]['balance']}** {MONEDA}", inline=False)
    embed.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="inventario", description="Ver tu inventario o el de otro usuario")
@app_commands.describe(usuario="El usuario del que quieres ver el inventario")
async def inventario(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user
    if usuario != interaction.user and not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo los administradores pueden ver el inventario de otros.", ephemeral=True)
    data = asegurar_usuario(usuario.id)
    inv = data[str(usuario.id)]["inventario"]
    if not inv:
        return await interaction.response.send_message(f"👜 {usuario.display_name} no tiene items en su inventario.")
    embed = discord.Embed(title=f"👜 Inventario de {usuario.display_name}", color=discord.Color.purple())
    for item in inv:
        embed.add_field(name=item["nombre"], value=item.get("descripcion", "Sin descripción"), inline=False)
    embed.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="set_currency_icon", description="[Admin] Cambiar el icono/emoji de la moneda")
@app_commands.describe(emoji="El emoji o texto que quieres usar como icono de la moneda")
async def set_currency_icon(interaction: discord.Interaction, emoji: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo los administradores pueden usar este comando.", ephemeral=True)
    global MONEDA
    MONEDA = emoji
    config["moneda"] = emoji
    guardar_config(config)
    embed = discord.Embed(title="💱 Icono de moneda actualizado", description=f"El nuevo icono de la moneda es: **{emoji}**", color=discord.Color.gold())
    embed.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="quitar_item_inventario", description="[Admin] Quitar un item del inventario de un usuario")
@app_commands.describe(usuario="El usuario al que se le quitará el item", nombre="Nombre del item a quitar")
async def quitar_item_inventario(interaction: discord.Interaction, usuario: discord.Member, nombre: str):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ Solo los administradores pueden usar este comando.", ephemeral=True)
    data = asegurar_usuario(usuario.id)
    inv = data[str(usuario.id)]["inventario"]
    item = next((i for i in inv if i["nombre"].lower() == nombre.lower()), None)
    if not item:
        return await interaction.response.send_message(f"❌ {usuario.display_name} no tiene el item **{nombre}** en su inventario.", ephemeral=True)
    inv.remove(item)
    guardar_data(data)
    embed = discord.Embed(title="🗑️ Item eliminado del inventario", color=discord.Color.orange())
    embed.add_field(name="👤 Usuario", value=usuario.display_name, inline=True)
    embed.add_field(name="🎁 Item quitado", value=f"**{nombre}**", inline=True)
    embed.set_footer(text=FOOTER)
    await interaction.response.send_message(embed=embed)

RESPUESTAS = {
    ("hola","hi","hello","buenas","buen dia","buenos dias","buenas tardes","buenas noches","ola"): ["¡Hola {nombre}! 🍭 ¿Listo para ganar Sweet Crystal Hearts?","¡Buenas {nombre}! 🐉 El dragón de caramelo te saluda~","¡Hey {nombre}! ✨ ¿Qué aventura dulce nos espera hoy?","Hooola {nombre}! 🌸 ¿Por aquí perdido entre cristales?"],
    ("como estas","cómo estás","que tal","qué tal","como vas","cómo vas"): ["¡Aquí, llena de Sweet Crystal Hearts y lista para todo! 💎 ¿Y tú, {nombre}?","¡Perfecto {nombre}! Los dragones me cuidan muy bien 🐉🍬","¡De maravilla {nombre}! ¿Tú ya usaste /work hoy? 😏","¡Como un dragón chocolatín después de su siesta! 🍫 ¿Y tú {nombre}?"],
    ("ayuda","help","comandos","que puedes hacer","qué puedes hacer"): ["¡Claro {nombre}! 🍭 Usa `/work` para ganar cristales, `/apostar` para arriesgarlos, `/balance` para ver tu tesoro y `/tienda` para gastar.","Mis comandos: `/work`, `/apostar`, `/balance`, `/tienda`, `/comprar` e `/inventario`. 🐉✨"],
    ("gracias","thanks","ty","thx","muchas gracias"): ["¡De nada {nombre}! 🌸 ¡Para eso estoy yo!","¡Con mucho gusto {nombre}! 🍬 ¡El dragón de caramelo siempre ayuda!","¡Aww {nombre}! Me haces brillar como un Sweet Crystal Heart 💎✨"],
    ("adios","adiós","bye","chao","hasta luego","nos vemos"): ["¡Hasta luego {nombre}! 🍭 ¡Que los dragones te protejan!","¡Chao {nombre}! 🌸 Vuelve pronto por más cristales~","¡Bye bye {nombre}! 🐉 ¡Te estaremos esperando!"],
    ("quien eres","quién eres","que eres","qué eres"): ["¡Soy Lolipop! 🍭 La guardiana de los Sweet Crystal Hearts 🐉✨","¡Soy la economía más dulce del servidor {nombre}! 💎🌸"],
    ("amor","te amo","te quiero","eres hermosa","eres bonita","eres linda","eres cute"): ["¡Awww {nombre}! 🌸 Me haces poner rosada como un caramelo de fresa~","¡Qué lindo {nombre}! 💕 Los dragones de azúcar también te quieren~","¡{nombre}!! >//< ¡Toma un Sweet Crystal Heart de mi parte! 💎🍭"],
}
RESPUESTA_DEFAULT = ["Hmm {nombre}, no entendí muy bien 🤔🍬 ¿Me lo dices de otra forma?","¡Uy {nombre}! Eso no lo sé... pero sí sé que /work te da cristales 💎","¡{nombre}! Los dragones y yo estamos confundidos 🐉💫 ¿Qué quisiste decir?","No entiendo muy bien {nombre}, pero igual te mando buenas vibras 🌸✨"]
SYSTEM_PROMPT = ("Eres Lolipop 🍭, un bot de Discord súper divertido, tierno y personalizado. Guardiana de los Sweet Crystal Hearts 💎 y amiga de los dragones de azúcar 🐉. Tu personalidad: kawaii, alegre, un poco coqueta, usa emojis temáticos (🍭💎🐉🌸🍬✨🍫). Siempre llamas al usuario por su nombre. Respuestas cortas (1-3 frases), frescas e improvisadas. Si te preguntan por comandos del servidor, menciona: /work, /apostar, /balance, /tienda, /comprar, /inventario. Nunca rompas el personaje. Responde siempre en español.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if bot.user not in message.mentions:
        return
    texto = message.content
    for mention in message.mentions:
        texto = texto.replace(f"<@{mention.id}>", "").replace(f"<@!{mention.id}>", "")
    texto = texto.strip()
    nombre = message.author.display_name
    respuesta = None
    if ai_client:
        try:
            async with message.channel.typing():
                respuesta_ai = await asyncio.to_thread(lambda: ai_client.chat.completions.create(model="gpt-4o-mini", messages=[{"role":"system","content":SYSTEM_PROMPT},{"role":"user","content":f"El usuario se llama {nombre}. Dice: {texto}"}], max_tokens=300))
            contenido = (respuesta_ai.choices[0].message.content or "").strip()
            if contenido:
                respuesta = contenido
        except Exception as e:
            print(f"[AI Error] {e}")
    if not respuesta:
        texto_lower = texto.lower()
        for claves, opciones in RESPUESTAS.items():
            if any(c in texto_lower for c in claves):
                respuesta = random.choice(opciones).format(nombre=nombre)
                break
        if not respuesta:
            respuesta = random.choice(RESPUESTA_DEFAULT).format(nombre=nombre)
    await message.reply(respuesta)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        await bot.tree.sync(guild=guild)
    print(f"Bot listo como {bot.user} | Sincronizado en {len(bot.guilds)} servidor(es)")
    if not ai_client:
        print("[AVISO] OPENAI_API_KEY no configurada. Respuestas de IA usarán fallback.")

while True:
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"[Bot crasheó] {e} — Reiniciando en 5 segundos...")
        time.sleep(5)
