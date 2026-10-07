from django.db import models
from django.urls import reverse

from apps.base.models import StaticImageMixin


class Room(StaticImageMixin):
    KIND_COTTAGE = 'cottage'
    KIND_YURT = 'yurt'
    KIND_CHOICES = [
        (KIND_COTTAGE, 'Номер в коттедже'),
        (KIND_YURT, 'Юрта'),
    ]

    name = models.CharField('Название', max_length=120)
    slug = models.SlugField('URL', unique=True)
    kind = models.CharField('Тип', max_length=20, choices=KIND_CHOICES, default=KIND_COTTAGE)
    short_description = models.CharField('Кратко', max_length=255)
    description = models.TextField('Описание')
    capacity = models.PositiveSmallIntegerField('Вместимость, чел.')
    beds = models.CharField('Кровати', max_length=120)
    amenities = models.TextField('Удобства', help_text='Каждое удобство с новой строки')
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера и юрты'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('room_detail', args=[self.slug])

    @property
    def amenities_list(self):
        return [line.strip() for line in self.amenities.splitlines() if line.strip()]

    @property
    def min_price(self):
        prices = [rate.price_full for rate in self.rates.all()]
        return min(prices) if prices else None


class RoomRate(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='rates', verbose_name='Номер')
    guests = models.PositiveSmallIntegerField('Гостей')
    price_full = models.PositiveIntegerField(
        'Цена с питанием и кымызом, сом/сутки',
        help_text='Проживание + трёхразовое питание + пятиразовое кобылье молоко',
    )
    price_room_only = models.PositiveIntegerField(
        'Цена без питания и молока, сом/сутки', null=True, blank=True,
    )
    note = models.CharField('Примечание', max_length=120, blank=True,
                            help_text='Например: «с человека 3150 сом» или «доп. место 2480 сом»')

    class Meta:
        verbose_name = 'Тариф'
        verbose_name_plural = 'Тарифы'
        ordering = ['-guests']

    def __str__(self):
        return f'{self.room} — {self.guests} чел.'


class RoomImage(StaticImageMixin):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='photos', verbose_name='Номер')
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Фото номера'
        verbose_name_plural = 'Фото номера'
        ordering = ['order', 'id']


class ServiceCategory(StaticImageMixin):
    name = models.CharField('Название', max_length=120)
    slug = models.SlugField('Якорь', unique=True)
    icon = models.CharField('Иконка', max_length=40, default='leaf',
                            help_text='Имя иконки из спрайта: leaf, spa, horse, bath, car, yurt, fire, cup')
    description = models.TextField('Описание', blank=True)
    show_on_home = models.BooleanField('Показывать на главной', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Категория услуг'
        verbose_name_plural = 'Услуги и прайс'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class PriceItem(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE,
                                 related_name='items', verbose_name='Категория')
    name = models.CharField('Наименование', max_length=160)
    duration = models.CharField('Время / объём', max_length=60, blank=True)
    price = models.CharField('Цена', max_length=60, help_text='Например: 2000 сом/час')
    note = models.CharField('Примечание', max_length=160, blank=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Позиция прайса'
        verbose_name_plural = 'Позиции прайса'
        ordering = ['order', 'id']

    def __str__(self):
        return self.name


class GalleryImage(StaticImageMixin):
    CATEGORY_CHOICES = [
        ('nature', 'Природа'),
        ('yurts', 'Юрты'),
        ('rooms', 'Номера'),
        ('kymyz', 'Кымыз'),
        ('rest', 'Отдых'),
    ]

    title = models.CharField('Подпись', max_length=160, blank=True)
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES, default='nature')
    order = models.PositiveSmallIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Показывать', default=True)

    class Meta:
        verbose_name = 'Фото галереи'
        verbose_name_plural = 'Галерея'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title or f'Фото #{self.pk}'


class Review(models.Model):
    name = models.CharField('Имя', max_length=80)
    city = models.CharField('Город', max_length=80, blank=True)
    text = models.TextField('Отзыв')
    rating = models.PositiveSmallIntegerField('Оценка', default=5,
                                              choices=[(i, str(i)) for i in range(1, 6)])
    source = models.CharField('Источник', max_length=40, default='Сайт')
    is_published = models.BooleanField('Опубликован', default=False)
    created_at = models.DateTimeField('Дата', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}: {self.text[:40]}'


class Promo(StaticImageMixin):
    badge = models.CharField('Метка', max_length=40, blank=True, help_text='Например: −20%')
    title = models.CharField('Заголовок', max_length=160)
    text = models.TextField('Текст')
    valid_until = models.DateField('Действует до', null=True, blank=True)
    is_active = models.BooleanField('Активна', default=True)
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['order', 'id']

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField('Вопрос', max_length=255)
    answer = models.TextField('Ответ')
    order = models.PositiveSmallIntegerField('Порядок', default=0)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Частые вопросы'
        ordering = ['order', 'id']

    def __str__(self):
        return self.question
