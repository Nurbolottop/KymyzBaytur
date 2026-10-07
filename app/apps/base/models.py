from functools import lru_cache

from django.contrib.staticfiles import finders
from django.db import models
from django.templatetags.static import static


@lru_cache(maxsize=None)
def _prefer_webp(path):
    """Для статичных .jpg/.png отдаём лёгкую .webp-копию, если она лежит рядом."""
    stem, dot, ext = path.rpartition('.')
    if dot and ext.lower() in ('jpg', 'jpeg', 'png') and finders.find(f'{stem}.webp'):
        return f'{stem}.webp'
    return path


class StaticImageMixin(models.Model):
    """Картинка из админки, а если её нет — файл из static/ (стартовый контент)."""

    image = models.ImageField('Изображение', upload_to='uploads/%Y/%m/', blank=True)
    static_image = models.CharField(
        'Картинка из static',
        max_length=255,
        blank=True,
        help_text='Путь внутри static/, например img/room-lux.jpg. '
                  'Используется, только если не загружено изображение.',
    )

    class Meta:
        abstract = True

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        if self.static_image:
            return static(_prefer_webp(self.static_image))
        return static('img/hero-mountains.webp')


class SiteSettings(models.Model):
    name = models.CharField('Название', max_length=120, default='Кымызолечебница «Байтур»')
    slogan = models.CharField('Слоган', max_length=255, blank=True)
    phone = models.CharField('Телефон', max_length=40, help_text='В формате +996 770 797 370')
    phone_2 = models.CharField('Доп. телефон', max_length=40, blank=True)
    whatsapp = models.CharField(
        'WhatsApp (только цифры)', max_length=20,
        help_text='Например 996770797370',
    )
    whatsapp_link = models.URLField('Ссылка WhatsApp', blank=True)
    instagram = models.URLField('Instagram', blank=True)
    email = models.EmailField('E-mail', blank=True)
    address = models.CharField('Адрес', max_length=255)
    address_note = models.CharField('Как добраться (кратко)', max_length=255, blank=True)
    map_link = models.URLField('Ссылка на карту (2GIS)', blank=True)
    map_embed = models.URLField('Встраиваемая карта (iframe src)', blank=True)
    season = models.CharField('Сезон', max_length=120, blank=True)
    working_hours = models.CharField('Режим работы', max_length=120, blank=True)

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj = cls.objects.filter(pk=1).first()
        return obj or cls(pk=1)

    @staticmethod
    def _tel(number):
        return 'tel:+' + ''.join(ch for ch in number if ch.isdigit())

    @property
    def phone_href(self):
        return self._tel(self.phone)

    @property
    def phone_2_href(self):
        return self._tel(self.phone_2) if self.phone_2 else ''

    @property
    def whatsapp_href(self):
        return self.whatsapp_link or f'https://wa.me/{self.whatsapp}'


class HeroSlide(StaticImageMixin):
    eyebrow = models.CharField('Надзаголовок', max_length=120, blank=True)
    title = models.CharField('Заголовок', max_length=160)
    subtitle = models.CharField('Подзаголовок', max_length=255, blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        verbose_name = 'Слайд на главной'
        verbose_name_plural = 'Слайды на главной'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title
