from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        raspberry_ip = request.POST.get('raspberry_ip')
        
        if not username or not password or not confirm_password:
            messages.error(request, 'Vui lòng nhập đầy đủ thông tin.')
            return render(request, 'app/register.html')
        if password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp.')
            return render(request, 'app/register.html')
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Tên đăng nhập đã tồn tại.')
            return render(request, 'app/register.html')
        user = User.objects.create(
            username=username,
            password=make_password(password),
            raspberry_ip=raspberry_ip
        )
        messages.success(request, 'Đăng ký thành công! Hãy đăng nhập.')
        return redirect('login')
    return render(request, 'app/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng.')
    return render(request, 'app/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Đăng xuất thành công!')
    return redirect('login')

@login_required
def account_info(request):
    user = request.user
    if request.method == 'POST':
        raspberry_ip = request.POST.get('raspberry_ip')
        password = request.POST.get('password')
        changed = False
        # Không cho đổi tên tài khoản
        # Đổi IP Raspberry Pi
        if raspberry_ip is not None and raspberry_ip != user.raspberry_ip:
            user.raspberry_ip = raspberry_ip
            changed = True
        # Đổi mật khẩu nếu nhập
        if password:
            user.password = make_password(password)
            changed = True
        if changed:
            user.save()
            messages.success(request, 'Cập nhật thông tin thành công!')
        elif not messages.get_messages(request):
            messages.info(request, 'Không có thay đổi nào được thực hiện.')
    return render(request, 'app/account_info.html', {'user': user})
