from celery import shared_task

from .utils import send_otp


@shared_task
def send_otp_task(email):
    return send_otp(email)
