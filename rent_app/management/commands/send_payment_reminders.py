from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from rent_app.models import PaymentSchedule
from rent_app.utils import send_sms

import locale
locale.setlocale(locale.LC_ALL, '')


def format_currency(value):
    try:
        return locale.format_string("%d", int(float(value)), grouping=True)
    except ValueError:
        return value


def format_date(date_str):
    try:
        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date.strftime('%d-%m-%Y %H:%M')
    except Exception as e:
        return date_str


class Command(BaseCommand):
    help = 'Send SMS reminders for payment schedules due today'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # To'lov kunlari bugun bo'lgan va hali to'lanmaganlar
        due_payments = PaymentSchedule.objects.filter(
            due_date__gte=today_start,
            due_date__lte=today_end,
            is_paid=False
        )

        for payment in due_payments:
            message = (f"Xurmatli {payment.rental.fullname}.\n"
                       f"Siz {format_currency(payment.amount)} so'm miqdoridagi to'lovingizni {format_date(payment.due_date)} gacha to'lanishi kerak.")
            send_sms(payment.rental.phone, message)
            self.stdout.write(self.style.SUCCESS(f"Sent reminder to {payment.rental.phone}"))
