from typing import Annotated, Any, cast
from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from ...core.security import blacklist_token, get_password_hash, oauth2_scheme
from ...crud.crud_rate_limit import crud_rate_limits
from ...crud.crud_tier import crud_tiers
from ...crud.crud_users import crud_users
from ...schemas.tier import TierRead
from ...schemas.user import UserCreate, UserCreateInternal, UserRead, UserTierUpdate, UserUpdate

member_router = APIRouter(tags=["members"])

async def _get_db_session() -> AsyncSession:
    return async_get_db()

@member_router.post("/member/add", response_model=UserRead, status_code=201)
async def register_member(request: Request, member_info: UserCreate, db: Annotated[AsyncSession, Depends(_get_db_session)]) -> UserRead:
    if await crud_users.exists(db=db, email=member_info.email):
        raise DuplicateValueException("Email already exists")
    if await crud_users.exists(db=db, username=member_info.username):
        raise DuplicateValueException("Username not available")

    internal_data = member_info.model_dump()
    internal_data["hashed_password"] = get_password_hash(password=internal_data.pop("password"))
    member_internal = UserCreateInternal(**internal_data)

    created_member = await crud_users.create(db=db, object=member_internal)
    member_read = await crud_users.get(db=db, id=created_member.id, schema_to_select=UserRead)
    if not member_read:
        raise NotFoundException("Member not found after creation")

    return cast(UserRead, member_read)


@member_router.get("/members/list", response_model=PaginatedListResponse[UserRead])
async def list_members(request: Request, db: Annotated[AsyncSession, Depends(_get_db_session)], page: int = 1, per_page: int = 10) -> dict:
    members_data = await crud_users.get_multi(
        db=db, offset=compute_offset(page, per_page), limit=per_page, is_deleted=False
    )
    response: dict[str, Any] = paginated_response(crud_data=members_data, page=page, items_per_page=per_page)
    return response


@member_router.get("/member/me", response_model=UserRead)
async def get_current_member(request: Request, current_user: Annotated[dict, Depends(get_current_user)]) -> dict:
    return current_user


@member_router.get("/member/{user_name}", response_model=UserRead)
async def get_member(user_name: str, db: Annotated[AsyncSession, Depends(_get_db_session)]) -> UserRead:
    member = await crud_users.get(db=db, username=user_name, is_deleted=False, schema_to_select=UserRead)
    if not member:
        raise NotFoundException("Member not found")
    return cast(UserRead, member)


@member_router.patch("/member/{user_name}")
async def update_member(
    user_name: str,
    changes: UserUpdate,
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(_get_db_session)]
) -> dict[str, str]:
    member = await crud_users.get(db=db, username=user_name, schema_to_select=UserRead)
    if not member:
        raise NotFoundException("Member not found")
    member = cast(UserRead, member)

    if current_user["username"] != member.username:
        raise ForbiddenException()

    if changes.username != member.username and await crud_users.exists(db=db, username=changes.username):
        raise DuplicateValueException("Username not available")
    if changes.email != member.email and await crud_users.exists(db=db, email=changes.email):
        raise DuplicateValueException("Email already exists")

    await crud_users.update(db=db, object=changes, username=user_name)
    return {"message": "Member updated"}


@member_router.delete("/member/{user_name}")
async def remove_member(
    user_name: str,
    request: Request,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(_get_db_session)],
    token: str = Depends(oauth2_scheme)
) -> dict[str, str]:
    member = await crud_users.get(db=db, username=user_name, schema_to_select=UserRead)
    if not member:
        raise NotFoundException("Member not found")

    if user_name != current_user["username"]:
        raise ForbiddenException()

    await crud_users.delete(db=db, username=user_name)
    await blacklist_token(token=token, db=db)
    return {"message": "Member deleted"}


@member_router.get("/member/{user_name}/tier/rate_limits", dependencies=[Depends(get_current_superuser)])
async def get_member_tier_rate_limits(user_name: str, db: Annotated[AsyncSession, Depends(_get_db_session)]) -> dict[str, Any]:
    member = await crud_users.get(db=db, username=user_name, schema_to_select=UserRead)
    if not member:
        raise NotFoundException("Member not found")
    member = cast(UserRead, member)
    result = member.model_dump()

    if member.tier_id is None:
        result["tier_rate_limits"] = []
        return result

    tier = await crud_tiers.get(db=db, id=member.tier_id, schema_to_select=TierRead)
    if not tier:
        raise NotFoundException("Tier not found")
    tier = cast(TierRead, tier)

    rate_limits = await crud_rate_limits.get_multi(db=db, tier_id=tier.id)
    result["tier_rate_limits"] = rate_limits.get("data", [])
    return result
