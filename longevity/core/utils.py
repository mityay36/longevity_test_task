from rest_framework.generics import get_object_or_404

from users.models import User


def send_otp(email):
    user = get_object_or_404(User, email=email)
    user.email_user(
        subject='confirmation_code',
        message=f'Your confirmation code is: {user.confirmation_code}',
        fail_silently=False
    )
