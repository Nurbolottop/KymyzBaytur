"""Структурированные данные Schema.org (JSON-LD) для поисковиков."""
from django.templatetags.static import static

# Точка на карте из 2GIS (карточка «Байтур Резорт»)
GEO = {'latitude': 42.235104, 'longitude': 73.713022}


def absolute(request, path):
    return request.build_absolute_uri(path)


def lodging_business(request, site, rooms=None, rating=None):
    data = {
        '@context': 'https://schema.org',
        '@type': 'LodgingBusiness',
        '@id': absolute(request, '/#business'),
        'name': site.name,
        'description': 'Кымызолечебница в Суусамырской долине: натуральный кымыз, юрты и коттеджи, '
                       'трёхразовое питание, баня, массаж и конные прогулки.',
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
