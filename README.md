# ProyectoBot - Comparador de Precios Multi-Tienda

Bot de Telegram que busca productos en **8 tiendas peruanas** simultáneamente y muestra los mejores precios.

## Tiendas Soportadas
- MercadoLibre
- Falabella
- Promart
- Oechsle
- Ripley
- Linio
- Sodimac
- PlazaVea

## Uso

En Telegram, simplemente escribe el producto que buscas:
```
laptop gamer
```

El bot buscará en todas las tiendas y te mostrará el Top 15 ordenado por precio.

## Comandos
- `/start` - Ver comandos disponibles
- `/p [producto]` - Buscar producto
- `/b [keyword]` - Buscar empleos en LinkedIn

## Instalación Local

```bash
# Clonar e instalar
cd proyectobot
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium

# Configurar
copy .env.example .env
# Editar .env con tu TELEGRAM_BOT_TOKEN

# Ejecutar
python main.py
```

## Deploy en Railway

1. Sube este proyecto a GitHub
2. Ve a [railway.app](https://railway.app) y conecta tu repo
3. En Railway, añade la variable de entorno:
   - `TELEGRAM_BOT_TOKEN` = tu token
4. Deploy automático

## Arquitectura
- **Patrón Strategy**: Cada tienda es una configuración, no una clase
- **Patrón Factory**: `registry.py` crea scrapers dinámicamente
- **Playwright**: Navegador headless para scraping
