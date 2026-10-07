import json
import logging
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram(text):
    """Отправляет сообщение в Telegram, если заданы токен и chat_id. Ошибки не роняют запрос."""
    token, chat_id = settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        return
    payload = json.dumps({'chat_id': chat_id, 'text': text}).encode()
    request = urllib.request.Request(
        f'https://api.telegram.org/bot{token}/sendMessage',
        data=payload,
        headers={'Content-Type': 'application/json'},
    )
    try:
        urllib.request.urlopen(request, timeout=5)
    except Exception:
        logger.exception('Не удалось отправить уведомление в Telegram')
