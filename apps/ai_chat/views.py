from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .chat_service import get_ai_response
from .models import ChatLog
import json

@login_required
def chat_view(request):
    chats = ChatLog.objects.filter(user=request.user).order_by('-created_at')[:20]
    chats = reversed(list(chats))
    return render(request, 'ai_chat/chat.html', {'chats': chats})

@login_required
def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        if not message:
            return JsonResponse({'error': 'Empty message'}, status=400)

        result = get_ai_response(message)

        ChatLog.objects.create(
            user=request.user,
            message=message,
            response=result['response'],
            is_blocked=result['is_blocked']
        )

        return JsonResponse(result)
    return JsonResponse({'error': 'Invalid method'}, status=405)