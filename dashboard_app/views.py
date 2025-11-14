from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Q
from django.contrib.auth import login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import User, Project, Task, DailyUpdate
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer, 
    ProjectSerializer, TaskSerializer, DailyUpdateSerializer,
    AddTeamMemberSerializer
)

class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        project_id = self.request.query_params.get("project_id")

        # ✅ Only include projects where user is a member
        project_ids = Project.objects.filter(team_members=user).values_list("id", flat=True)

        queryset = Task.objects.filter(project_id__in=project_ids).select_related("project", "assignee")

        # ✅ If project_id is provided → filter tasks of that project
        if project_id:
            queryset = queryset.filter(project_id=project_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save()

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only allow admin to edit/delete projects
        if self.request.user.is_superuser:
            return Project.objects.all()
        return Project.objects.none()


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(project__team_members=self.request.user)

class DailyUpdateListCreateView(generics.ListCreateAPIView):
    serializer_class = DailyUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return DailyUpdate.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class DashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        projects = Project.objects.all()
        tasks = Task.objects.all()

        data = {
            'projects': {
                'total': projects.count(),
            },
            'tasks': {
                'total': tasks.count(),
                'todo': tasks.filter(status='todo').count(),
                'in_progress': tasks.filter(status='in_progress').count(),
                'review': tasks.filter(status='review').count(),
                'done': tasks.filter(status='done').count(),
            },
            'recent_updates': DailyUpdateSerializer(
                DailyUpdate.objects.filter(user=user).order_by('-created_at')[:5],
                many=True
            ).data,
            'recent_tasks': TaskSerializer(
                tasks.order_by('-created_at')[:5],
                many=True
            ).data,
        }
        return Response(data)



class AllUsersView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

class AllProjectsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Show all projects to everyone (for testing)
        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
    



class AddTeamMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_id = request.data.get("user_id")
        try:
            project = Project.objects.get(pk=pk)
            user = User.objects.get(pk=user_id)

            # ✅ Allow any authenticated user
            project.team_members.add(user)
            return Response({"status": "Team member added"}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, Project.DoesNotExist):
            return Response({"error": "User or project not found"}, status=status.HTTP_404_NOT_FOUND)


class RemoveTeamMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user_id = request.data.get("user_id")
        try:
            project = Project.objects.get(pk=pk)
            user = User.objects.get(pk=user_id)

            # ✅ Allow any authenticated user
            project.team_members.remove(user)
            return Response({"status": "Team member removed"}, status=status.HTTP_200_OK)

        except (User.DoesNotExist, Project.DoesNotExist):
            return Response({"error": "User or project not found"}, status=status.HTTP_404_NOT_FOUND)
        

    