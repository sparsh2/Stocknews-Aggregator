from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile, UserRole, UserRoleAssignment

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'preferences', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole model"""
    class Meta:
        model = UserRole
        fields = ['id', 'name', 'description', 'permissions', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class UserRoleAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for UserRoleAssignment model"""
    role = UserRoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True)
    created_by = serializers.EmailField(read_only=True)

    class Meta:
        model = UserRoleAssignment
        fields = ['id', 'role', 'role_id', 'created_at', 'created_by']
        read_only_fields = ['created_at', 'created_by']

    def create(self, validated_data):
        role_id = validated_data.pop('role_id')
        try:
            role = UserRole.objects.get(id=role_id)
        except UserRole.DoesNotExist:
            raise serializers.ValidationError({'role_id': 'Invalid role ID'})
        
        validated_data['role'] = role
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = UserProfileSerializer(required=False)
    roles = UserRoleSerializer(many=True, read_only=True)
    role_assignments = UserRoleAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_active', 'is_staff', 'created_at', 'updated_at',
            'profile', 'roles', 'role_assignments'
        ]
        read_only_fields = ['created_at', 'updated_at']

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password2',
            'first_name', 'last_name', 'profile'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()

        if profile_data:
            UserProfile.objects.create(user=user, **profile_data)
        else:
            UserProfile.objects.create(user=user)

        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating a user"""
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name',
            'is_active', 'is_staff', 'profile'
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance

class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

class TokenObtainPairSerializer(serializers.Serializer):
    """Serializer for JWT token obtain pair"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class TokenRefreshSerializer(serializers.Serializer):
    """Serializer for refreshing JWT token"""
    refresh = serializers.CharField() 