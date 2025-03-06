from django.contrib import admin
from .models import Email_report
from .models import UserProfile, ParentChildRelation, Note

# Register the UserProfile model
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role")
    search_fields = ("id", "user__username", "role")

# Register the ParentChildRelation model
@admin.register(ParentChildRelation)
class ParentChildRelationAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "child")
    search_fields = ("id", "parent__user__username", "child__user__username")

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "created_at")
    search_fields = ("id", "title", "author__username")

# Display the report to be sent by email notification to Parent User
admin.site.register(Email_report)
