from .models import CustomUser, OTP
from .serializers import UserSerializer, RegisterSerializer, OTPSerializer
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework import status
from django.shortcuts import get_object_or_404
from .tasks import send_email, send_message
import random
import string
import json
from rest_framework_simplejwt.tokens import RefreshToken
from automate_mail.settings import SECRET_KEY
from django.utils import timezone


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def otp_email(user):
    email = user.email
    username = user.username
    otp = OTP.objects.create(user=user, code="".join(random.choices(string.ascii_uppercase + string.digits, k=5)),
                             type="EM")
    data = {"email": email, "email_subject": "Hello", "email_body": f"Hello {username}, <3. This is your code : "
                                                                    f"{otp.code}"}
    send_email.delay(data)


def otp_phone(user):
    phone = user.phone_number
    username = user.username
    otp = OTP.objects.create(user=user, code="".join(random.choices(string.ascii_uppercase + string.digits, k=6)),
                             type="PH")
    data = {"phone_number": phone, "body": f"Hello {username}, <3. This is your code : "
                                           f"{otp.code}"}
    send_message.delay(data)


class RegisterAPI(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        print(get_tokens_for_user(user))
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
        })


class SendOTP(GenericAPIView):
    serializer_class = OTPSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        type_of_verification = json.loads(request.body.decode('utf-8'))["type"]
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        data = {'token': token}
        try:
            valid_data = TokenBackend(algorithm='HS256', signing_key=SECRET_KEY).decode(str(token), verify=True)
            user_id = valid_data['user_id']
        except Exception as v:
            print("validation error", v)
        user = CustomUser.objects.get(pk=user_id)
        if user.email_is_verified and type_of_verification == "EM":
            return Response(data={"data": "Email already verified"})

        elif not user.email_is_verified and type_of_verification == "EM":
            otp_email(user)
            return Response(data={"data": "OTP sent to email"})

        if user.phone_is_verified and type_of_verification == "PH":
            return Response(data={"data": "Phone already verified"})

        elif not user.phone_is_verified and type_of_verification == "PH":
            otp_phone(user)
            return Response(data={"data": "OTP sent to phone"})
        return Response(data={"data": "done"})


class EmailVerificationAPI(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OTPSerializer

    def post(self, request):
        code = json.loads(request.body.decode('utf-8'))["code"]
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        data = {'token': token}
        try:
            valid_data = TokenBackend(algorithm='HS256', signing_key=SECRET_KEY).decode(str(token), verify=True)
            user_id = valid_data['user_id']
        except Exception as v:
            print("validation error", v)
        otp = get_object_or_404(OTP, user__pk=user_id, type="EM")
        user = CustomUser.objects.get(pk=user_id)
        if timezone.now() > otp.exp_time:
            return Response(data={"error": "code expired"}, status=status.HTTP_403_FORBIDDEN)
        if otp.code != code:
            otp_email(user)
            otp.delete()
            return Response(data={"error": "invalid"}, status=status.HTTP_403_FORBIDDEN)
        user.email_is_verified = True
        user.save()
        otp.delete()
        return Response(data={"data": "email verified"}, status=status.HTTP_202_ACCEPTED)


class PhoneVerificationAPI(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = OTPSerializer

    def post(self, request):
        code = json.loads(request.body.decode('utf-8'))["code"]
        token = request.META.get('HTTP_AUTHORIZATION', " ").split(' ')[1]
        data = {'token': token}
        print(data)
        try:
            valid_data = TokenBackend(algorithm='HS256', signing_key=SECRET_KEY).decode(str(token), verify=True)
            user_id = valid_data['user_id']
        except Exception as v:
            print("validation error", v)
        otp = get_object_or_404(OTP, user__pk=user_id, type="PH")
        user = CustomUser.objects.get(pk=user_id)
        if timezone.now() > otp.exp_time:
            return Response(data={"error": "code expired"}, status=status.HTTP_403_FORBIDDEN)
        if otp.code != code:
            return Response(data={"error": "invalid"}, status=status.HTTP_403_FORBIDDEN)
        user.phone_is_verified = True
        user.save()
        otp.delete()
        return Response(data={"data": "phone verified"}, status=status.HTTP_202_ACCEPTED)


class ListUser(ListAPIView):
    model = CustomUser
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
