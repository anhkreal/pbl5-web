from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from .models import Insect, ImageHistory
import base64
from collections import defaultdict
from datetime import datetime
import torch
from torchvision import transforms
from PIL import Image
import io

User = get_user_model()

def load_model():
    model_path = 'app/static/app/model/resnext50_32x4d_P2_BestFinetuned.pth'
    model = torch.hub.load('pytorch/vision', 'resnext50_32x4d', pretrained=False)
    # Đặt số lớp đúng với checkpoint (50 lớp)
    model.fc = torch.nn.Linear(model.fc.in_features, 50)
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    return model

model = None

def predict_insect(image_bytes, threshold=0.5):
    global model
    if model is None:
        model = load_model()
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    input_tensor = preprocess(img).unsqueeze(0)
    with torch.no_grad():
        output = model(input_tensor)
        probs = torch.softmax(output, dim=1)
        conf, pred = torch.max(probs, 1)
        conf = conf.item()
        pred = pred.item()
    if conf < threshold:
        return None, conf
    return pred, conf

def home(request):
    result = False
    image_data = None
    insect = None
    debug_info = None
    not_found = False
    confidence = None
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        image_bytes = image_file.read()
        image_data = base64.b64encode(image_bytes).decode('utf-8')
        image_data = f'data:{image_file.content_type};base64,{image_data}'
        try:
            pred, confidence = predict_insect(image_bytes, threshold=0.55)
            debug_info = f"Model prediction (class index): {pred}\nConfidence: {confidence}\n"
            if pred is not None:
                insect = Insect.objects.filter(id=pred+1).first()
                debug_info += f"DB query with id={pred+1}: {'Found' if insect else 'Not found'}\n"
                if insect:
                    debug_info += f"Insect name: {insect.name}, scientific: {insect.scientific_name}"
                    result = True
                else:
                    not_found = True
                    result = True
            else:
                not_found = True
                result = True
        except Exception as e:
            result = False
            insect = None
            not_found = True
            debug_info = f"Error: {e}"
    return render(request, 'app/home.html', {
        'result': result,
        'image_data': image_data,
        'insect': insect,
        'not_found': not_found,
        'confidence': confidence,
        'debug_info': debug_info,
    })

def thu_vien_con_trung(request):
    insects = Insect.objects.all().order_by('name')
    search_query = request.GET.get('q', '').strip()
    if search_query:
        insects = insects.filter(name__icontains=search_query) | insects.filter(scientific_name__icontains=search_query)
    # Phân loại theo từ đầu trong tên tiếng Việt
    group_insects = {}
    for insect in insects:
        first_word = insect.name.split()[0] if insect.name else 'Khác'
        img = f"data:image/jpeg;base64,{base64.b64encode(insect.image).decode()}" if insect.image else ''
        if first_word not in group_insects:
            group_insects[first_word] = []
        group_insects[first_word].append({
            'id': insect.id,
            'name': insect.name,
            'scientific_name': insect.scientific_name,
            'image': img,
        })
    group_insects = dict(sorted(group_insects.items()))
    return render(request, 'app/thu_vien_con_trung.html', {
        'group_insects': group_insects,
        'search_query': search_query,
    })

def login_view(request):
    if request.method == 'POST':
        return redirect('home')
    return render(request, 'app/login.html')

def register_view(request):
    return render(request, 'app/register.html')

def logout_view(request):
    return render(request, 'app/base.html', {'message': 'Đăng xuất'})

def account_info(request):
    user = User.objects.first()
    username = user.username if user else 'admin'
    raspberry_ip = user.raspberry_ip if user and hasattr(user, 'raspberry_ip') else '192.168.1.100'
    success = False
    if request.method == 'POST':
        username = request.POST.get('username', username)
        raspberry_ip = request.POST.get('raspberry_ip', raspberry_ip)
        # password = request.POST.get('password')
        if user:
            user.username = username
            user.raspberry_ip = raspberry_ip
            user.save()
        success = True
    return render(request, 'app/account_info.html', {
        'username': username,
        'raspberry_ip': raspberry_ip,
        'success': success
    })

def livefeed(request):
    user = User.objects.first()
    raspberry_ip = user.raspberry_ip if user and hasattr(user, 'raspberry_ip') else '192.168.1.100'
    return render(request, 'app/livefeed.html', {'raspberry_ip': raspberry_ip})

def insect_detail(request, id):
    insect = get_object_or_404(Insect, pk=id)
    img = f"data:image/jpeg;base64,{base64.b64encode(insect.image).decode()}" if insect.image else ''
    return render(request, 'app/insect_detail.html', {
        'insect': {
            'id': insect.id,
            'name': insect.name,
            'scientific_name': insect.scientific_name,
            'description': insect.description,
            'habitat': insect.habitat,
            'host_plants': insect.host_plants,
            'treatment': insect.treatment,
            'active_season': insect.active_season,
            'image': img,
        }
    })

def api_detect_insect(request):
    # Giả lập trả về côn trùng đầu tiên
    insect = Insect.objects.first()
    return JsonResponse({
        'insect_name': insect.name if insect else '',
        'scientific_name': insect.scientific_name if insect else '',
        'id': insect.id if insect else 1
    })

def history(request):
    user = User.objects.first()
    search_date = request.GET.get('date', '')
    search_query = request.GET.get('q', '').strip().lower()
    histories = ImageHistory.objects.filter(user=user) if user else ImageHistory.objects.none()
    if search_date:
        histories = histories.filter(detected_at__date=search_date)
    if search_query:
        histories = histories.filter(
            insect__name__icontains=search_query
        ) | histories.filter(
            insect__scientific_name__icontains=search_query
        )
    grouped_history = defaultdict(list)
    for h in histories:
        day = h.detected_at.date()
        img = f"data:image/jpeg;base64,{base64.b64encode(h.image).decode()}" if h.image else ''
        grouped_history[day].append({
            'image': img,
            'vn_name': h.insect.name if h.insect else '',
            'scientific_name': h.insect.scientific_name if h.insect else '',
            'time': h.detected_at.strftime('%Y-%m-%d %H:%M'),
            'insect_id': h.insect.id if h.insect else 1
        })
    grouped_history = dict(sorted(grouped_history.items(), reverse=True))
    return render(request, 'app/history.html', {
        'grouped_history': grouped_history,
        'search_date': search_date,
        'search_query': request.GET.get('q', '')
    })
