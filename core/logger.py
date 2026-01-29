"""
Sistema de Logging Centralizado
-------------------------------
Configura cómo y dónde se imprimen los mensajes (consola, archivo).

# C# Equivalente:
# Similar a configurar Serilog o NLog en `Program.cs`.
# builder.Services.AddLogging(configure => configure.AddConsole());
"""
import logging
import sys

def setup_logger(name: str = "BotCore") -> logging.Logger:
    """
    Crea y configura un logger.
    
    Args:
        name: El nombre del componente (ej. "LinkedInScraper").
        
    Returns:
        Un objeto Logger listo para usar.
    """
    logger = logging.getLogger(name)
    
    # Si ya tiene handlers, no agregamos más para evitar duplicados
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # Formato: [HORA] [NIVEL] [NOMBRE] Mensaje
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Salida a Consola (Console.WriteLine)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger

# Logger global para el core
core_logger = setup_logger("Core")
