from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    #path('projects/', views.ProjectListCreateView.as_view(), name='project-list'),
    path('projects/all/', views.AllProjectsView.as_view(), name='all-projects'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('tasks/', views.TaskListCreateView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('updates/', views.DailyUpdateListCreateView.as_view(), name='update-list'),
    #path('add-team-member/', views.AddTeamMemberView.as_view(), name='add-team-member'), 
    path('users/', views.AllUsersView.as_view(), name='all-users'),


    #newly
   path('projects/<int:pk>/add_member/', views.AddTeamMemberView.as_view(), name='add-member'),
   path('projects/<int:pk>/remove_member/', views.RemoveTeamMemberView.as_view(), name='remove-member'),

]