from django.contrib.auth import authenticate
from django.core.mail import send_mail
from rest_framework import serializers

from .models import MyUser
from .utils import send_activation_code


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    password_confirm = serializers.CharField(min_length=6, write_only=True)

    class Meta:
        model = MyUser
        fields = ("email", "password", "password_confirm")

    def validate(self, validated_data):   #def validate = def clean; validated_data = cleaned_data
        password = validated_data.get("password")
        password_confirm = validated_data.get("password_confirm")
        if password != password_confirm:
            raise serializers.ValidationError("Password do not much")
        return validated_data

    def create(self, validated_data):
        """This function is called when self.save() method is called"""
        email = validated_data.get("email")
        password = validated_data.get("password")
        user = MyUser.objects.create_user(email=email, password=password)
        send_activation_code(email=user.email, activation_code=user.activation_code)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get("request"), email=email, password=password)
            if not user:
                message = "Unable to log in with provided credentials"
                raise serializers.ValidationError(message, code="authorization")
        else:
            message = "Must include 'email' and 'password'"
            raise serializers.ValidationError(message, code="authorization")

        attrs["user"] = user
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        if not MyUser.objects.filter(email=email).exists():
            raise serializers.ValidationError()
        return email

    def send_reset_email(self):
        email = self.validated_data.get("email")
        user = MyUser.objects.get(email=email)
        user.create_activation_code()
        message = f"Код для смены пароля {user.activation_code}"
        send_mail(
            "Смена пароля",
            message,
            "test@gmail.com",
            [email]
        )
        user.save()


class CreateNewPasswordSerializer(serializers.Serializer):
    activation_code = serializers.CharField(required=True)
    password = serializers.CharField(min_length=6, required=True)
    password_confirm = serializers.CharField(min_length=6, required=True)

    def validate_activation_code(self, code):
        if not MyUser.objects.filter(activation_code=code).exists():
            raise serializers.ValidationError("Неверный код активации")
        return code

    def validate(self, attrs):
        password = attrs.get("password")
        password_confirm = attrs.get("password_confirm")

        if password != password_confirm:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs

    def create_pass(self):
        code = self.validated_data.get("activation_code")
        password = self.validated_data.get("password")
        user = MyUser.objects.get(activation_code=code)
        user.set_password(password)
        user.activation_code = ""
        user.save()
