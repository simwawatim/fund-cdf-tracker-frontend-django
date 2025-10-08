from django.db import models
from django.contrib.auth.models import User

# ---------------------------
# Choice Options
# ---------------------------
STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('ongoing', 'Ongoing'),
    ('completed', 'Completed'),
)

FUNDING_SOURCES = (
    ('CDF', 'CDF'),
    ('Donor', 'Donor'),
    ('Government', 'Government'),
    ('Private', 'Private Partnership'),
)

USER_ROLES = (
    ('admin', 'Admin'),
    ('officer', 'Officer'),
    ('viewer', 'Viewer'),
)

PROJECT_TYPES = (
    ('education', 'Education'),
    ('health', 'Health'),
    ('infrastructure', 'Infrastructure'),
    ('other', 'Other'),
)

UPDATE_TYPES = (
    ('progress', 'Progress'),
    ('milestone', 'Milestone'),
    ('issue', 'Issue'),
)

DOC_TYPES = (
    ('proposal', 'Proposal'),
    ('report', 'Report'),
    ('photo', 'Photo'),
    ('other', 'Other'),
)

class Program(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# ---------------------------
# Constituency Model
# ---------------------------
class Constituency(models.Model):
    name = models.CharField(max_length=100, unique=True)
    district = models.CharField(max_length=100)
    constituency_code = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.constituency_code})"
    

    def save(self, *args, **kwargs):
        if not self.constituency_code:
            last = Constituency.objects.all().order_by('-id').first()
            if last and last.constituency_code.isdigit():
                next_code = str(int(last.constituency_code) + 1).zfill(4)
            else:
                next_code = '0001'
            self.constituency_code = next_code
        super().save(*args, **kwargs)

# ---------------------------
# User Profile / Roles
# ---------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='viewer')
    phone = models.CharField(max_length=20, null=True, blank=True)
    constituency = models.ForeignKey(Constituency, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username} ({self.role})"

# ---------------------------
# Project Model
# ---------------------------
class Project(models.Model):
    name = models.CharField(max_length=200)
    constituency = models.ForeignKey(Constituency, on_delete=models.CASCADE, related_name='projects')
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    allocated_budget = models.DecimalField(max_digits=12, decimal_places=2)
    actual_expenditure = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    completion_percentage = models.PositiveSmallIntegerField(default=0)
    beneficiaries_count = models.PositiveIntegerField(null=True, blank=True)
    project_manager = models.CharField(max_length=100, null=True, blank=True)
    funding_source = models.CharField(max_length=50, choices=FUNDING_SOURCES, default='CDF')
    location = models.CharField(max_length=200, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_projects')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # Soft delete / archive

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.constituency.name})"

    # ---------------------------
    # Auto-calculate completion and expenditure
    # ---------------------------
    def update_completion(self):
        updates = self.updates.all()
        if updates.exists():
            avg_progress = sum(u.progress_percentage for u in updates) / updates.count()
            self.completion_percentage = int(avg_progress)
            self.save()

    def update_expenditure(self):
        reports = self.financial_reports.all()
        total_spent = sum(r.amount_spent for r in reports)
        self.actual_expenditure = total_spent
        self.save()

# ---------------------------
# Project Update / Progress Log
# ---------------------------
class ProjectUpdate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='updates')
    update_type = models.CharField(max_length=20, choices=UPDATE_TYPES, default='progress')
    date = models.DateTimeField(auto_now_add=True)
    progress_percentage = models.PositiveSmallIntegerField()
    remarks = models.TextField(null=True, blank=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_updates')
    is_active = models.BooleanField(default=True)  # For soft delete / archiving

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.project.name} Update - {self.progress_percentage}%"

# ---------------------------
# Financial Report / Spending
# ---------------------------
class FinancialReport(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='financial_reports')
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()
    category = models.CharField(max_length=50, null=True, blank=True)  # Materials, Labor, Admin
    amount_spent = models.DecimalField(max_digits=12, decimal_places=2)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_reports')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.project.name} - {self.amount_spent}"

# ---------------------------
# Project Attachments / Documents
# ---------------------------
class ProjectDocument(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPES, default='other')
    file = models.FileField(upload_to='project_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_documents')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.project.name} - {self.title}"
    


# ---------------------------
# Project Messages / Comments
# ---------------------------
class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_comments')
    message = models.TextField()
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    ) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project.name}"
