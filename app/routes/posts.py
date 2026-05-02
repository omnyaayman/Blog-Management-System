from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, require_role

router = APIRouter()


# =========================================================
# Authentication (Member 2)
# =========================================================
@router.get("/protected")
def protected_route(
    current_user = Depends(get_current_user)
):
    return {
        "message": "You are authenticated",
        "user": current_user.username,
        "role": current_user.role
    }


# =========================================================
#  Member 3 
# =========================================================
@router.get("/admin-only")
def admin_route(
    current_user = Depends(require_role(["admin"]))
):
    return {
        "message": "Welcome Admin",
        "user": current_user.username
    }

@router.post("/posts")
def create_post(
    current_user = Depends(require_role(["admin", "author"]))
):
    return {
        "message": "Post created successfully",
        "user": current_user.username,
        "role": current_user.role
    }
    
