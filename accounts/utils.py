import random
from django.core.mail import EmailMessage
from django.conf import settings
from twilio.rest import Client
from django.utils import timezone
from datetime import timedelta
from .models import PasswordResetOTP

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def generate_otp():
	return str(random.randint(100000 , 999999))


def send_email(subject , message , to_email):
	try:
		email = Mail(
			from_email=settings.DEFAULT_FROM_EMAIL ,
			to_emails=to_email ,
			subject=subject ,
			plain_text_content=message ,
		)
		
		sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
		sg.send(email)
	
	except Exception as e:
		raise Exception(f"SendGrid email failed: {str(e)}")


def send_sms(phone , message):
	phone = "+91" + phone
	account_sid = "ACf8cad3961219c5f8af7d385f7451b775"
	auth_token = "1a5e7e5b4e3a00e90cd2b8d42efe17b3"
	from_number = "+12543292685"
	
	client = Client(account_sid , auth_token)
	client.messages.create(
		body=message ,
		from_=from_number ,
		to=phone
	)
