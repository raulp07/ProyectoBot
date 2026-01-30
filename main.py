"""
Punto de Entrada Principal (Main)
---------------------------------
Orquesta todo el sistema. Registra los comandos y las dependencias.

# Patrón Command:
Mapea comandos de texto (/b, /p) a funciones ejecutoras.

# C# Equivalente:
# Program.cs en una Console App o Worker Service.
# var host = Host.CreateDefaultBuilder(args).ConfigureServices(...).Build();
# host.Run();
"""
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from config.settings import TELEGRAM_BOT_TOKEN
from core.logger import setup_logger
from core.browser import BrowserManager
from domains.jobs.linkedin import LinkedInScraper
# Nuevo: Import simplificado usando el Registry
from domains.commerce.registry import get_all_scrapers
from domains.commerce.stores_config import get_all_store_names
from adapters.telegram_adapter import TelegramAdapter

logger = setup_logger("Main")

# --- Command Handlers (Manejadores de Comandos) ---

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    store_names = ", ".join(get_all_store_names())
    await update.message.reply_text(
        "🤖 **Bot Multi-Propósito Iniciado**\n\n"
        "Comandos disponibles:\n"
        "💼 `/b [texto]` -> Buscar Empleos (LinkedIn)\n"
        f"🛒 `/p [texto]` -> Buscar Productos en: {store_names}\n"
        "O simplemente escribe 'ok' para pruebas."
    )

async def cmd_buscar_empleo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador para búsqueda de empleos."""
    query = " ".join(context.args) if context.args else ".net backend"
    
    await update.message.reply_text(f"💼 Buscando empleos: *{query}*...")
    
    # Inyección de Dependencia Manual
    scraper = LinkedInScraper()
    results = await scraper.search(query, location="Lima, Peru")
    
    if not results:
        await update.message.reply_text("❌ No se encontraron ofertas.")
        return

    # Formateo de respuesta (Presenter)
    lines = [f"✅ Encontrados {len(results)} empleos:\n"]
    for job in results[:10]:
        lines.append(f"• [{job.title}]({job.url}) - {job.company}")
        
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_buscar_producto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador para búsqueda de productos."""
    query = " ".join(context.args) if context.args else "iphone 15"
    
    store_names = get_all_store_names()
    await update.message.reply_text(f"🛒 Buscando *{query}* en {len(store_names)} tiendas...")
    
    # --- Patrón Aggregator + Factory con Límite de Concurrencia ---
    # Railway tiene poca RAM (512MB). Si abrimos 8 navegadores a la vez, explota.
    # Usamos un Semáforo para que solo corran 2 al mismo tiempo.
    sem = asyncio.Semaphore(2) 
    scrapers = get_all_scrapers()

    async def wrapped_search(scraper):
        async with sem:
            try:
                return await scraper.search(query)
            except Exception as e:
                logger.error(f"Error en {scraper.store_name}: {e}")
                return []

    tasks = [wrapped_search(s) for s in scrapers]
    results_lists = await asyncio.gather(*tasks)
    
    all_results = []
    for res in results_lists:
        if isinstance(res, list):
            all_results.extend(res)
    
    if not all_results:
        await update.message.reply_text("❌ No se encontraron productos.")
        return

    # Ordenar por precio (el más barato primero)
    all_results.sort(key=lambda x: x.price)

    lines = [f"✅ Encontrados {len(all_results)} productos:\n"]
    for prod in all_results[:15]: # Top 15 mejores precios
        lines.append(f"• **S/ {prod.price:,.2f}** [{prod.source}] [{prod.title}]({prod.url})")
        
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    await update.message.reply_text("✅ Búsqueda finalizada.")

# Handler para búsqueda directa (sin /p)
async def handle_text_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cualquier texto que no sea un comando se trata como búsqueda de producto."""
    text = update.message.text.strip()
    if text and not text.startswith("/"):
        # Simular como si hubieran escrito /p texto
        context.args = text.split()
        await cmd_buscar_producto(update, context)

# --- Main Logic ---

def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("No se encontró el token de Telegram. Revisa config/settings.py o .env")
        return

    # C# Equivalente: services.AddSingleton<BotApplication>();
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Registro de Comandos (Command Registry)
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("b", cmd_buscar_empleo)) # Alias corto
    app.add_handler(CommandHandler("p", cmd_buscar_producto))
    
    # Handler para texto directo (sin comando /p)
    # Cualquier mensaje de texto se interpreta como búsqueda de productos
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_search))

    logger.info("🤖 Bot escuchando...")
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        # Aseguramos cerrar recursos (Dispose pattern)
        # Nota: En V2 esto debería ser async, pero python-telegram-bot maneja su propio loop.
        # BrowserManager.close() se llamaría idealmente en un shutdown hook.
        pass
