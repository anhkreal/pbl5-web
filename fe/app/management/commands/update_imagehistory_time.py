import random
from datetime import datetime, timedelta, time
from django.core.management.base import BaseCommand
from app.models import ImageHistory

class Command(BaseCommand):
    help = 'Cập nhật lại ngày giờ cho các bản ghi ImageHistory trong 15 ngày gần đây, giờ từ 17:00 đến 23:59.'

    def handle(self, *args, **options):
        today = datetime.now().date()
        start_date = today - timedelta(days=14)
        histories = ImageHistory.objects.filter(detected_at__date__gte=start_date)
        count = 0
        for h in histories:
            # Sinh ngày ngẫu nhiên trong 15 ngày gần đây
            random_day = today - timedelta(days=random.randint(0, 14))
            # Sinh giờ ngẫu nhiên từ 17:00 đến 23:59
            random_hour = random.randint(17, 23)
            random_minute = random.randint(0, 59)
            new_dt = datetime.combine(random_day, time(random_hour, random_minute))
            h.detected_at = new_dt
            h.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Đã cập nhật {count} bản ghi ImageHistory với ngày giờ mới.'))
