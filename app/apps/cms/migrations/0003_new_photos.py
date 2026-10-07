from django.db import migrations

SERVICE_IMAGES = {
    'procedures': 'img/procedures.webp',
    'banya': 'img/sauna.webp',
    'leisure': 'img/leisure-horse.webp',
}

GALLERY = [
    ('img/hero-mountains.webp', 'Юрты на летнем пастбище', 'yurts'),
    ('img/kymyz-pour.webp', 'Свежее молоко', 'kymyz'),
    ('img/yurt-beds.webp', 'Внутри юрты', 'yurts'),
    ('img/chan.webp', 'Горячий чан под открытым небом', 'rest'),
    ('img/river.webp', 'Горная река в долине', 'nature'),
    ('img/hero-milking.webp', 'Кобылица с жеребёнком', 'kymyz'),
    ('img/room-lux.webp', 'Номер «Люкс»', 'rooms'),
    ('img/yurt-camp.webp', 'Юрты среди холмов', 'yurts'),
    ('img/hero-valley.webp', 'Зелёная долина', 'nature'),
    ('img/yurt-ceiling.webp', 'Убранство большой юрты', 'yurts'),
    ('img/guest-girl.webp', 'Прогулка по лугам', 'rest'),
    ('img/room-semilux.webp', 'Номер «Полулюкс»', 'rooms'),
    ('img/yurt-horses.webp', 'Кони у юрты', 'nature'),
    ('img/leisure-horse.webp', 'Конь на горном пастбище', 'nature'),
    ('img/yurt-door.webp', 'Резная дверь юрты', 'yurts'),
    ('img/room-standard.webp', 'Номер «Стандарт»', 'rooms'),
    ('img/yurt-window.webp', 'Вид на горы из окна', 'rest'),
    ('img/sauna.webp', 'Баня', 'rest'),
]


def update(apps, schema_editor):
    ServiceCategory = apps.get_model('cms', 'ServiceCategory')
    GalleryImage = apps.get_model('cms', 'GalleryImage')

    for slug, path in SERVICE_IMAGES.items():
        ServiceCategory.objects.filter(slug=slug, image='').update(static_image=path)

    # Стартовые фото галереи (без загруженных в админке) заменяем новым набором
    GalleryImage.objects.filter(image='').exclude(static_image='').delete()
    for order, (path, title, category) in enumerate(GALLERY):
        GalleryImage.objects.create(static_image=path, title=title, category=category, order=order)


class Migration(migrations.Migration):
    dependencies = [('cms', '0002_seed')]
    operations = [migrations.RunPython(update, migrations.RunPython.noop)]
