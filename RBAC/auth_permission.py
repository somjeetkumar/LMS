from rest_framework.permissions import BasePermission


class is_Admin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'
    


class is_Student(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student'
    


class is_HeadTeacher(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'head_teacher'
    
