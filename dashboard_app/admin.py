from django.contrib import admin
from django import forms
from .models import User, Project, Task, DailyUpdate

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'date_joined', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_superuser', 'is_staff', 'is_active')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')
    filter_horizontal = ('team_members',)

class TaskAdminForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter assignee based on selected project
        if self.instance and self.instance.pk:  # Editing existing task
            self.fields['assignee'].queryset = self.instance.project.team_members.all()
        elif 'initial' in kwargs and 'project' in kwargs['initial']:  # New task with project selected
            project_id = kwargs['initial']['project']
            try:
                project = Project.objects.get(id=project_id)
                self.fields['assignee'].queryset = project.team_members.all()
            except Project.DoesNotExist:
                self.fields['assignee'].queryset = User.objects.none()
        else:  # No project selected yet
            self.fields['assignee'].queryset = User.objects.none()

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    form = TaskAdminForm
    list_display = ('title', 'project', 'status', 'assignee', 'due_date')
    list_filter = ('status', 'due_date', 'project')
    search_fields = ('title', 'description')

@admin.register(DailyUpdate)
class DailyUpdateAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'user__username')