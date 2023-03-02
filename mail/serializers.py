from .models import CustomUser, OTP
from rest_framework import serializers
from rest_framework.validators import UniqueValidator


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["username", "password", "email", "email_is_verified", "phone_is_verified", "phone_number"]


class OTPSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = OTP
        fields = "__all__"

    def get_type(self):
        type = self.context.get("type")
        return type


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', "phone_number")
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if CustomUser.objects.filter(email=data["email"]):
            raise serializers.ValidationError({"email": "already used"})
        if CustomUser.objects.filter(phone_number=data["phone_number"]):
            raise serializers.ValidationError({"phone_number": "already used"})
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(validated_data['username'], validated_data['email'],
                                              validated_data['password'], phone_number=validated_data['phone_number'])
        return user
