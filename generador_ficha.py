#-------------------------------------------------
# Generador echo x Chat GPT si tuviera pagina web (echo despues de mostrarle el que tenia)
#--------------------------------------------------
import random
import string
from telegram.ext import Application, MessageHandler, filters
import re
import requests
from bs4 import BeautifulSoup

MI_NUMERO = "+54 9 2235385001"
TELEGRAM_BOT_TOKEN = '8586713628:AAFm9sVd_aysUs3cmux9dOkiWQZK6U152Vc'

# ✨ Aun NO existe, pero el bot lo va a usar igual
DOMINIO_FICHAS = "https://tuweb.com/ficha/"   # <- Cambialo cuando tengas la web

PATRON_TELEFONO = r'(?:\+\d{1,3}\s?\d{2,4}\s?[\s\d]{4}[-\s]?\d{4,6})|(?:\d{3,5}[-\s]?\d{4}[-\s]?\d{4})'
PATRON_LIMPIEZA_CONTACTO = r'(?:Inicio Ventas Campo \(1\).*Buscar por:)|(?:Contáctanos Cabrera Propiedades.*wasi\.co)|(?:Ofertar\s*×\s*Ofertar\s*×)'


def generar_id_unico(longitud=5):
    """Genera IDs tipo ABC3F o 91TZQ."""
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))


def generar_ficha_desde_enlace(enlace_ficha):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "es-ES,es;q=0.9"
    }

    response = requests.get(enlace_ficha, headers=headers, timeout=10)
    response.raise_for_status()
    sopa = BeautifulSoup(response.text, "html.parser")

    titulo_elem = sopa.find("h2", class_="title-sup-property")
    titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Título no encontrado"

    descripcion_elem = sopa.find("article", id="article-container")

    if descripcion_elem:
        texto = descripcion_elem.get_text(separator=' ', strip=True)
    else:
        main = sopa.find("div", class_="page-content") or sopa.find("body")
        texto = main.get_text(separator=' ', strip=True)

    # Limpieza
    texto = re.sub(PATRON_TELEFONO, MI_NUMERO, texto)
    texto = re.sub(PATRON_LIMPIEZA_CONTACTO, "", texto, flags=re.DOTALL | re.IGNORECASE)

    return titulo, texto


async def handle_message(update, context):
    mensaje = update.message.text
    link = re.search(r'https?://cabrerapropmdq\.com/[\w\d\-]+/\d+', mensaje)

    if not link:
        await update.message.reply_text("Enviame un enlace válido.")
        return

    enlace = link.group(0)

    # 1️⃣ Mensaje previo
    await update.message.reply_text("🔄 Generando la ficha… un momento por favor…")

    try:
        titulo, texto_limpio = generar_ficha_desde_enlace(enlace)

        # 2️⃣ Creamos ID único
        id_ficha = generar_id_unico()

        # 3️⃣ Creamos enlace final (no existe todavía)
        enlace_final = DOMINIO_FICHAS + id_ficha

        # 4️⃣ Mensaje principal
        await update.message.reply_text(f"🔗 Aquí tienes tu ficha:\n{enlace_final}")

        # 5️⃣ Mensaje que genera la tarjeta/preview para enviar a clientes
        await update.message.reply_text(
            f"Encontré esta propiedad que te puede interesar:\n{enlace_final}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()