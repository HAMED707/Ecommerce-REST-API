from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Users
from accounts.services import create_user_account, authenticated


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"
    
    def validate_phone_number(self, value):
        """Validate phone number has country code"""
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must include country code (e.g., +1234567890)"
            )
        if value and len(value) < 10:
            raise serializers.ValidationError(
                "Phone number is too short"
            )
        return value


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['username', 'email', 'first_name',
                  'last_name', 'password', 'phone_number',
                  'gender', 'date_of_birth', 'profile_picture']
    
    def validate_phone_number(self, value):
        """Validate phone number has country code"""
        # make sure phone starts with +
        if value and not value.startswith('+'):
            raise serializers.ValidationError(
                "Phone number must include country code (e.g., +1234567890)"
            )
        if value and len(value) < 10:
            raise serializers.ValidationError(
                "Phone number is too short"
            )
        return value
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = create_user_account(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)  # dont return password

    def validate(self, data):
        # TODO: add email login option
        user = authenticated(username=data['username'], password=data['password'])

        if not user:
            raise serializers.ValidationError("Invalid credentials")
        
        return {"user": user}


class TokenSerializer(serializers.Serializer):
    """Serializer for JWT tokens"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()

