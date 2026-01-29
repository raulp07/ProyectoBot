"""
Adaptador de Telegram
---------------------
Implementa INotifier usando python-telegram-bot.
Permite que el Core envíe mensajes sin saber que es Telegram.

# Patrón Adapter:
Adapta la interfaz de Telegram (bot.send_message) a nuestra interfaz INotifier.

# C# Equivalente:
# public class TelegramAdapter : INotifier {
#     private TelegramBotClient _client;
#     public async Task SendMessageAsync(string chatId, string text) { ... }
# }
"""
from telegram import Bot
from telegram.constants import ParseMode
from core.interfaces import INotifier
from config.settings import TELEGRAM_BOT_TOKEN
from core.logger import setup_logger

logger = setup_logger("TelegramAdapter")

class TelegramAdapter(INotifier):
    
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN:
            logger.warning("No hay token de Telegram configurado.")
            self.bot = None
        else:
            self.bot = Bot(token=TELEGRAM_BOT_TOKEN)

    async def send_message(self, chat_id: str, text: str) -> bool:
        if not self.bot:
            return False
        try:
            # Enviamos con Markdown habilitado
            await self.bot.send_message(
                chat_id=chat_id, 
                text=text, 
                parse_mode=ParseMode.MARKDOWN
            )
            return True
        except Exception as e:
            logger.error(f"Error enviando mensaje a {chat_id}: {e}")
            return False
