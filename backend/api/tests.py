from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from .models import UserProfile, Note, ParentChildRelation
from rest_framework_simplejwt.tokens import AccessToken

class NoteViewTests(APITestCase):

    def setUp(self):
        # Create users
        self.parent_user = User.objects.create_user(username='parent', password='password')
        self.parent_profile = UserProfile.objects.create(user=self.parent_user, role='parent')
        self.parent_token = str(AccessToken.for_user(self.parent_user))

        self.child_user = User.objects.create_user(username='child', password='password')
        self.child_profile = UserProfile.objects.create(user=self.child_user, role='child')
        self.child_token = str(AccessToken.for_user(self.child_user))

        self.teacher_user = User.objects.create_user(username='teacher', password='password')
        self.teacher_profile = UserProfile.objects.create(user=self.teacher_user, role='teacher')
        self.teacher_token = str(AccessToken.for_user(self.teacher_user))

        self.linguist_user = User.objects.create_user(username='linguist', password='password')
        self.linguist_profile = UserProfile.objects.create(user=self.linguist_user, role='linguist')
        self.linguist_token = str(AccessToken.for_user(self.linguist_user))

        # Create reports for testing
        self.note = Note.objects.create(title="Test Note", content="Test Content", author=self.teacher_user)

    def authenticate(self, token):
        """Helper function to add JWT authentication header"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_parent_can_view_notes(self):
        self.authenticate(self.parent_token)
        response = self.client.get(reverse('note-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_child_cannot_view_notes(self):
        self.authenticate(self.child_token)
        response = self.client.get(reverse('note-list-create'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_create_note(self):
        self.authenticate(self.teacher_token)
        data = {'title': 'New Note', 'content': 'New Content'}
        response = self.client.post(reverse('note-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_parent_cannot_create_note(self):
        self.authenticate(self.parent_token)
        data = {'title': 'New Note', 'content': 'New Content'}
        response = self.client.post(reverse('note-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_delete_note(self):
        self.authenticate(self.teacher_token)
        response = self.client.delete(reverse('note-delete', args=[self.note.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_child_cannot_delete_note(self):
        self.authenticate(self.child_token)
        response = self.client.delete(reverse('note-delete', args=[self.note.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class CreateChildAccountTests(APITestCase):

    def setUp(self):
        # Creating Parent Accounts and JWT Tokens
        self.parent_user = User.objects.create_user(username='parent', password='password')
        self.parent_profile = UserProfile.objects.create(user=self.parent_user, role='parent')
        self.parent_token = str(AccessToken.for_user(self.parent_user))

        # Create other role accounts
        self.child_user = User.objects.create_user(username='child', password='password')
        self.child_profile = UserProfile.objects.create(user=self.child_user, role='child')
        self.child_token = str(AccessToken.for_user(self.child_user))

        self.teacher_user = User.objects.create_user(username='teacher', password='password')
        self.teacher_profile = UserProfile.objects.create(user=self.teacher_user, role='teacher')
        self.teacher_token = str(AccessToken.for_user(self.teacher_user))

        # Define the URL to create the child account
        self.create_child_url = reverse('create-child')

    def authenticate(self, token):
        """Helper function to add JWT authentication header"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def test_parent_can_create_child_account(self):
        # Create a child account using a parent account
        self.authenticate(self.parent_token)
        data = {
            "child_name": "child_account",
            "child_icon": ""
        }
        response = self.client.post(self.create_child_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ParentChildRelation.objects.filter(parent=self.parent_profile).exists())

    def test_non_parent_cannot_create_child_account(self):
        # Attempt to create a child account using the child account
        self.authenticate(self.child_token)
        data = {"child_name": "another_child"}
        response = self.client.post(self.create_child_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Attempt to create a child account using a teacher account
        self.authenticate(self.teacher_token)
        data = {"child_name": "another_child"}
        response = self.client.post(self.create_child_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
