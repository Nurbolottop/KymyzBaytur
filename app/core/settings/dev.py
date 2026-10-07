from core.settings.base import *

DEBUG = True
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Разрешаем iframe с того же домена — удобно для проверки мобильной вёрстки
X_FRAME_OPTIONS = 'SAMEORIGIN'
