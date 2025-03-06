from django.shortcuts import render
from difflib import SequenceMatcher
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Note, UserProfile, ParentChildRelation, ParentChildRequest, TherapistChildRequest, TherapistChildRelation
from .serializers import UserSerializer, NoteSerializer, ChildAccountSerializer, UserProfileSerializer, ParentChildRequestSerializer, AvatarUploadSerializer, CustomTokenObtainPairSerializer, CustomizedUsernameSerializer, TherapistChildRequestSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import viewsets
# from .serializers import CourseSerializer, LessonSerializer, ExerciseSerializer, MediaSerializer
from rest_framework.exceptions import PermissionDenied
from django.http import JsonResponse, StreamingHttpResponse
import json
import time
from django.middleware.csrf import get_token
import aiohttp
import whisper
import os
from django.conf import settings
<<<<<<< HEAD
=======
from pydub import AudioSegment
import asyncio
import tempfile
>>>>>>> 8c7561de3bbe52f887c9065f39ea052265c0fae5


# from dotenv import load_dotenv
# import os

# def configure():
#     load_dotenv()

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class SendParentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        child_user = request.user
<<<<<<< HEAD
        parent_email = request.data.get('parent_email')  # 使用邮箱而不是ID

        print(f"Received request to send parent request for child: {child_user.username}, parent_email: {parent_email}")

=======
        parent_email = request.data.get('parent_email')  # using email to identify parent

>>>>>>> 8c7561de3bbe52f887c9065f39ea052265c0fae5
        # 查找家长用户
        try:
            parent_user = User.objects.get(username=parent_email)
            user_profile = UserProfile.objects.get(user=parent_user)
            
            if user_profile.role != 'parent':
<<<<<<< HEAD
                print("Specified user is not a parent")
                return Response({"error": "指定的用户不是家长"}, status=status.HTTP_400_BAD_REQUEST)

            # 创建请求
            request_instance = ParentChildRequest.objects.create(child=child_user, parent=parent_user)
            print(f"Parent-Child request created with ID: {request_instance.id}")
            return Response({"message": "请求已发送", "request_id": request_instance.id}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            print(f"Parent user with email {parent_email} not found")
            return Response({"error": "找不到指定的家长用户"}, status=status.HTTP_404_NOT_FOUND)
=======
                return Response({"error": "Please use parent account to access to the report."}, status=status.HTTP_400_BAD_REQUEST)

            # 创建请求
            request_instance, created = ParentChildRequest.objects.get_or_create(
                child=child_user,
                parent=parent_user,
                defaults={'status': 'pending'}
            )

            if not created:
                if ParentChildRequest.objects.get(child=child_user, parent=parent_user).status == 'rejected':
                    ParentChildRequest.objects.filter(child=child_user, parent=parent_user).update(status='pending')
                else:
                    return Response({"message": "request existed"}, status=status.HTTP_200_OK)
            return Response({"message": "The request has been sent", "request_id": request_instance.id, "child_username": child_user.username}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "Cannot find this parent account"}, status=status.HTTP_404_NOT_FOUND)
>>>>>>> 8c7561de3bbe52f887c9065f39ea052265c0fae5

class ApproveParentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        try:
            parent_request = ParentChildRequest.objects.get(id=request_id, parent=request.user)

            if parent_request.status != 'pending':
                return Response({"error": "Your request has been modified."}, status=status.HTTP_400_BAD_REQUEST)

            parent_request.status = 'approved'
            parent_request.save()

            # 创建家长-孩子关系
            ParentChildRelation.objects.create(
                parent=parent_request.parent,
                child=parent_request.child,
                child_name=parent_request.child.username
            )
            return Response({"message": "Approved!"}, status=status.HTTP_200_OK)

        except ParentChildRequest.DoesNotExist:
            return Response({"error": "Cannot find or modify this request."}, status=status.HTTP_404_NOT_FOUND)

class RejectParentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        try:
            parent_request = ParentChildRequest.objects.get(id=request_id, parent=request.user)

            if parent_request.status != 'pending':
                return Response({"error": "request processed"}, status=status.HTTP_400_BAD_REQUEST)

            parent_request.status = 'rejected'
            parent_request.save()

            return Response({"message": "request rejected"}, status=status.HTTP_200_OK)

        except ParentChildRequest.DoesNotExist:
            return Response({"error": "no request found"}, status=status.HTTP_404_NOT_FOUND)


