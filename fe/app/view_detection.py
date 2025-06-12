import base64
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from .models import Insect, ImageHistory
from django.contrib.auth import get_user_model
from .views import predict_insect
import json
import threading
import queue
import uuid

User = get_user_model()

# Hàng đợi nhận diện và thread worker
ai_queue = queue.Queue(maxsize=3)

# Kết quả nhận diện tạm thời lưu theo session key
ai_results = {}

def ai_worker():
    while True:
        key, image_bytes = ai_queue.get()
        print(f'[BE DEBUG] Worker bắt đầu nhận diện: session_key={key}, queue_size={ai_queue.qsize()}')
        worker_start = timezone.now()
        try:
            pred, confidence = predict_insect(image_bytes, threshold=0.55)
            print(f'[BE DEBUG] Worker xong: session_key={key}, pred={pred}, confidence={confidence}, thời gian={(timezone.now()-worker_start).total_seconds()}s')
            ai_results[key] = (pred, confidence)
        except Exception as e:
            print(f'[BE DEBUG] Worker lỗi: session_key={key}, error={e}')
            ai_results[key] = (None, None)
        ai_queue.task_done()

threading.Thread(target=ai_worker, daemon=True).start()

@csrf_exempt
def detect_insect_from_frame(request):
    # Bỏ login_required để không redirect khi gọi từ JS, kiểm tra user thủ công
    if request.method == 'POST':
        if not request.user.is_authenticated:
            print('[BE DEBUG] Chưa đăng nhập khi gọi nhận diện!')
            return JsonResponse({'error': 'Chưa đăng nhập'}, status=401)
        try:
            data = json.loads(request.body)
            frame_url = data.get('frame_url')
            print(f'[BE DEBUG] Nhận request nhận diện từ user={request.user.username}, frame_url={frame_url}')
            # Tải ảnh từ frame_url
            resp = requests.get(frame_url)
            print(f'[BE DEBUG] requests.get status={resp.status_code}, content-type={resp.headers.get("content-type")}, content head={resp.content[:32]}')
            if resp.status_code != 200:
                print('[BE DEBUG] Không lấy được ảnh từ livefeed')
                return JsonResponse({'error': 'Không lấy được ảnh từ livefeed'}, status=400)
            try:
                image_bytes = resp.content
                print(f'[BE DEBUG] Đã tải ảnh từ livefeed, size={len(image_bytes)} bytes')
            except Exception as e:
                print(f'[BE DEBUG] Lỗi khi đọc ảnh từ livefeed: {e}')
                return JsonResponse({'error': 'Lỗi khi đọc ảnh từ livefeed'}, status=400)
            # Sử dụng queue để tránh block BE
            session_key = str(uuid.uuid4())
            start_time = timezone.now()
            print(f'[BE DEBUG] Nhận diện: session_key={session_key}, user={request.user.username}, start={start_time}')
            try:
                ai_queue.put_nowait((session_key, image_bytes))
                print(f'[BE DEBUG] Put vào queue: session_key={session_key}, queue_size={ai_queue.qsize()}')
            except queue.Full:
                print('[BE DEBUG] AI queue full, reject request')
                return JsonResponse({'error': 'Hệ thống đang bận, vui lòng thử lại sau!'}, status=429)
            # Đợi kết quả tối đa 10 giây
            for _ in range(90):
                if session_key in ai_results:
                    pred, confidence = ai_results.pop(session_key)
                    break
                import time; time.sleep(0.1)
            else:
                print('[BE DEBUG] AI nhận diện quá lâu, trả về timeout')
                return JsonResponse({'error': 'Nhận diện quá lâu, vui lòng thử lại!'}, status=504)
            end_time = timezone.now()
            print(f'[BE DEBUG] Trả kết quả về FE: session_key={session_key}, pred={pred}, confidence={confidence}, tổng thời gian={(end_time-start_time).total_seconds()}s')
            if pred is not None:
                insect = Insect.objects.filter(id=pred+1).first()
                if insect:
                    user = request.user
                    print(f'[BE DEBUG] User {user.username} nhận diện: {insect.name} (id={insect.id}), độ tin cậy={confidence}')
                    ImageHistory.objects.create(
                        user=user,
                        insect=insect,
                        image=image_bytes,
                        detected_at=timezone.now()
                    )
                    return JsonResponse({
                        'insect_name': insect.name,
                        'scientific_name': insect.scientific_name,
                        'id': insect.id,
                        'confidence': round(confidence, 3)
                    })
            print('[BE DEBUG] Không nhận diện được côn trùng hoặc độ tin cậy thấp')
            return JsonResponse({'insect_name': '', 'scientific_name': '', 'id': None, 'confidence': round(confidence, 3) if confidence is not None else None})
        except Exception as e:
            print(f'[BE DEBUG] Lỗi nhận diện: {e}')
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)
