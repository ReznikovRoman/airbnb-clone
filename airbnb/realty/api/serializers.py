from rest_framework import serializers

from django.shortcuts import get_object_or_404

from hosts.models import RealtyHost
from accounts.models import CustomUser, Profile
from addresses.models import Address
from ..models import Realty, Amenity


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'country', 'city', 'street']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'profile_image', 'date_of_birth', 'gender',
                  'phone_number', 'is_phone_number_confirmed', 'description']
        read_only_fields = ['id', 'profile_image', 'date_of_birth', 'gender',
                            'phone_number', 'is_phone_number_confirmed', 'description']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_email_confirmed', 'profile']
        read_only_fields = ['id', 'email', 'first_name', 'last_name', 'is_email_confirmed', 'profile']


class RealtyHostSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = RealtyHost
        fields = ['id', 'user', 'host_rating']
        read_only_fields = ['id', 'user', 'host_rating']


class RealtyAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Amenity
        fields = ['id', 'name']


class RealtySerializer(serializers.ModelSerializer):
    location = AddressSerializer()
    host = RealtyHostSerializer()
    amenities = RealtyAmenitySerializer(many=True)

    class Meta:
        model = Realty
        fields = ['id', 'name', 'description', 'is_available', 'created',
                  'realty_type', 'beds_count', 'max_guests_count', 'price_per_night',
                  'location', 'host', 'amenities']

    def create(self, validated_data: dict):
        location_data = validated_data.pop('location')
        amenities_data = validated_data.pop('amenities')
        validated_data.pop('host')

        new_location = Address.objects.create(**location_data)
        amenities = [Amenity.objects.get_or_create(**amenity_data)[0] for amenity_data in amenities_data]

        # TODO: set realty host properly (another issue - DRF authentication, authorization)
        realty_host_pk = validated_data.pop('host_pk')
        realty_host = get_object_or_404(RealtyHost, pk=realty_host_pk)

        new_realty = Realty(**validated_data)
        new_realty.location = new_location
        new_realty.host = realty_host
        new_realty.save()
        new_realty.amenities.add(*amenities)

        return new_realty


class RealtyUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Realty
        fields = ['name', 'description', 'is_available',
                  'realty_type', 'beds_count', 'max_guests_count', 'price_per_night']
