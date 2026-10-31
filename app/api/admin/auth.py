import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserOut, UserUpdate
from app.utils.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="Authenticate and receive access token",
    description="OAuth2 compatible password login endpoint returning JWT bearer token and user role.",
)
@limiter.limit("5/minute")
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username.strip().lower()).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled. Please contact the administrator.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate single session token (invalidates other simultaneous logins for this account)
    new_session_token = uuid.uuid4().hex
    user.session_token = new_session_token
    db.commit()

    access_token = create_access_token(
        subject=user.email,
        role=user.role.value,
        session_id=new_session_token,
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        role=user.role.value,
    )

@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
    description="Retrieve the profile of the currently authenticated staff member.",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    return current_user

@router.put(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile",
    description="Update profile details and author bio of current user. Requires previous password to change email or password.",
)
def update_current_user_profile(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    changing_email = user_in.email and user_in.email.strip().lower() != current_user.email
    changing_password = bool(user_in.password and user_in.password.strip())

    if changing_email or changing_password:
        if not user_in.current_password or not verify_password(user_in.current_password, current_user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect. Please enter your valid current password to change your email or password.",
            )

    if changing_email:
        new_email = user_in.email.strip().lower()
        conflict = db.query(User).filter(User.email == new_email).first()
        if conflict and conflict.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address is already in use by another account",
            )
        current_user.email = new_email

    if changing_password:
        current_user.password_hash = get_password_hash(user_in.password.strip())
        current_user.must_change_password = False

    if user_in.name:
        current_user.name = user_in.name.strip()
    if user_in.avatar is not None:
        current_user.avatar = user_in.avatar
    if user_in.role_title is not None:
        current_user.role_title = user_in.role_title
    if user_in.bio is not None:
        current_user.bio = user_in.bio

    db.commit()
    db.refresh(current_user)
    return current_user

