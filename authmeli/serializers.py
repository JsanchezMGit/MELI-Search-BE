from rest_framework import serializers

class ProductSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    price = serializers.FloatField()
    thumbnail = serializers.URLField()