class NoteListCreate(generics.ListCreateAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_profile = UserProfile.objects.get(user=user)

        # 家长和语言学家可以查看学习报告
        if user_profile.role in ['parent', 'linguist']:
            return Note.objects.all()
        elif user_profile.role == 'child':
            raise PermissionDenied("Sorry, children cannot access to the report")
        return Note.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        user_profile = UserProfile.objects.get(user=user)

        # 只有语言学家可以创建或修改学习报告
        if user_profile.role in ['linguist']:
            if serializer.is_valid():
                serializer.save(author=user)
            else:
                print(serializer.errors)
        else:
            raise PermissionDenied("Only linguist can modify the report.")


class NoteDelete(generics.DestroyAPIView):
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_profile = UserProfile.objects.get(user=user)

        # 只有语言学家可以删除学习报告
        if user_profile.role in ['linguist']:
            return Note.objects.all()
        else:
            raise PermissionDenied("Only linguist can delete the report.")


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class CreateChildAccountView(CreateAPIView):
    serializer_class = ChildAccountSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}


class FetchChildAccountsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 获取登录用户
        parent_user = request.user
        # 获取这个家长所有的孩子账户
        children = ParentChildRelation.objects.filter(parent=parent_user)
        # 序列化数据
        child_data = [
            {
                "id": child.child.id,
                "username": child.child.username,
                "name": child.child_name
            }
            for child in children
        ]
        return Response({"children": child_data})
    

def api_index(request):
    """Simple view to serve as the index of the API, providing basic info."""
    return JsonResponse({
        "message": "Welcome to the API index.",
        "available_endpoints": {
            "/api/user/register/": "Register a new user",
            "/api/token/": "Obtain a JWT token",
            "/api/token/refresh/": "Refresh the JWT token",
            "/api/notes/": "List or create notes",
            "/api/notes/<int:pk>/": "Delete a specific note",
            "/api/create-child/": "Create a child account",
            "/api/children/": "Fetch child accounts",
        }
    })


class ListUsersView(APIView):
    permission_classes = [IsAuthenticated]  # 仅允许经过身份验证的用户访问

    def get(self, request):
        # 获取所有用户及其 UserProfile 信息
        users = User.objects.all()
        user_data = []

        for user in users:
            # 尝试获取 user 的 UserProfile
            try:
                user_profile = UserProfile.objects.get(user=user)
                role = user_profile.role
            except UserProfile.DoesNotExist:
                role = "No Role Assigned"

            user_data.append({
                "id": user.id,
                "username": user.username,
                "role": role
            })

        return Response(user_data)
    

class ListParentRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 获取登录用户
        parent_user = request.user

        # 确保当前用户是家长
        user_profile = UserProfile.objects.get(user=parent_user)
        if user_profile.role != 'parent':
            return Response({"error": "Only parent can deal with the request"}, status=403)

        # 获取所有发给该家长的待处理请求
        pending_requests = ParentChildRequest.objects.filter(parent=parent_user, status='pending')
        serializer = ParentChildRequestSerializer(pending_requests, many=True)
        
        return Response(serializer.data, status=200)
    

class AvatarUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            # 获取当前登录用户的 UserProfile
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "Cannot find this user profile"}, status=status.HTTP_404_NOT_FOUND)
        
        print("Request Data:", request.data)

        # 使用 AvatarUploadSerializer 来处理用户上传的头像
        serializer = AvatarUploadSerializer(instance=user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            # 保存上传的头像
            serializer.save()
            
            return Response({
                "message": "Succeed to upload the avatar.",
                "avatar_id": user_profile.avatar_id,
                "user_id": user_profile.user.id  # 返回用户ID来确认关联
            }, status=status.HTTP_200_OK)
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        try:
            # 获取当前登录用户的 UserProfile
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "用户配置文件未找到"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "avatar_id": user_profile.avatar_id,
            "user_id": user_profile.user.id  # 返回用户ID来确认关联
        }, status=status.HTTP_200_OK)

class customizeUsernameView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "用户配置文件未找到"}, status=status.HTTP_404_NOT_FOUND)
        
        print("Request Data:", request.data)

        serializer = CustomizedUsernameSerializer(instance=user_profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            
            return Response({
                "message": "username customized successfully",
                "username": user_profile.customized_username,
                "user_id": user_profile.user.id
            }, status=status.HTTP_200_OK)
        print("Serializer Errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "用户配置文件未找到"}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "username": user_profile.customized_username,
            "user_id": user_profile.user.id
        }, status=status.HTTP_200_OK)


import json
import os
import aiofiles
from datetime import datetime
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token

