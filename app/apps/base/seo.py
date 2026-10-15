"""Структурированные данные Schema.org (JSON-LD) для поисковиков."""
from django.templatetags.static import static

# Точка на карте из 2GIS (карточка «Байтур Резорт»)
GEO = {'latitude': 42.235104, 'longitude': 73.713022}

# Другие названия, под которыми нас ищут и упоминают — помогает поисковикам и ИИ
# связать все упоминания с одним местом
ALTERNATE_NAMES = [
    'Байтур', 'Кумысолечебница Байтур', 'Кымызолечебница Байтур', 'Байтур Резорт',
    'Kymyz Baytur', 'Baytur Kymyz Therapy', 'Кымыз Байтур Суусамыр',
]

KNOWS_ABOUT = [
    'Кумысолечение', 'Кымызолечение', 'Кымыз дарылоо', 'Кумыс', 'Кобылье молоко', 'Саамал',
    'Отдых в юрте', 'Суусамырская долина', 'Отдых в горах Кыргызстана',
]


def absolute(request, path):
    return request.build_absolute_uri(path)


def lodging_business(request, site, rooms=None, rating=None):
    data = {
        '@context': 'https://schema.org',
        '@type': 'LodgingBusiness',
        '@id': absolute(request, '/#business'),
        'name': site.name,
        'alternateName': ALTERNATE_NAMES,
        'slogan': 'Кымыз дарылоо · Kymyz Therapy',
        'description': 'Кумысолечебница (кымызолечебница) «Байтур» в Суусамырской долине Кыргызстана, '
                       '3 часа от Бишкека. Натуральный кумыс от своих кобылиц 5 раз в день, юрты и коттеджи, '
                       'трёхразовое питание, баня, массаж, конные прогулки. Сезон — с мая по сентябрь.',
        'knowsAbout': KNOWS_ABOUT,
        'areaServed': ['Кыргызстан', 'Бишкек', 'Казахстан', 'Чуйская область'],
        'hasMap': 'https://2gis.kg/bishkek/geo/70000001071813605',
        'isAccessibleForFree': False,
        'petsAllowed': False,
        'containedInPlace': {'@type': 'Place', 'name': 'Суусамырская долина',
                             'address': {'@type': 'PostalAddress', 'addressCountry': 'KG'}},
        'url': absolute(request, '/'),
        'logo': absolute(request, static('img/logo.png')),
        'image': [absolute(request, static(f'img/{name}.webp'))
                  for name in ('hero-mountains', 'yurt-beds', 'room-lux', 'hero-valley')],
        'telephone': site.phone,
        'priceRange': '2500–12880 KGS',
        'currenciesAccepted': 'KGS',
        'address': {
            '@type': 'PostalAddress',
            'addressCountry': 'KG',
            'addressRegion': 'Чуйская область',
            'addressLocality': 'Суусамырская долина',
            'streetAddress': site.address,
        },
        'geo': {'@type': 'GeoCoordinates', **GEO},
        'amenityFeature': [
            {'@type': 'LocationFeatureSpecification', 'name': name, 'value': True}
            for name in ('Кымызолечение', 'Трёхразовое питание', 'Баня и сауна', 'Массаж',
                         'Конные прогулки', 'Wi-Fi', 'Трансфер из Бишкека')
        ],
        'sameAs': [url for url in (site.instagram, site.map_link) if url],
        # Связь с другими проектами компании — чтобы поисковики и ИИ не путали места
        'parentOrganization': {
            '@type': 'Organization',
            'name': 'Байтур',
            'url': 'https://baytur.kg/',
            'subOrganization': [
                {'@type': 'Resort', 'name': 'Baytur Resort & Spa (Иссык-Куль)', 'url': 'https://resort.baytur.kg/'},
                {'@type': 'SkiResort', 'name': 'Горнолыжная база Байтур (Тоо-Ашуу)', 'url': 'https://ski.baytur.kg/'},
            ],
        },
    }
    if rooms:
        prices = [rate.price_full for room in rooms for rate in room.rates.all()]
        if prices:
            data['priceRange'] = f'{min(prices)}–{max(prices)} KGS'
        data['makesOffer'] = [
            {
                '@type': 'Offer',
                'name': room.name,
                'url': absolute(request, room.get_absolute_url()),
                'priceCurrency': 'KGS',
                'price': room.min_price,
                'description': 'Цена за сутки с трёхразовым питанием и пятиразовым кобыльим молоком',
            }
            for room in rooms if room.min_price
        ]
    if rating and rating.get('count'):
        data['aggregateRating'] = {
            '@type': 'AggregateRating',
            'ratingValue': round(rating['avg'], 1),
            'reviewCount': rating['count'],
            'bestRating': 5,
        }
    return data


