from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIRequestFactory
from .models import User
from .permissions import IsAdmin, IsAdminOrAgent, IsCustomer, IsOwnerOrAdmin

class AuthorizationPermissionTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(email="customer@example.com",
            password="StrongPass123!", role=User.Role.CUSTOMER)
        self.agent = User.objects.create_user(email="agent@example.com",
            password="StrongPass123!", role=User.Role.AGENT)
        self.admin = User.objects.create_superuser(email="admin@example.com",
            password="StrongPass123!")

    def test_role_permissions(self):
        request = APIRequestFactory().get("/")
        request.user = self.customer
        self.assertTrue(IsCustomer().has_permission(request, None))
        self.assertFalse(IsAdmin().has_permission(request, None))
        self.assertFalse(IsAdminOrAgent().has_permission(request, None))
        request.user = self.agent
        self.assertTrue(IsAdminOrAgent().has_permission(request, None))
        self.assertFalse(IsCustomer().has_permission(request, None))
        request.user = self.admin
        self.assertTrue(IsAdmin().has_permission(request, None))

    def test_owner_or_admin(self):
        request = APIRequestFactory().get("/")
        permission = IsOwnerOrAdmin()
        owned = type("Owned", (), {"user": self.customer})()
        not_owned = type("Owned", (), {"user": self.agent})()
        request.user = self.customer
        self.assertTrue(permission.has_object_permission(request, None, owned))
        self.assertFalse(permission.has_object_permission(request, None, not_owned))
        request.user = self.admin
        self.assertTrue(permission.has_object_permission(request, None, not_owned))

class AccountApiTests(APITestCase):
    def test_registration_forces_customer_role(self):
        response = self.client.post(reverse("accounts:register"), {
            "email": "new@example.com", "password": "StrongPass123!",
            "role": "ADMIN", "is_staff": True,
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(Token.objects.filter(user=user).exists())

    def test_login_me_and_logout(self):
        user = User.objects.create_user(email="login@example.com", password="StrongPass123!")
        login = self.client.post(reverse("accounts:login"),
            {"email": user.email, "password": "StrongPass123!"}, format="json")
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        token = login.data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        me = self.client.get(reverse("accounts:current-user"))
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["email"], user.email)
        logout = self.client.post(reverse("accounts:logout"), {}, format="json")
        self.assertEqual(logout.status_code, status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(key=token).exists())
