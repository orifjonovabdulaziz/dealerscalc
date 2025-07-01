from django.core.management.base import BaseCommand
from telegram import Bot
from dashboard.excel_utils import generate_report_excel  # создадим
from django.conf import settings

class Command(BaseCommand):
    help = 'Send dashboard report to Telegram group'

    def handle(self, *args, **kwargs):
        bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        chat_id = settings.TELEGRAM_CHAT_ID

        file_path = generate_report_excel()

        with open(file_path, 'rb') as f:
            bot.send_document(chat_id=chat_id, document=f, filename='report.xlsx')

        self.stdout.write(self.style.SUCCESS('Отчёт успешно отправлен в Telegram'))