def reviews_page(request, site, reviews, rating):
    data = lodging_business(request, site, rating=rating)
    data['review'] = [
        {
            '@type': 'Review',
            'author': {'@type': 'Person', 'name': review.name},
            'reviewBody': review.text,
            'reviewRating': {'@type': 'Rating', 'ratingValue': review.rating, 'bestRating': 5},
            'datePublished': review.created_at.date().isoformat(),
        }
        for review in reviews[:20]
    ]
    return data


def room_page(request, site, room):
    data = {
        '@context': 'https://schema.org',
        '@type': 'HotelRoom',
        'name': room.name,
        'description': room.short_description,
        'url': absolute(request, room.get_absolute_url()),
        'image': absolute(request, room.image_url),
        'occupancy': {'@type': 'QuantitativeValue', 'maxValue': room.capacity},
        'bed': room.beds,
        'containedInPlace': {'@id': absolute(request, '/#business'), '@type': 'LodgingBusiness', 'name': site.name},
        'offers': {
            '@type': 'Offer',
            'priceCurrency': 'KGS',
            'price': room.min_price,
            'description': 'Цена за сутки с питанием и кымызом',
        } if room.min_price else None,
    }
    return {k: v for k, v in data.items() if v is not None}


def breadcrumbs(request, items):
    return {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': i, 'name': name, 'item': absolute(request, url)}
            for i, (name, url) in enumerate(items, start=1)
        ],
    }



def website(request, site):
    """Сайт как сущность: название и связь с организацией."""
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': absolute(request, '/#website'),
        'url': absolute(request, '/'),
        'name': site.name,
        'alternateName': ALTERNATE_NAMES,
        'inLanguage': 'ru-RU',
        'publisher': {'@id': absolute(request, '/#business')},
    }


def faq_page(questions):
    """Вопросы-ответы — ИИ-поиск и Google берут отсюда готовые ответы."""
    return {
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        'mainEntity': [
            {'@type': 'Question', 'name': question,
             'acceptedAnswer': {'@type': 'Answer', 'text': answer}}
            for question, answer in questions
        ],
    }


def offer_catalog(request, categories):
    """Услуги с ценами из прайса."""
    return {
        '@context': 'https://schema.org',
        '@type': 'LodgingBusiness',
        '@id': absolute(request, '/#business'),
        'hasOfferCatalog': {
            '@type': 'OfferCatalog',
            'name': 'Услуги кумысолечебницы «Байтур»',
            'itemListElement': [
                {
                    '@type': 'OfferCatalog',
                    'name': category.name,
                    'itemListElement': [
                        {
                            '@type': 'Offer',
                            'itemOffered': {'@type': 'Service', 'name': item.name,
                                            **({'description': item.note} if item.note else {})},
                            'priceSpecification': {'@type': 'PriceSpecification', 'priceCurrency': 'KGS',
                                                   'description': f'{item.price}' + (f', {item.duration}' if item.duration else '')},
                        }
                        for item in category.items.all()
                    ],
                }
                for category in categories
            ],
        },
    }


def webpage(request, title, description, page_type='WebPage'):
    return {
        '@context': 'https://schema.org',
        '@type': page_type,
        '@id': request.build_absolute_uri(request.path) + '#webpage',
        'url': request.build_absolute_uri(request.path),
        'name': title,
        'description': description,
        'inLanguage': 'ru-RU',
        'isPartOf': {'@id': absolute(request, '/#website')},
        'about': {'@id': absolute(request, '/#business')},
    }
