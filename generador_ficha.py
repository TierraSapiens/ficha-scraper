#--------------------------
# Generador ficha V 1.1
# -------------------------
from telegram.ext import Application, MessageHandler, filters
import re
import requests
from bs4 import BeautifulSoup 
import sys

# ----------------------------------------------------------------------
# Configuracion del Usuario
# ----------------------------------------------------------------------
MI_NUMERO = "+54 9 2235385001"
TELEGRAM_BOT_TOKEN = '8586713628:AAFm9sVd_aysUs3cmux9dOkiWQZK6U152Vc'
LINK_PRUEBA = "https://cabrerapropmdq.com/apartamento-venta-centro-mar-del-plata/9627731?shared=whatsapp" 
PATRON_TELEFONO = r'(?:\+\d{1,3}\s?\d{2,4}\s?[\s\d]{4}[-\s]?\d{4,6})|(?:\d{3,5}[-\s]?\d{4}[-\s]?\d{4})'
PATRON_LIMPIEZA_CONTACTO = r'(?:Contáctanos Cabrera Propiedades.*|Escribania designada:.*)'

def generar_ficha_desde_enlace(enlace_ficha):
    print("-" * 50)
    print(f"Iniciando Web Scraping en: {enlace_ficha}")
    print("-" * 50)

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8'
        }
        response = requests.get(enlace_ficha, headers=headers, timeout=10)
        response.raise_for_status() 
        sopa = BeautifulSoup(response.text, 'html.parser')
        
        titulo_elem = sopa.find('h2', class_='title-sup-property')
        titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Título no encontrado"
        
        descripcion_elem = sopa.find('article', id='article-container')
        
        if descripcion_elem:
            descripcion_limpia = descripcion_elem.get_text(separator=' ', strip=True)
            texto_de_la_ficha = f"{titulo} {descripcion_limpia}"
            print(f"✅ Título encontrado: {titulo}")
            print("✅ Descripción extraída con éxito.")
        else:
            texto_de_la_ficha = sopa.find('body').get_text(separator=' ', strip=True)
            print("⚠️ Advertencia: Usando texto completo del cuerpo.")
            
# ... (Bloque try) ...
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ Error de red al acceder a la ficha: {e}"
        print(error_msg)
        return error_msg

    numeros_encontrados = re.findall(PATRON_TELEFONO, texto_de_la_ficha)

    if not numeros_encontrados:
        mensaje_no_numeros = "\n✅ No se encontraron números. Ficha procesada sin cambios."
        print(mensaje_no_numeros)
        return texto_de_la_ficha + mensaje_no_numeros
    print("\n" + "=" * 50)
    print(f"⚠️ CONTROL: Números encontrados:")
    numeros_unicos = sorted(list(set(n.strip() for n in numeros_encontrados if n.strip())))
    for num in numeros_unicos: 
        print(f"- {num}")
    print("=" * 50)
    confirmacion = 'S'
    
    if confirmacion == 'S':

        texto_modificado = re.sub(PATRON_TELEFONO, MI_NUMERO, texto_de_la_ficha)
        
        # Lógica de corte (solo si existe la frase)
        if "Buscar Departamento" in texto_modificado:
            texto_modificado = texto_modificado.split("Buscar Departamento")[-1]
            texto_modificado = "Departamento" + texto_modificado
        
        # ✅ CORRECCIÓN: Esta línea de limpieza se ejecuta siempre,
        # asegurando que texto_modificado_limpio exista.
        texto_modificado_limpio = re.sub(PATRON_LIMPIEZA_CONTACTO, "", texto_modificado, flags=re.DOTALL | re.IGNORECASE)

        print("\n🎉 Publicación Modificada (Copia y Pega):")
        print("=" * 50)
        print(texto_modificado_limpio)
        print("=" * 50)
        return texto_modificado_limpio
    else:
        print("\n❌ Cancelado.")
        return "❌ Procesamiento cancelado." # Retornar mensaje en caso de cancelación

# ----------------------------------------------------
# NUEVA FUNCIÓN PRINCIPAL PARA TELEGRAM (CON MEJOR CONTROL)
# ----------------------------------------------------

async def handle_message(update, context):
    """Maneja los mensajes entrantes, busca enlaces y procesa."""
    mensaje_recibido = update.message.text
    
    # 1. Extracción y Verificación de Enlace
    # Intentamos encontrar la URL completa. Esto ayuda a limpiar cualquier texto extra.
    match = re.search(r'https?://cabrerapropmdq\.com/[\w\d\-]+/\d+', mensaje_recibido)

    if match:
        enlace_limpio = match.group(0)
        print(f"🤖 Procesando enlace: {enlace_limpio}")
        
        try:
            # 2. Ejecutar la función de scraping
            ficha_procesada = generar_ficha_desde_enlace(enlace_limpio)
            
            # 3. Responder al usuario
            await update.message.reply_text(ficha_procesada)
            
        except Exception as e:
            # Si el scraping falla por razones internas (BS4, Regex, etc.)
            error_msg = f"❌ ¡ERROR DE PROCESAMIENTO INTERNO! Detalle: {e}"
            print(error_msg)
            await update.message.reply_text(error_msg)
            
    else:
        # 4. Respuesta si no se encuentra un enlace válido
        await update.message.reply_text("👋 Hola! Por favor, envíame el **enlace completo** de una ficha (debe contener cabrerapropmdq.com).")

if __name__ == "__main__":
    print("🤖 Iniciando Bot (Modo Application v20+)...")
    
    # 1. Construir la Aplicación con el Builder
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # 2. Añadir el manejador (Filtros actualizados)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 3. Iniciar el bot (run_polling se encarga de todo, no hace falta idle)
    print("🚀 Bot escuchando...")
    application.run_polling()