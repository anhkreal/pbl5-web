import os
from django.core.management.base import BaseCommand
from app.models import Insect

class Command(BaseCommand):
    help = 'Cập nhật hình ảnh cho 50 loài côn trùng từ thư mục selected_images/'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # Sửa lại đường dẫn images_dir cho đúng với cấu trúc workspace
        images_dir = os.path.join(base_dir, '..', 'selected_images')
        images_dir = os.path.abspath(images_dir)
        updated = 0
        for i in range(50):
            insect_id = i + 1
            filename = f'{i}_'
            # Tìm file bắt đầu bằng i_
            files = [f for f in os.listdir(images_dir) if f.startswith(filename)]
            if not files:
                self.stdout.write(self.style.WARNING(f'Không tìm thấy ảnh cho loài id {insect_id}'))
                continue
            file_path = os.path.join(images_dir, files[0])
            try:
                with open(file_path, 'rb') as img_file:
                    image_bytes = img_file.read()
                insect = Insect.objects.filter(id=insect_id).first()
                if insect:
                    insect.image = image_bytes
                    insect.save()
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f'Đã cập nhật ảnh cho loài id {insect_id}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Không tìm thấy loài id {insect_id} trong DB'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Lỗi với loài id {insect_id}: {e}'))
        self.stdout.write(self.style.SUCCESS(f'Đã cập nhật {updated}/50 loài.'))
