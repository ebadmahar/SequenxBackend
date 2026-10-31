from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, require_roles
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserOut, UserStatusUpdate, UserUpdate

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])

@router.get(
    "",
    response_model=List[UserOut],
    status_code=status.HTTP_200_OK,
    summary="List all staff users",
    description="Retrieve all registered staff members. Restricted strictly to administrators.",
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    return db.query(User).order_by(User.id.asc()).all()

@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new staff user",
    description="Register a new staff member with assigned role (admin, hr, or editor).",
)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    existing_user = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A staff user with this email address already exists",
        )

    user = User(
        name=user_in.name.strip(),
        email=user_in.email.strip().lower(),
        password_hash=get_password_hash(user_in.password),
        role=user_in.role,
        avatar=user_in.avatar,
        role_title=user_in.role_title,
        bio=user_in.bio,
        must_change_password=True,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get(
    "/{id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve details for a specific user.",
)
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

@router.put(
    "/{id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Update staff user",
    description="Update user name, email, role, or reset password.",
)
def update_user(
    id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user_in.email and user_in.email.strip().lower() != user.email:
        conflict = db.query(User).filter(User.email == user_in.email.strip().lower()).first()
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered by another account",
            )
        user.email = user_in.email.strip().lower()

    if user_in.name:
        user.name = user_in.name.strip()

    if user_in.role:
        user.role = user_in.role

    if user_in.avatar is not None:
        user.avatar = user_in.avatar
    if user_in.role_title is not None:
        user.role_title = user_in.role_title
    if user_in.bio is not None:
        user.bio = user_in.bio

    if user_in.is_active is not None:
        if user.id == current_user.id and not user_in.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot deactivate your own administrative account",
            )
        user.is_active = user_in.is_active

    if user_in.password:
        user.password_hash = get_password_hash(user_in.password)

    db.commit()
    db.refresh(user)
    return user

@router.patch(
    "/{id}/status",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Activate or deactivate user account",
    description="Toggle active status of a user. Inactive users are rejected upon login.",
)
def toggle_user_active_status(
    id: int,
    status_in: UserStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.id == current_user.id and not status_in.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot disable your own active administrative session",
        )

    user.is_active = status_in.is_active
    db.commit()
    db.refresh(user)
    return user

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete staff user",
    description="Permanently remove a staff user account.",
)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    if id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    db.delete(user)
    db.commit()
    return None

