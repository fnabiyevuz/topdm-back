from rest_framework import serializers

from apps.common.models import Country, Region, District, Neighborhood, Media


class CountryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            "id",
            "name",
        )


class RegionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = (
            "id",
            "name",
        )


class DistrictListSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = (
            "id",
            "name",
        )


class NeighborhoodListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Neighborhood
        fields = (
            "id",
            "name",
        )


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = '__all__'
        read_only_fields = ['file_type', 'file_name']
