from django.db import models


class BookingRequest(models.Model):
    STATUS_NEW = 'new'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Новая'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
    ]

    name = models.CharField('Имя', max_length=120)
    phone = models.CharField('Телефон / WhatsApp', max_length=40)
    check_in = models.DateField('Заезд')
    check_out = models.DateField('Выезд')
    adults = models.PositiveSmallIntegerField('Взрослых', default=2)
    children = models.PositiveSmallIntegerField('Детей', default=0)
    room = models.ForeignKey('cms.Room', on_delete=models.SET_NULL, null=True, blank=True,
                             verbose_name='Номер')
    with_meals = models.BooleanField('С питанием и кымызом', default=True)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Заявка на бронь'
        verbose_name_plural = 'Заявки на бронь'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} {self.check_in:%d.%m}–{self.check_out:%d.%m}'

    @property
    def nights(self):
        return (self.check_out - self.check_in).days


class ContactMessage(models.Model):
    name = models.CharField('Имя', max_length=120)
    phone = models.CharField('Телефон', max_length=40)
    message = models.TextField('Сообщение')
    is_processed = models.BooleanField('Обработано', default=False)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения с сайта'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.phone})'
