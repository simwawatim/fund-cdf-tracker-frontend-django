
from base.models import Contractor, Program, Constituency, Project, ProjectComment, ProjectUpdate, ProjectDocument, UserProfile, ProjectComment
from django.contrib import admin


admin.site.register(Program)
admin.site.register(Project)
admin.site.register(UserProfile)
admin.site.register(Constituency)
admin.site.register(ProjectComment)
admin.site.register(ProjectUpdate)
admin.site.register(ProjectDocument)
admin.site.register(Contractor)
