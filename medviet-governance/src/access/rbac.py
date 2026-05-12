# src/access/rbac.py
import casbin
from functools import wraps
from fastapi import HTTPException, Header
from typing import Optional

# Danh sách user giả lập (production dùng JWT + DB)
MOCK_USERS = {
    "token-alice": {"username": "alice", "role": "admin"},
    "token-bob":   {"username": "bob",   "role": "ml_engineer"},
    "token-carol": {"username": "carol", "role": "data_analyst"},
    "token-dave":  {"username": "dave",  "role": "intern"},
}

class RBACEnforcer:
    """Casbin-based RBAC enforcer."""

    def __init__(self, model_path: str, policy_path: str):
        """Initialize Casbin enforcer with model and policies."""
        self.enforcer = casbin.Enforcer(model_path, policy_path)

    def enforce(self, user: str, resource: str, action: str) -> bool:
        """Check if user has permission for action on resource."""
        result = self.enforcer.enforce(user, resource, action)
        return result

    def add_policy(self, subject: str, obj: str, action: str):
        """Add a new policy rule."""
        self.enforcer.add_policy(subject, obj, action)

    def add_role_for_user(self, user: str, role: str):
        """Assign role to user."""
        self.enforcer.add_grouping_policy(user, role)

    def get_roles_for_user(self, user: str) -> list:
        """Get all roles for a user."""
        return self.enforcer.get_roles_for_user(user)

    def get_permissions_for_user(self, user: str) -> list:
        """Get all permissions (direct and via roles)."""
        return self.enforcer.get_permissions_for_user(user)

enforcer = None
def init_enforcer():
    global enforcer
    if enforcer is None:
        enforcer = RBACEnforcer("src/access/model.conf", "src/access/policy.csv")
    return enforcer

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    Parse Bearer token và trả về user info.
    Raise HTTPException 401 nếu token không hợp lệ.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ")[1]
    user = MOCK_USERS.get(token)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user

def require_permission(resource: str, action: str):
    """
    Decorator kiểm tra RBAC permission.
    Dùng casbin enforcer để check (role, resource, action).
    Raise HTTPException 403 nếu không có quyền.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            role = current_user["role"]

            rbac = init_enforcer()
            allowed = rbac.enforce(role, resource, action)

            if not allowed:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role '{role}' cannot '{action}' on '{resource}'"
                )
            return await func(*args, **kwargs)
        return wrapper
    return decorator
