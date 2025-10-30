from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    Kullanıcı bilgileri için serializer
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'hedef_meslek', 'bolum', 'yas', 'cinsiyet', 'dogum_tarihi', 'created_at']
        read_only_fields = ['id', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    """
    Kullanıcı kayıt için serializer
    - Şifre eşleşme kontrolü
    - Sadece izin verilen (whitelist) field'lar User'a aktarılır
    - Gereksiz/gizli alanlar user oluşturulurken dışarıda tutulur
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        # Update: Sadece whitelisted fields
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'hedef_meslek', 'bolum', 'yas', 'cinsiyet', 'dogum_tarihi']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Şifreler eşleşmiyor.")
        return attrs
    
    def create(self, validated_data):
        # Field filtering için fazlalıkları ayıkla
        validated_data.pop('password_confirm', None)
        # Whitelisted fields only!
        allowed_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'hedef_meslek', 'bolum', 'yas', 'cinsiyet', 'dogum_tarihi']
        filtered_data = {k: v for k, v in validated_data.items() if k in allowed_fields}
        user = User.objects.create_user(**filtered_data)
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Kullanıcı profil güncelleme için serializer
    - Güncellenen alanların filtrelenmesi
    - Mass assignment açığı önlenir
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'hedef_meslek', 'bolum', 'yas', 'cinsiyet', 'dogum_tarihi']
    
    def update(self, instance, validated_data):
        # Sadece meta'daki alanları güncelle (güvenlik)
        for attr in self.Meta.fields:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    """
    Şifre değiştirme için serializer
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Yeni şifreler eşleşmiyor.")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mevcut şifre yanlış.")
        return value 