from rest_framework import serializers

class ProductSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    domain_id = serializers.CharField()
    status = serializers.CharField()
    attributes = serializers.ListField(child=serializers.DictField())
    pictures = serializers.ListField(child=serializers.DictField())
    main_features = serializers.ListField(child=serializers.CharField())
    
    # Campos calculados
    thumbnail = serializers.SerializerMethodField()
    brand = serializers.SerializerMethodField()
    color = serializers.SerializerMethodField()

    def get_thumbnail(self, obj):
        return obj["pictures"][0]["url"] if obj.get("pictures") else None

    def get_brand(self, obj):
        for attr in obj["attributes"]:
            if attr.get("id") == "BRAND":
                return attr.get("value_name")
        return None

    def get_color(self, obj):
        for attr in obj["attributes"]:
            if attr.get("id") == "COLOR":
                return attr.get("value_name")
        return None