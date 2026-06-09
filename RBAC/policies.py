from rest_framework.permissions import BasePermission

ROLE_BASE_POLICES = {
    "admin": {
        "course":["create", "update", "delete", "read","enrollment","subject"],
        "subject":["create","update","delete","read","chapter","pdf"],
        "chapter":["create","update","delete","read","topics"],
        "content":["create","update","delete","read"],
        "topics":["create","update","delete","read","Teacher_files","student_files","uncheck_files"],
        "Teacherfiles":True,
        "files":['update','read','delete']  
    },
    "head_teacher": {
        "course":[ "read","subject","enrollment",],
        "subject":["create","update","delete","read","chapter","pdf"],
        "chapter":["create","update","delete","read","topics"],
        "content":["create","update","delete","read"],
        "topics":["create","update","delete","read","Teacher_files","student_files","uncheck_files"],
        "Teacherfiles":True,
        "files":['update','read','delete']
        # "contents":["create","update","delete","read"],
    },
    "teacher": {
        "course": ["read","enrollment","subject"],
        "subject":["read","chapter","pdf"],
        "chapter":["create","update","delete","read","topics"],
        "content":["create","update","delete","read","topics"],
        "topics":["create","update","delete","read","Teacher_files","student_files","uncheck_files"],
        "Teacherfiles":True,
        "files":['update','read','delete']        # "contents":["create","update","delete","read"],
    },
    "student": {
        "course": ["read","subject"],
        "subject":["read","chapter"],
        "chapter":["read","teacher_topics","topics","studentTest","studentTestsubmitcheck"],
        "content":["read"],
        "topics":["read","Teacher_files","student_files","ai-topic-tutor"],
        # "studentTest":['read']
        # "files":['update','read','delete']        # "contents":["read"],

    }
}


ACTION_MAP = {
    "list": "read",
    "retrieve": "read",
    "create": "create",
    "update": "update",
    "partial_update": "update",
    "destroy": "delete",
    "test":"test",
    "course_enroll":"enrollment",
    "course_subject":"subject",
    "TeacherfileOpration":"Teacherfiles",
    "chapterOFSubject":"chapter",
    "topics":"topics",
    "TeacherfileOpration":"Teacher_files",
    "studentfileOpration":"student_files",
    "studentUncheckfileOpration":"uncheck_files",
    "get_pdf":"pdf",
    "studentTestData":"studentTest",
    "studentTestsubmit":"studentTestsubmitcheck",
    "studentDoutSolve":"ai-topic-tutor"
}                             
                              

class RoleBasedPermission(BasePermission):

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False
        user_role = request.user.role  

        model_name = view.queryset.model._meta.model_name
        action = ACTION_MAP.get(view.action)

    
        if user_role not in ROLE_BASE_POLICES:
            return False
        role_permissions = ROLE_BASE_POLICES[user_role].get(model_name)

        if not role_permissions:
            return False
        return action in role_permissions
    
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        
        if request.user.role == 'head_teacher':
            return obj.M_teacher == request.user
        
        if  request.user.role == 'teacher':
            return obj.teacher == request.user

        return None
    

