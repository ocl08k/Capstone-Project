from django.urls import path, include
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from . import views
from .views import FetchChildAccountsView, CreateUserView, NoteListCreate, NoteDelete, SendParentRequestView, ApproveParentRequestView, RejectParentRequestView, ListUsersView, ListParentRequestsView, AvatarUploadView, customizeUsernameView, trigger_stream_view, SendTherapistRequestView, ApproveTherapistRequestView, RejectTherapistRequestView, ListTherapistRequestsView, FetchChildAccountsForTherapistView, AudioTranscriptionView, ChatbotAudioTranscriptionView, get_csrf_token, get_response_text, get_user_reports

urlpatterns = [
    path('notes/', NoteListCreate.as_view(), name='note-list-create'),
    path('notes/<int:pk>/', NoteDelete.as_view(), name='note-delete'),
    # path('create-child/', CreateChildAccountView.as_view(), name='create-child'),
    # path("register/", CreateUserView.as_view(), name="register"),
    path("fetch-children/", FetchChildAccountsView.as_view(), name="fetch-children"),
    #path('upload-audio/', UploadAudioView.as_view(), name='upload-audio'),
    path('user/register/', CreateUserView.as_view(), name='register'),
    path('parent_request/send/', SendParentRequestView.as_view(), name='send_parent_request'),
    path('parent-request/approve/<int:request_id>/', ApproveParentRequestView.as_view(), name='approve_parent_request'),
    path('parent-request/reject/<int:request_id>/', RejectParentRequestView.as_view(), name='reject_parent_request'),
    path('users/', ListUsersView.as_view(), name='list_users'),
    path('parent-request/list/', ListParentRequestsView.as_view(), name='list_parent_requests'),
    path('therapist-request/send/', SendTherapistRequestView.as_view(), name='send_therapist_request'),
    path('therapist-request/approve/<int:request_id>/', ApproveTherapistRequestView.as_view(), name='approve_therapist_request'),
    path('therapist-request/reject/<int:request_id>/', RejectTherapistRequestView.as_view(), name='reject_therapist_request'),
    path('therapist-request/list/', ListTherapistRequestsView.as_view(), name='list_therapist_requests'),
    path("fetch-children-for-therapist/", FetchChildAccountsForTherapistView.as_view(), name="fetch-children"),
    
    path('user/avatar/upload/', AvatarUploadView.as_view(), name='avatar_upload'),
    path('user/customize-username/', customizeUsernameView.as_view(), name='customize_username'),
    path('trigger/', trigger_stream_view, name='trigger_view'),
<<<<<<< HEAD
    path("current_question/", views.CurrentQuestionView.as_view(), name="current_question"),
    path('', include(router.urls)),
    path('exercises/upload_audio/', UserAudioUploadView.as_view(), name='upload_audio'),  # Configure the URL for the audio upload endpoint in urls.py
=======
    path('transcribe-audio/', AudioTranscriptionView.as_view(), name='transcribe_audio'),
    path('chatbot-audio/', ChatbotAudioTranscriptionView.as_view(), name='chatbot_audio'),
    path('get-csrf-token/', get_csrf_token, name='get-csrf-token'),
    path('get-response-text/', get_response_text, name='get-response-text'),
    path('get-user-reports/<int:user_id>/', get_user_reports, name='get_user_reports'),
>>>>>>> 8c7561de3bbe52f887c9065f39ea052265c0fae5
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
