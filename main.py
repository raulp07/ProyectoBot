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
    await update.message.reply_text(f"🛒 Buscando *{query}* en {len(store_names)} tiendas...", parse_mode="Markdown")
    
    # --- Patrón Aggregator + Factory con Límite de Concurrencia ---
    sem = asyncio.Semaphore(4) 
    scrapers = get_all_scrapers()
    
    all_results = []
    status_lines = []

    async def wrapped_search(scraper):
        async with sem:
            try:
                import random
                await asyncio.sleep(random.uniform(0.3, 0.8))
                results = await scraper.search(query)
                count = len(results) if results else 0
                return (scraper.store_name, results, count, None)
            except Exception as e:
                return (scraper.store_name, [], 0, str(e))

    tasks = [wrapped_search(s) for s in scrapers]
    results_lists = await asyncio.gather(*tasks)
    
    # Procesar resultados y generar reporte
    for store_name, results, count, error in results_lists:
        if error:
            status_lines.append(f"❌ {store_name}: Error ({error[:30]}...)")
            logger.error(f"❌ {store_name}: {error}")
        elif count > 0:
            status_lines.append(f"✅ {store_name}: {count} productos")
            all_results.extend(results)
            logger.info(f"✅ {store_name}: {count} productos")
        else:
            status_lines.append(f"⚠️ {store_name}: 0 productos")
            logger.warning(f"⚠️ {store_name}: 0 productos")
    
    # Enviar reporte de estado de tiendas
    await update.message.reply_text("📊 **Reporte por tienda:**\n" + "\n".join(status_lines), parse_mode="Markdown")
    
    if not all_results:
        await update.message.reply_text("😕 No se encontraron productos. Intenta con otra búsqueda.")
        return

    # Filtrar productos con precio 0 y ordenar
    all_results = [p for p in all_results if p.price > 0]
    all_results.sort(key=lambda x: x.price)

    if not all_results:
        await update.message.reply_text("😕 Se encontraron productos pero sin precio válido.")
        return

    # Mostrar Top 15
    lines = [f"🏆 **Top {min(15, len(all_results))} mejores precios:**\n"]
    for prod in all_results[:15]:
        title_short = prod.title[:35] + "..." if len(prod.title) > 35 else prod.title
        lines.append(f"• S/ {prod.price:,.2f} [{prod.source}]\n  [{title_short}]({prod.url})")
        
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown", disable_web_page_preview=True)

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
