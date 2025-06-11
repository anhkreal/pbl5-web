# Hệ thống nhận diện côn trùng sử dụng Django

## Mô tả dự án
Hệ thống web nhận diện côn trùng sử dụng Django, MySQL (XAMPP), lưu ảnh dạng blob, nhận diện qua ảnh upload hoặc livefeed, quản lý tài khoản, lịch sử nhận diện, thư viện côn trùng, giao diện hiện đại với Tailwind CSS.

## Tính năng chính
- Đăng ký, đăng nhập, đăng xuất, quản lý tài khoản (có trường raspberry_ip)
- Nhận diện côn trùng qua ảnh upload hoặc livefeed (từ Raspberry Pi)
- Lưu lịch sử nhận diện (ảnh, user, côn trùng, thời gian)
- Thư viện côn trùng, phân nhóm theo từ đầu tên tiếng Việt, tìm kiếm
- Hiển thị lịch sử nhận diện, lọc theo ngày, tìm kiếm
- Phân quyền: chỉ user đăng nhập mới xem được lịch sử, livefeed
- Lưu ảnh dạng blob trong MySQL
- Nhận diện sử dụng model AI PyTorch (.pth), có ngưỡng độ tin cậy

## Tính năng chi tiết

### 1. Đăng ký, đăng nhập, đăng xuất, quản lý tài khoản
- Đăng ký tài khoản mới với tên đăng nhập, mật khẩu, địa chỉ IP Raspberry Pi.
- Đăng nhập, đăng xuất, bảo vệ các trang cần đăng nhập.
- Xem và cập nhật thông tin tài khoản (đổi mật khẩu, đổi IP Raspberry Pi).
- Phân quyền: chỉ user đăng nhập mới truy cập được livefeed, lịch sử.

### 2. Nhận diện côn trùng qua ảnh upload
- Trang chủ cho phép chọn và upload ảnh bất kỳ.
- Ảnh được gửi lên backend, sử dụng model AI (PyTorch) để nhận diện.
- Nếu nhận diện thành công (độ tin cậy > 0.55), hiển thị tên tiếng Việt, tên khoa học, độ tin cậy, và link xem chi tiết loài côn trùng.
- Nếu không nhận diện được hoặc độ tin cậy thấp, hiển thị thông báo rõ ràng.
- Ảnh upload và kết quả nhận diện được lưu vào lịch sử cho user đang đăng nhập.

### 3. Nhận diện côn trùng qua livefeed
- Trang livefeed lấy ảnh từ camera Raspberry Pi (stream qua HTTP).
- Mỗi 5 giây tự động cắt 1 frame, gửi về backend để nhận diện.
- Kết quả nhận diện (nếu có) sẽ hiển thị tên, tên khoa học, độ tin cậy, link chi tiết.
- Nếu nhận diện thành công, ảnh frame và kết quả được lưu vào lịch sử user.
- Nếu không nhận diện được, hiển thị "Không xác định" và không lưu lịch sử.

### 4. Lịch sử nhận diện
- Hiển thị toàn bộ lịch sử nhận diện của user (ảnh, tên, tên khoa học, thời gian).
- Có thể lọc theo ngày, tìm kiếm theo tên hoặc tên khoa học.
- Ảnh hiển thị là ảnh thực tế đã nhận diện (từ upload hoặc livefeed).
- Chỉ user đăng nhập mới xem được lịch sử của mình.

### 5. Thư viện côn trùng
- Hiển thị danh sách tất cả các loài côn trùng trong hệ thống.
- Phân nhóm theo từ đầu tiên trong tên tiếng Việt (ví dụ: "Bọ", "Bướm", "Ong"...)
- Tìm kiếm theo tên tiếng Việt hoặc tên khoa học.
- Xem chi tiết từng loài: mô tả, hình ảnh, mùa hoạt động, cây ký chủ, biện pháp xử lý...

### 6. Công nghệ & bảo mật
- Sử dụng Django ORM, custom user model, lưu ảnh dạng blob (BinaryField).
- Kết nối MySQL (XAMPP) hoặc sqlite3.
- Giao diện hiện đại, responsive với Tailwind CSS, Heroicons.
- Bảo vệ CSRF, xác thực session, phân quyền truy cập.
- Có thể mở rộng thêm API, tích hợp AI nâng cao, hoặc các tính năng quản trị.

## Cấu trúc thư mục
```
fe/
  manage.py
  db.sqlite3 (hoặc cấu hình MySQL)
  app/
    models.py         # Định nghĩa User, Insect, ImageHistory
    views.py          # View chính (home, thư viện, lịch sử...)
    view_account.py   # Đăng ký, đăng nhập, tài khoản
    view_detection.py # Nhận diện từ livefeed/API
    templates/app/    # Giao diện các trang
    static/app/       # Static files, model .pth
  fe/
    settings.py, urls.py
```

## Cài đặt & chạy
1. Cài Python 3.10+, pip, Django, mysqlclient/pymysql, torch, torchvision, pillow
2. Cấu hình CSDL trong `settings.py` (MySQL hoặc sqlite3)
3. Chạy migrate:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Chạy server:
   ```
   python manage.py runserver
   ```
5. Truy cập http://localhost:8000

## Nhận diện AI
- Model: `static/app/model/resnext50_32x4d_P2_BestFinetuned.pth` (PyTorch, 50 lớp)
- Độ tin cậy: chỉ nhận nếu confidence > 0.55
- Nhận diện qua ảnh upload hoặc livefeed, lưu lịch sử nếu có kết quả

## Ghi chú
- Ảnh côn trùng và lịch sử đều lưu dạng blob (BinaryField)
- Đã phân quyền, bảo vệ các view cần đăng nhập
- Giao diện responsive, hiện đại, sử dụng Tailwind CSS, Heroicons
- Có thể mở rộng thêm API, phân quyền, hoặc tích hợp AI nâng cao