async def stream_generator(active, user_id):
    url = "http://127.0.0.1:8001/trigger/"
    headers = {"Accept": "text/event-stream"}
    params = {"turn": active}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            async for line in response.content:
                if line:
                    try:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data:'):
                            data = json.loads(decoded_line[5:].strip())
                            label = data["type"]
                            response_text = data["response"].replace(""", "").replace(""", "")
                            
                            # 使用异步任务处理文件保存
                            if "answer" in label:
                                await save_answer_to_file(response_text)
                            elif "report" in label.lower():
                                await save_report_to_file(response_text, user_id)
                            
                            print(f"type:{label}\nresponse:{response_text}\n")
                            yield response_text
                    except Exception as e:
                        print(f"Error processing stream data: {e}")
                        continue

async def save_answer_to_file(response_text):
    file_path = os.path.join(os.path.dirname(__file__), 'responses.txt')
    try:
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
            await file.write(response_text + '\n')
        print(f"dialogue has been saved to: {file_path}")
    except Exception as e:
        print(f"Error saving answer: {e}")

async def save_report_to_file(report_text, user_id):
    try:
        reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{user_id}_{timestamp}.txt"
        file_path = os.path.join(reports_dir, filename)
        
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
            await file.write(report_text)
        
        print(f"Report has been saved, userid: {user_id}, file path: {file_path}")
    except Exception as e:
        print(f"Error saving report: {e}")

@csrf_exempt
@require_http_methods(["POST"])
async def trigger_stream_view(request):
    try:
        data = json.loads(request.body)
        param = data.get('theme', '')
        user_id = data.get('user_id', '')
        print(f"frontend param: {param}, userid: {user_id}")
        
        if not user_id:
            raise ValueError("userid cannot be empty")
            
        print(f"frontend param: {param}, userid: {user_id}")

        async_generator = stream_generator(param, user_id)

        response = StreamingHttpResponse(
            event_stream(async_generator),
            content_type='text/event-stream'
        )
        
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'
        
        return response
        
    except Exception as e:
        return StreamingHttpResponse(
            f"data: {json.dumps({'error': str(e)})}\n\n",
            content_type='text/event-stream'
        )

async def event_stream(async_generator):
    try:
        async for result in async_generator:
            if result:
                yield f"data: {json.dumps({'result': result})}\n\n"
    except Exception as e:
        print(f"Stream error: {e}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

async def get_response_text(request):
    file_path = os.path.join(os.path.dirname(__file__), 'responses.txt')
    
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
            response_text = await file.read()
            response_text = response_text.strip()
            print(f"Response: {response_text}")
        async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
            await file.write('')
    except FileNotFoundError:
        response_text = "File not found."
    except Exception as e:
        response_text = f"Error reading file: {str(e)}"
    
    return JsonResponse({'response_text': response_text})

async def get_user_reports(request, user_id):
    print(f"User ID: {user_id}")
    if not user_id:
        return JsonResponse({'error': 'need to provide userid'}, status=400)
    
    reports_dir = os.path.join(os.path.dirname(__file__), 'reports')
    if not os.path.exists(reports_dir):
        return JsonResponse({'reports': []})
    
    user_reports = []
    for filename in os.listdir(reports_dir):
        if filename.startswith(f"{user_id}_"):
            file_path = os.path.join(reports_dir, filename)
            try:
                async with aiofiles.open(file_path, 'r', encoding='utf-8') as file:
                    content = await file.read()
                    user_reports.append({
                        'filename': filename,
                        'content': content,
                        'created_at': filename.split('_')[1].replace('.txt', '')
                    })
            except Exception as e:
                print(f"Error reading report {filename}: {e}")
                continue
    
    return JsonResponse({'reports': user_reports})

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})


