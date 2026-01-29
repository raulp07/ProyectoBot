# Dockerfile para ProyectoBot con Playwright
# Usa la imagen oficial de Playwright que ya tiene Chromium instalado

FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar navegadores de Playwright
RUN playwright install chromium

# Copiar el resto del código
COPY . .

# Variable de entorno para modo headless
ENV BROWSER_HEADLESS=true

# Comando para ejecutar el bot
CMD ["python", "main.py"]
