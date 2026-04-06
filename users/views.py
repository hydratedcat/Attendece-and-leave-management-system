from rest_framework import generics, permissions

from .models import CustomUser
from .permissions import IsHRAdmin
from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListCreateView(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsHRAdmin]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return RegisterSerializer
        return UserSerializer
