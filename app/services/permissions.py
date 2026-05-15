from fastapi import HTTPException, status


def check_owner(resource_user_id: int, current_user) -> None:
    """Allow if user is admin or owns the resource. Raise 403 otherwise."""
    if current_user.role == "admin":
        return
    if resource_user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own resources",
        )