import base64
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Insect, ImageHistory
from django.contrib.auth import get_user_model
from .views import predict_insect
from PIL import Image
import io

User = get_user_model()

@csrf_exempt
@login_required
def detect_insect_from_frame(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            frame_url = data.get('frame_url')
            # Tải ảnh từ frame_url
            resp = requests.get(frame_url)
            if resp.status_code != 200:
                return JsonResponse({'error': 'Không lấy được ảnh từ livefeed'}, status=400)
            image_bytes = resp.content
            pred, confidence = predict_insect(image_bytes, threshold=0.55)
            if pred is not None:
                insect = Insect.objects.filter(id=pred+1).first()
                if insect:
                    user = request.user
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
            # Nếu không nhận diện được hoặc độ tin cậy thấp
            return JsonResponse({'insect_name': '', 'scientific_name': '', 'id': None, 'confidence': round(confidence, 3) if confidence is not None else None})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)
