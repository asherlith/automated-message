from celery import shared_task
from django.core.mail import EmailMessage, send_mass_mail
from .models import CustomUser
from automate_mail.settings import EMAIL_HOST_USER, PHONE_HOST_USER
from sms import send_sms


@shared_task()
def send_email(data):
    email = EmailMessage(subject=data["email_subject"], body=data["email_body"], to=[data["email"]])
    email.send()


@shared_task()
def send_many_email(data):
    email_subject = data["email_subject"]
    email_body = data["email_body"]
    email = (email_subject, email_body, EMAIL_HOST_USER,
             list(CustomUser.objects.filter(email_is_verified=True).values_list('email', flat=True)))
    send_mass_mail((email,), fail_silently=False)


@shared_task()
def send_message(data):
    send_sms(data["body"], PHONE_HOST_USER, data["phone_number"])


@shared_task()
def send_many_message(data):
    send_sms(data["body"], PHONE_HOST_USER,
             list(CustomUser.objects.filter(phone_is_verified=True).values_list('phone_number', flat=True)))
