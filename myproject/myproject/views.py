from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages

def custom_logout(request):
    """カスタムログアウトビュー"""
    logout(request)
    messages.success(request, 'ログアウトしました。再度ログインしてください。')
    return redirect('login')
