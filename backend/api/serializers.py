from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Note, UserProfile, ParentChildRelation, ParentChildRequest, TherapistChildRequest, TherapistChildRelation
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserProfileSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'role', 'avatar_url', 'date_of_birth']
    
    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            avatar_url = obj.avatar.url
            return request.build_absolute_uri(avatar_url) if request else avatar_url
        return None

class UserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True}
        }

    def create(self, validated_data):
        role = validated_data.pop('role')
        email = validated_data.pop('email')
        user = User.objects.create_user(**validated_data, email=email)
        user_profile, created = UserProfile.objects.get_or_create(user=user, defaults={'role': role})
        user_profile.role = role
        user_profile.save()
        return user

class AvatarUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['avatar_id']
    
    def update(self, instance, validated_data):
        fileNameWithoutExtension = validated_data.pop('avatar_id', None)
        if fileNameWithoutExtension:
            instance.avatar_id = fileNameWithoutExtension
        instance.save()
        return instance
    
class CustomizedUsernameSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['customized_username']
    
    def update(self, instance, validated_data):
        usernane = validated_data.get('customized_username', None)
        if usernane:
            instance.customized_username = usernane
        instance.save()
        return instance

# serializers.py
class ChildAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentChildRelation
        fields = ['child_name', 'child_icon']

    def create(self, validated_data):
        parent = self.context['request'].user
        child_user = User.objects.create(username=validated_data['child_name'], password='default_password')
        child_user.set_password('default_password')
        child_user.save()
        
        UserProfile.objects.create(user=child_user, role='CHILD')
        
        parent_child_relation = ParentChildRelation.objects.create(
            parent=parent,
            child=child_user,
            child_name=validated_data['child_name'],
            child_icon=validated_data.get('child_icon')
        )
        
        return parent_child_relation


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ["id", "title", "content", "created_at", "author"]
        extra_kwargs = {"author": {"read_only": True}}


class ParentChildRequestSerializer(serializers.ModelSerializer):
    child_username = serializers.SerializerMethodField()

    class Meta:
        model = ParentChildRequest
        fields = '__all__'
    def get_child_username(self, obj):
        return obj.child.username
    
class TherapistChildRequestSerializer(serializers.ModelSerializer):
    child_username = serializers.SerializerMethodField()

    class Meta:
        model = TherapistChildRequest
        fields = '__all__'
    def get_child_username(self, obj):
        return obj.child.username


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        user_profile = UserProfile.objects.get(user=user)
        token['role'] = user_profile.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add additional response data
        user_profile = UserProfile.objects.get(user=self.user)
        data['role'] = user_profile.role

        return data