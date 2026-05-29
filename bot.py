import os
import asyncio
from telethon import TelegramClient, events
import yt_dlp
from aiohttp import web

# Берем настройки из сервера
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

bot = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern=r'(https?://[^\s]+)'))
async def handle_link(event):
    url = event.text
    
    # Отсекаем Ютуб и ТикТок
    if any(x in url.lower() for x in ['youtube.com', 'youtu.be', 'tiktok.com', 'vt.tiktok']):
        return await event.respond("❌ Ютуб и ТикТок отключены.")

    msg = await event.respond("⏳ Качаю...")
    
    def download():
        opts = {
            'format': 'best', 
            'outtmpl': 'video_%(id)s.%(ext)s', 
            'max_filesize': 500 * 1024 * 1024, # 500 МБ
            'quiet': True,
            'noplaylist': True
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
        except Exception:
            return None

    path = await asyncio.to_thread(download)
    
    if path and os.path.exists(path):
        await msg.edit("✅ Отправляю...")
        await bot.send_file(event.chat_id, path)
        os.remove(path)
    else:
        await msg.edit("❌ Ошибка или файл больше 500 МБ.")

# Заглушка для хостинга, чтобы он думал, что мы веб-сайт и не выключал бота
async def web_server():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is online!"))
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, '0.0.0.0', int(os.environ.get("PORT", 10000))).start()

async def main():
    await web_server()
    await bot.run_until_disconnected()

if __name__ == '__main__':
    bot.loop.run_until_complete(main())
  
