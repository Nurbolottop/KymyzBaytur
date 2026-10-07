from django.db import migrations

SLIDES = [
    {
        'eyebrow': 'Суусамырская долина · Кыргызстан',
        'title': 'Кымызолечение среди гор Суусамыра',
        'subtitle': 'Натуральный кымыз, чистый горный воздух и уют юрт — всего в 3 часах от Бишкека.',
        'static_image': 'img/hero-mountains.jpg',
    },
    {
        'eyebrow': 'Пятиразовое кобылье молоко',
        'title': 'Сила природы в каждой пиале',
        'subtitle': 'Свежий кымыз и саамал от наших кобылиц включены в стоимость проживания.',
        'static_image': 'img/hero-milking.jpg',
    },
    {
        'eyebrow': 'Коттеджи и национальные юрты',
        'title': 'Отдых, который возвращает силы',
        'subtitle': 'Трёхразовое питание, баня, массаж, конные прогулки и река Кокомерен рядом.',
        'static_image': 'img/hero-valley.jpg',
    },
]


def seed(apps, schema_editor):
    SiteSettings = apps.get_model('base', 'SiteSettings')
    HeroSlide = apps.get_model('base', 'HeroSlide')

    SiteSettings.objects.update_or_create(pk=1, defaults={
        'name': 'Кымызолечебница «Байтур»',
        'slogan': 'Кымыз дарылоо · Kymyz Therapy',
        'phone': '+996 770 797 370',
        'whatsapp': '996770797370',
        'whatsapp_link': 'https://wa.me/message/RAZGFAGTISTIA1',
        'instagram': 'https://www.instagram.com/kymyz_baytur_resort/',
        'address': 'Кыргызстан, Чуйская область, Жайылский район, Суусамырская долина',
        'address_note': 'Всего 3 часа от Бишкека · 10 минут до реки Кокомерен',
        'map_link': 'https://2gis.kg/bishkek/geo/70000001071813605',
        'map_embed': 'https://maps.google.com/maps?q=%D0%A1%D1%83%D1%83%D1%81%D0%B0%D0%BC%D1%8B%D1%80%2C+'
                     '%D0%9A%D1%8B%D1%80%D0%B3%D1%8B%D0%B7%D1%81%D1%82%D0%B0%D0%BD&z=10&output=embed',
        'season': 'Сезон кымыза: май — сентябрь',
        'working_hours': 'Отвечаем в WhatsApp ежедневно',
    })

    if not HeroSlide.objects.exists():
        for i, slide in enumerate(SLIDES):
            HeroSlide.objects.create(order=i, **slide)


class Migration(migrations.Migration):
    dependencies = [('base', '0001_initial')]
    operations = [migrations.RunPython(seed, migrations.RunPython.noop)]
