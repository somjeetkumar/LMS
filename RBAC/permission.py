from rest_framework.permissions import BasePermission
from project.models import Test_Track
from .policies import ROLE_BASE_POLICES,ACTION_MAP

class RBAC_Permission(BasePermission):
    def has_permission(self, request, view):


        user = request.user

        if not user.is_authenticated:
            return False
        
        role = getattr(user,'role',None)

        if not role:
            return False
        
        module = view.basename
        action = ACTION_MAP.get(view.action)

        if not action:
            return False
        
                # allowed_actions = RBAC_POLICY.get(role, {}).get(module, [])
        allowed_action = ROLE_BASE_POLICES.get(role,{}).get(module,[])

        return action in allowed_action
    
