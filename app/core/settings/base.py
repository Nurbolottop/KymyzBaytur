from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

# =============================================================================
# PATHS (ПУТИ)
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================================
# SECURITY (БЕЗОПАСНОСТЬ)
# =============================================================================
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise Exception("SECRET_KEY не задан в переменных окружения")

_allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '').strip()
ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts_env.split(',') if host.strip()]

_csrf_trusted_origins_env = os.getenv('CSRF_TRUSTED_ORIGINS', '').strip()
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in _csrf_trusted_origins_env.split(',') if origin.strip()
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# =============================================================================
# APPLICATIONS (ПРИЛОЖЕНИЯ)
# =============================================================================

INSTALLED_APPS = [
    # Тема админки — до django.contrib.admin
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third-party
    'ckeditor',
    'ckeditor_uploader',
    'django_resized',

    # Local apps
    'apps.base',
    'apps.cms',
    'apps.contacts',
]

# =============================================================================
# MIDDLEWARE (ПРОМЕЖУТОЧНЫЕ ОБРАБОТЧИКИ)
# =============================================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =============================================================================
# URLS & WSGI (МАРШРУТЫ И WSGI)
# =============================================================================

ROOT_URLCONF = 'core.urls'
WSGI_APPLICATION = 'core.wsgi.application'


# =============================================================================
# TEMPLATES (ШАБЛОНЫ)
# =============================================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.base.context_processors.site_settings',
            ],
        },
    },
]

# =============================================================================
# DATABASE (БАЗА ДАННЫХ)
# =============================================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': int(os.getenv('POSTGRES_PORT', 5432)),
    }
}

# Локальный запуск без Docker: USE_SQLITE=1 python manage.py runserver
if os.getenv('USE_SQLITE') == '1':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# =============================================================================
# PASSWORD VALIDATION (ВАЛИДАЦИЯ ПАРОЛЕЙ)
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# =============================================================================
# INTERNATIONALIZATION (ИНТЕРНАЦИОНАЛИЗАЦИЯ)
# =============================================================================

LANGUAGE_CODE = os.getenv('LANGUAGE_CODE', 'ru')
TIME_ZONE = os.getenv('TIME_ZONE', 'Asia/Bishkek')
USE_I18N = True
USE_TZ = True

# =============================================================================
# STATIC & MEDIA FILES (СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ)
# =============================================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# =============================================================================
# DEFAULTS (ЗНАЧЕНИЯ ПО УМОЛЧАНИЮ)
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# =============================================================================
# CKEDITOR (РЕДАКТОР CKEDITOR)
# =============================================================================

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}


# =============================================================================
# TELEGRAM (УВЕДОМЛЕНИЯ О ЗАЯВКАХ)
# =============================================================================
# Если оба значения заданы — новые заявки на бронь и сообщения
# дублируются в Telegram. Пустые значения = уведомления выключены.
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')


# =============================================================================
# АДМИНКА (DJANGO UNFOLD)
# =============================================================================
from django.templatetags.static import static  # noqa: E402
from django.urls import reverse_lazy  # noqa: E402


def _admin_badge(model_path, **filters):
    """Счётчик для пункта бокового меню: сколько записей ждут внимания."""
    def callback(request):
        from django.apps import apps
        count = apps.get_model(model_path).objects.filter(**filters).count()
        return count or None
    return callback


UNFOLD = {
    'SITE_TITLE': 'Байтур — админка',
    'SITE_HEADER': 'Байтур',
    'SITE_SUBHEADER': 'Кымызолечебница',
    'SITE_URL': '/',
    'SITE_ICON': lambda request: static('img/logo-sm.webp'),
    'SITE_FAVICONS': [{'rel': 'icon', 'sizes': '64x64', 'type': 'image/png', 'href': lambda request: static('img/favicon.png')}],
    'SHOW_HISTORY': True,
    'SHOW_VIEW_ON_SITE': True,
    'DASHBOARD_CALLBACK': 'apps.base.dashboard.dashboard_callback',
    'STYLES': [lambda request: static('admin-theme/unfold.css')],
    'COLORS': {
        # Фирменный синий логотипа (#0d3a99) — основной цвет кнопок и акцентов
        'primary': {
            '50': 'oklch(97% .014 264)',
            '100': 'oklch(93.5% .032 264)',
            '200': 'oklch(87% .065 264)',
            '300': 'oklch(78% .11 264)',
            '400': 'oklch(66% .17 264)',
            '500': 'oklch(56% .21 264)',
            '600': 'oklch(48% .2 264)',
            '700': 'oklch(41% .18 264)',
            '800': 'oklch(35% .15 264)',
            '900': 'oklch(29% .12 264)',
            '950': 'oklch(20% .08 264)',
        },
        # Тёплый нейтральный — фон и рамки в тон молочному фону сайта
        'base': {
            '50': 'oklch(98.4% .004 85)',
            '100': 'oklch(96.4% .007 85)',
            '200': 'oklch(92.5% .011 85)',
            '300': 'oklch(86.5% .014 85)',
            '400': 'oklch(70.5% .02 264)',
            '500': 'oklch(55% .027 264)',
            '600': 'oklch(44.5% .03 264)',
            '700': 'oklch(37% .035 264)',
            '800': 'oklch(27.5% .04 264)',
            '900': 'oklch(20.5% .045 264)',
            '950': 'oklch(14% .04 264)',
        },
    },
    'SIDEBAR': {
        'show_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': 'Главное',
                'items': [
                    {'title': 'Обзор', 'icon': 'dashboard', 'link': reverse_lazy('admin:index')},
                    {'title': 'Заявки на бронь', 'icon': 'event_available',
                     'link': reverse_lazy('admin:contacts_bookingrequest_changelist'),
                     'badge': _admin_badge('contacts.BookingRequest', status='new')},
                    {'title': 'Сообщения с сайта', 'icon': 'mail',
                     'link': reverse_lazy('admin:contacts_contactmessage_changelist'),
                     'badge': _admin_badge('contacts.ContactMessage', is_processed=False)},
                    {'title': 'Отзывы', 'icon': 'reviews',
                     'link': reverse_lazy('admin:cms_review_changelist'),
                     'badge': _admin_badge('cms.Review', is_published=False)},
                ],
            },
            {
                'title': 'Контент сайта',
                'collapsible': True,
                'items': [
                    {'title': 'Номера и юрты', 'icon': 'bed', 'link': reverse_lazy('admin:cms_room_changelist')},
                    {'title': 'Услуги и прайс', 'icon': 'spa', 'link': reverse_lazy('admin:cms_servicecategory_changelist')},
                    {'title': 'Акции', 'icon': 'sell', 'link': reverse_lazy('admin:cms_promo_changelist')},
                    {'title': 'Галерея', 'icon': 'photo_library', 'link': reverse_lazy('admin:cms_galleryimage_changelist')},
                    {'title': 'Частые вопросы', 'icon': 'help', 'link': reverse_lazy('admin:cms_faq_changelist')},
                    {'title': 'Слайды на главной', 'icon': 'view_carousel', 'link': reverse_lazy('admin:base_heroslide_changelist')},
                ],
            },
            {
                'title': 'Настройки',
                'collapsible': True,
                'items': [
                    {'title': 'Контакты и сайт', 'icon': 'settings', 'link': reverse_lazy('admin:base_sitesettings_changelist')},
                    {'title': 'Пользователи', 'icon': 'person', 'link': reverse_lazy('admin:auth_user_changelist')},
                    {'title': 'Группы', 'icon': 'group', 'link': reverse_lazy('admin:auth_group_changelist')},
                ],
            },
        ],
    },
}