class AudioTranscriptionView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = whisper.load_model("base")

    def post(self, request):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response(
                {"error": "No audio file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                for chunk in audio_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            try:
                result = self.model.transcribe(
                    tmp_file_path,
                    language="en",
                    task="transcribe",
                )
                transcribed_text = result["text"]

                return Response({
                    "user_id": request.user.id,
                    "transcribed_text": transcribed_text
                }, status=status.HTTP_200_OK)

            finally:
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    print(f"Temporary file deleted: {tmp_file_path}")
                else:
                    print(f"Temporary file not found: {tmp_file_path}")

        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            return Response(
                {"error": f"Error processing audio: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendTherapistRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        child_user = request.user
        therapist_email = request.data.get('therapist_email')  # using email to identify therapist

        try:
            therapist_user = User.objects.get(username=therapist_email)
            user_profile = UserProfile.objects.get(user=therapist_user)
            
            if user_profile.role != 'therapist':
                return Response({"error": "Please use therapist account to access to the report."}, status=status.HTTP_400_BAD_REQUEST)

            # Make request
            request_instance, created = TherapistChildRequest.objects.get_or_create(
                child=child_user,
                therapist=therapist_user,
                defaults={'status': 'pending'}
            )

<<<<<<< HEAD
class MediaViewSet(viewsets.ModelViewSet):
    '''
    It provides all CRUD functionality (list, retrieve, create, update, destroy) for `Media`
    model.
    
    Instead of creating separate classes for each action (like ListAPIView, CreateAPIView, etc.), 
    we can have one ModelViewSet that encapsulates all CRUD actions.
    '''
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    
    
class UserAudioUploadView(APIView):        # Custom view for uploading user audio
    '''
    This creates an API Endpoint for User-Generated Audio which handles the audio file upload 
    (or collected from the Frontend). This view will accept the audio file and link it to the 
    appropriate `Exercise` (Entity) instance as user-generated content.
    '''
    def post(self, request):
        audio_file = request.FILES.get('audio')
        if audio_file:
            upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, audio_file.name)
            with open(file_path, 'wb') as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)

            return Response({"message": "File uploaded successfully"}, status=status.HTTP_201_CREATED)
        return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
=======
            if not created:
                if TherapistChildRequest.objects.get(child=child_user, therapist=therapist_user).status == 'rejected':
                    TherapistChildRequest.objects.filter(child=child_user, therapist=therapist_user).update(status='pending')
                else:
                    return Response({"message": "request existed"}, status=status.HTTP_200_OK)
            return Response({"message": "The request has been sent", "request_id": request_instance.id, "child_username": child_user.username}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({"error": "Cannot find this therapist account"}, status=status.HTTP_404_NOT_FOUND)

class ApproveTherapistRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        try:
            therapist_request = TherapistChildRequest.objects.get(id=request_id, therapist=request.user)

            if therapist_request.status != 'pending':
                return Response({"error": "Your request has been modified."}, status=status.HTTP_400_BAD_REQUEST)

            therapist_request.status = 'approved'
            therapist_request.save()

            TherapistChildRelation.objects.create(
                therapist=therapist_request.therapist,
                child=therapist_request.child,
                child_name=therapist_request.child.username
            )
            return Response({"message": "Approved!"}, status=status.HTTP_200_OK)

        except TherapistChildRequest.DoesNotExist:
            return Response({"error": "Cannot find or modify this request."}, status=status.HTTP_404_NOT_FOUND)

class RejectTherapistRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        try:
            therapist_request = TherapistChildRequest.objects.get(id=request_id, therapist=request.user)

            if therapist_request.status != 'pending':
                return Response({"error": "request processed"}, status=status.HTTP_400_BAD_REQUEST)

            therapist_request.status = 'rejected'
            therapist_request.save()

            return Response({"message": "request rejected"}, status=status.HTTP_200_OK)

        except TherapistChildRequest.DoesNotExist:
            return Response({"error": "no request found"}, status=status.HTTP_404_NOT_FOUND)

class ListTherapistRequestsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        therapist_user = request.user
        user_profile = UserProfile.objects.get(user=therapist_user)
        if user_profile.role != 'therapist':
            return Response({"error": "Only therapist can deal with the request"}, status=403)

        pending_requests = TherapistChildRequest.objects.filter(therapist=therapist_user, status='pending')
        serializer = TherapistChildRequestSerializer(pending_requests, many=True)
        
        return Response(serializer.data, status=200)
>>>>>>> 8c7561de3bbe52f887c9065f39ea052265c0fae5
    
class FetchChildAccountsForTherapistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        therapist_user = request.user
        children = TherapistChildRelation.objects.filter(therapist=therapist_user)
        child_data = [
            {
                "id": child.child.id,
                "username": child.child.username,
                "name": child.child_name
            }
            for child in children
        ]
        return Response({"children": child_data})

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer    

class ChatbotAudioTranscriptionView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def post(self, request):
        audio_file = request.FILES.get('audio')
        theme = request.data.get('theme')
        id = request.user.id
        if not audio_file:
            return Response(
                {"error": "No audio file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        upload_dir = os.path.join(settings.BASE_DIR, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, audio_file.name)
        with open(file_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
        try:
            return Response({
                "user_id": request.user.id,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error processing audio: {str(e)}")
            return Response(
                {"error": f"Error processing audio: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )