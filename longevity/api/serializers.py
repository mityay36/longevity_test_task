from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken

from core.tasks import send_otp_task
from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        '''if password is not None:
            user.set_password(password)'''
        send_otp_task.delay(user.email)
        return {
            'email': user.email,
        }


class TokenSerializer(serializers.ModelSerializer, TokenObtainPairSerializer):

    class Meta:
        model = User
        fields = ('confirmation_code', 'email')

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        confirm_code = None
        if 'request' in self.context:
            authenticate_kwargs['request'] = self.context['request']
            confirm_code = self.context['request'].data['confirmation_code']

        self.user = authenticate(**authenticate_kwargs)

        if self.user is None:
            raise NotFound(
                'User does not exist.'
            )

        if self.user.confirmation_code != confirm_code:
            raise serializers.ValidationError(
                'Invalid confirmation_code.'
            )

        access = AccessToken.for_user(self.user)

        return {
            'token': str(access)
        }


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name',
            'bio', 'role'
        )

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'bio': user.bio,
            'role': user.role,
        }
