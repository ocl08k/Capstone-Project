from django.contrib import admin
from django.urls import path, include
from api.views import CreateUserView, CreateChildAccountView, FetchChildAccountsView, SendParentRequestView, api_index, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import HttpResponse
from graphene_django.views import GraphQLView

# Define a view function that returns an HTML page containing a link
def api_index(request):
    return HttpResponse("""
        <h1>Welcome to the Backend API</h1>
        <ul>
            <li><a href="/admin/">Admin Panel</a></li>
            <li><a href="/api/user/register/">User Registration</a></li>
            <li><a href="/api/token/">Get Token</a></li>
            <li><a href="/api/token/refresh/">Refresh Token</a></li>
            <li><a href="/api/">API Root</a></li>
            <li><a href="/api-auth/login/">API Auth Login</a></li>
        </ul>
    """)

# Modify urlpatterns and add root path processing
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/user/register/", CreateUserView.as_view(), name="register"),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="get_token"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="refresh"),
    path("api-auth/", include("rest_framework.urls")),
    path("api/", include("api.urls")),
    # path('api/add-child/', CreateChildAccountView.as_view(), name='add-child-account'),
    # path("api/children/", FetchChildAccountsView.as_view(), name="fetch-children"),b vgbvf
    path("graphql/", GraphQLView.as_view(graphiql=True)),
    path("", api_index),  # View function that handles the root path
    path("parent/", SendParentRequestView.as_view(), name="parent_link"),
]