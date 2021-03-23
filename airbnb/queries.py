def main():
    from django.db.models import Count

    from addresses.models import Address
    from hosts.models import RealtyHost
    from realty.models import Realty, Amenity

    # create addresses
    address1 = Address.objects.create(
        country='Russia',
        city='Moscow',
        street='Bolshaya Molchanovka, 22',
    )
    address2 = Address(
        country='Italy',
        city='Rome',
        street='Via Nomentana',
    )
    address2.save()

    # get host
    host: RealtyHost = RealtyHost.objects.first()

    # create amenities
    amenity_wifi = Amenity.objects.first()
    amenity_washer = Amenity.objects.create(name='washer')
    amenity_breakfast = Amenity(name='breakfast')
    amenity_breakfast.save()

    # create realty
    realty1 = Realty.objects.create(
        name='SMART HOST | Bright studio | 2 guests',
        slug='smart-host-bright-studio-2-guests',
        description='Comfortable and cozy apartment situated in the centre of the city, 21 floor. '
                    'One of the best views paired with perfect location.',
        beds_count=2,
        max_guests_count=4,
        price_per_night=65,
        location=address1,
        host=host,
    )
    realty1.amenities.add(amenity_wifi, amenity_washer)  # add many-to-many fields

    realty2 = Realty.objects.create(
        name="Napoleon's Boutique",
        slug='napoleons-boutique',
        description='The apartment is located in a vintage building in the centre of the city, '
                    'it is elegantly furnished and equipped with all the comforts required for a pleasant holiday.',
        beds_count=3,
        max_guests_count=6,
        price_per_night=30,
        location=address2,
        host=host,
    )
    realty2.amenities.add(amenity_wifi, amenity_breakfast)  # add many-to-many fields

    # all realty
    print(Realty.objects.all())

    # filtered realty
    required_amenities = [amenity_wifi, amenity_washer]
    filtered_realty = Realty.objects.filter(
        amenities__in=required_amenities,
        max_guests_count__gte=4,
        location__city__iexact='moscow'
    ).annotate(amenities_count=Count('amenities')).\
        filter(amenities_count=len(required_amenities))

    for realty in filtered_realty:
        print(realty.name)


if __name__ == '__main__':
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'airbnb.settings')

    import django
    django.setup()

    main()
