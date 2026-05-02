from rest_framework import serializers
from django.contrib.auth.models import User

from meals.models import MenuItem
from orders.models import Order, OrderItem
from reviews.models import Review
from homecook.models import HomeCook



class RegisterSerializer(serializers.ModelSerializer):
    phone   = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model  = User
        fields = ["first_name", "last_name", "email", "password", "phone", "address"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        from users.models import UserProfile

        phone   = validated_data.pop("phone",   "")
        address = validated_data.pop("address", "")
        email   = validated_data["email"]

        user = User.objects.create_user(
            username   = email,
            email      = email,
            password   = validated_data["password"],
            first_name = validated_data.get("first_name", ""),
            last_name  = validated_data.get("last_name",  ""),
        )

        profile, _ = UserProfile.objects.get_or_create(user=user)
        if phone:
            profile.phone = phone
        if address:
            profile.address = address
        profile.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["id", "username", "first_name", "last_name", "email"]



class MenuItemSerializer(serializers.ModelSerializer):
    display_image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = MenuItem
        fields = [
            "id", "name", "price", "description",
            "cuisine", "image", "image_url", "display_image_url",
        ]
        extra_kwargs = {
            "image":     {"required": False, "allow_null": True},
            "image_url": {"required": False, "allow_blank": True},
        }

    def get_display_image_url(self, obj):
        request = self.context.get("request")
        if obj.image:
            url = obj.image.url
            return request.build_absolute_uri(url) if request else url
        return obj.image_url or "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?ixlib=rb-4.0.3"


class OrderItemSerializer(serializers.ModelSerializer):
    name  = serializers.CharField(source="menu_item.name",  read_only=True)
    price = serializers.DecimalField(source="menu_item.price",
                                     max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model  = OrderItem
        fields = ["id", "name", "quantity", "price", "status"]


class OrderSerializer(serializers.ModelSerializer):
    items         = OrderItemSerializer(many=True, read_only=True)
    human_status  = serializers.CharField(source="human_readable_status", read_only=True)

    class Meta:
        model  = Order
        fields = [
            "id", "client_name", "status", "human_status",
            "subtotal", "created_at", "items",
        ]
        read_only_fields = ["id", "status", "subtotal", "created_at"]



class ReviewSerializer(serializers.ModelSerializer):
    """
    Read  : public — anyone can GET reviews.
    Write : authenticated only — first_name / last_name / email are
            auto-populated from the logged-in user (see views.py).
    """
    class Meta:
        model  = Review
        fields = ["id", "first_name", "last_name", "rating", "message", "created_at"]
        read_only_fields = ["id", "first_name", "last_name", "created_at"]

    def validate_rating(self, value):
        if not (1 <= int(value) <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_message(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters.")
        return value.strip()


class HomeCookSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model  = HomeCook
        fields = [
            "id", "name", "surname", "cuisine", "bio",
            "address", "phone", "latitude", "longitude",
            "profile_picture_url",
        ]

    def get_profile_picture_url(self, obj):
        request = self.context.get("request")
        if obj.profile_picture:
            url = obj.profile_picture.url
            return request.build_absolute_uri(url) if request else url
        return None