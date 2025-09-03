from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags


@shared_task
def send_welcome_email(user_email, full_name, department, position):
    subject = "Welcome to MySite!"
    current_year = timezone.now().year

    html_content = render_to_string(
        "emails/welcome_email.html",
        {
            "full_name": full_name,
            "position": position,
            "department": department,
            "current_year": current_year,
        },
    )

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject, text_content, "noreply@dev_asset_manager.com", [user_email]
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


@shared_task
def send_otp_email(email, otp):
    current_year = timezone.now().year
    subject = "Your Dev Assets Manager OTP (Valid for 10 minutes)"

    html_content = render_to_string(
        "emails/otp_email.html",
        {"email": email, "otp": otp, "current_year": current_year},
    )

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject, text_content, "noreply@dev_asset_manager.com", [email]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()


@shared_task
def send_change_password(email, current_password):
    current_year = timezone.now().year
    subject = "Secure Your Account: Dev Assets Manager Credentials Inside"

    html_content = render_to_string(
        "emails/send_change_password.html",
        {"email": email, "password": current_password, "current_year": current_year},
    )

    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject, text_content, "noreply@dev_asset_manager.com", [email]
    )

    email.attach_alternative(html_content, "text/html")
    email.send()
