import os
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from app.models import Insect, ImageHistory, User

class Command(BaseCommand):
    help = 'Sinh dữ liệu mẫu cho ImageHistory trong 15 ngày gần đây.'

    def handle(self, *args, **options):
        # Lấy user đầu tiên (hoặc tạo nếu chưa có)
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('Không tìm thấy user nào trong hệ thống!'))
            return
        insects = list(Insect.objects.all())
        if not insects:
            self.stdout.write(self.style.ERROR('Không có dữ liệu côn trùng!'))
            return
        today = datetime.now().date()
        count = 0
        for day_offset in range(15):
            date = today - timedelta(days=day_offset)
            # Sinh ngẫu nhiên 2-5 lịch sử mỗi ngày
            for _ in range(random.randint(2, 5)):
                insect = random.choice(insects)
                # Lấy ảnh mẫu từ insect
                image_blob = insect.image
                if not image_blob:
                    continue
                detected_at = datetime.combine(date, datetime.min.time()) + timedelta(hours=random.randint(7, 20), minutes=random.randint(0, 59))
                ImageHistory.objects.create(
                    user=user,
                    insect=insect,
                    image=image_blob,
                    detected_at=detected_at
                )
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Đã tạo {count} bản ghi ImageHistory cho 15 ngày gần đây.'))
