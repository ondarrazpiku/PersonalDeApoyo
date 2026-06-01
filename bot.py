import os
import threading
import asyncio
from http.server import SimpleHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai  # <-- Nueva librería oficial de Google

# 1. Configurar la Inteligencia Artificial (Nueva SDK de Gemini)
# El nuevo cliente detecta automáticamente tu variable GEMINI_API_KEY
client = genai.Client()

# 2. Leer tu base de conocimiento
def obtener_base_conocimiento():
    try:
        with open("informacion.txt", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "El archivo de información no está disponible."

# 3. Funciones del Bot de Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("¡Hola! Soy tu asistente. Pregúntame lo que quieras sobre la información que tengo guardada.")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pregunta = update.message.text
    contexto = obtener_base_conocimiento()
    
    prompt = f"""
    Eres un asistente inteligente y fiel. Responde a la pregunta del usuario utilizando ÚNICAMENTE la información provista en el Contexto. 
    Si la respuesta no se encuentra en el Contexto, sé amable y di que no dispones de esa información.

    Contexto:
    {contexto}

    Pregunta: {pregunta}
    Respuesta:
    """
    
    try:
        # Usamos el nuevo método de generación de contenido oficial
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt,
        )
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error IA: {e}")
        await update.message.reply_text("Lo siento, tuve un problema al procesar tu respuesta.")

# 4. Truco para Render: Servidor Web Falso para pasar el Health Check
def run_dummy_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"Servidor de control escuchando en el puerto {port}")
    server.serve_forever()

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Iniciar el servidor falso en un hilo separado
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # Iniciar el Bot de Telegram
    token = os.environ.get("TELEGRAM_TOKEN")
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    
    print("Bot de Telegram iniciado...")
    app.run_polling()

if __name__ == '__main__':
    main()
