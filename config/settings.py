"""
Módulo de Configuración Global
------------------------------
Aquí centralizamos todas las variables de entorno y constantes.

# C# Equivalente:
# Sería similar a una clase `AppSettings` que lee de `appsettings.json` o `Environment.GetEnvironmentVariable`.
# public static class AppSettings {
#     public static string TelegramToken => Environment.GetEnvironmentVariable("TELEGRAM_BOT_TOKEN");
#     ...
# }
"""
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env si existe
load_dotenv()

# --- Telegram ---
# El token es obligatorio. Si no está, el bot no puede arrancar.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- Browser (Playwright) ---
# Define si el navegador se abre visible (False) o invisible (True).
# C# Equivalente: bool Headless = bool.Parse(...)
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "true").lower() == "true"

# --- Defaults ---
DEFAULT_LOCATION = "Lima, Peru"
DEFAULT_JOB_KEYWORDS = ".net backend"

# --- Credenciales (Jobs) ---
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
BUMERAN_EMAIL = os.getenv("BUMERAN_EMAIL", "")
BUMERAN_PASSWORD = os.getenv("BUMERAN_PASSWORD", "")
