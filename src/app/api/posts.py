from typing import Annotated, Any, cast
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response

from ...api.dependencies import get_current_superuser, get_current_user
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import ForbiddenException, NotFoundException
from ...core.utils.cache import cache
from ...crud.crud_posts import crud_posts
from ...crud.crud_users import crud_users
from ...schemas.post import PostCreate, PostCreateInternal, PostRead, PostUpdate
from ...schemas.user import UserRead

router = APIRouter(tags=["posts"])

@router.post("/{username}/post", response_model=PostRead, status_code=201)
async def create_post(
    req: Request,
    username: str,
    post_input: PostCreate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> PostRead:
    user_obj = await crud_users.get(db, username=username, is_deleted=False)
    if not user_obj:
        raise NotFoundException("کاربر یافت نشد")
    if current_user["id"] != user_obj.id:
        raise ForbiddenException()
    internal_post = PostCreateInternal(**{**post_input.model_dump(), "created_by_user_id": user_obj.id})
    new_post = await crud_posts.create(db, object=internal_post)
    post_out = await crud_posts.get(db, id=new_post.id)
    if not post_out:
        raise NotFoundException("پست ایجاد شده یافت نشد")
    return post_out

@router.get("/{username}/posts", response_model=PaginatedListResponse[PostRead])
@cache(key_prefix="{username}_posts_cache:page_{page}", resource_id_name="username", expiration=90)
async def list_posts(
    req: Request,
    username: str,
    db: Annotated[AsyncSession, Depends(async_get_db)],
    page: int = 1,
    items_per_page: int = 10,
) -> dict:
    user_obj = await crud_users.get(db, username=username, is_deleted=False)
    if not user_obj:
        raise NotFoundException("کاربر یافت نشد")
    posts_list = await crud_posts.get_multi(
        db,
        offset=(page-1)*items_per_page,
        limit=items_per_page,
        created_by_user_id=user_obj.id,
        is_deleted=False,
    )
    return paginated_response(posts_list, page=page, items_per_page=items_per_page)

@router.get("/{username}/post/{post_id}", response_model=PostRead)
@cache(key_prefix="{username}_single_post_cache", resource_id_name="post_id")
async def get_post(
    req: Request, username: str, post_id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> PostRead:
    user_obj = await crud_users.get(db, username=username, is_deleted=False)
    if not user_obj:
        raise NotFoundException("کاربر یافت نشد")
    post_obj = await crud_posts.get(db, id=post_id, created_by_user_id=user_obj.id, is_deleted=False)
    if not post_obj:
        raise NotFoundException("پست یافت نشد")
    return post_obj

@router.patch("/{username}/post/{post_id}")
@cache("{username}_single_post_cache", resource_id_name="post_id", pattern_to_invalidate_extra=["{username}_posts_cache:*"])
async def update_post(
    req: Request,
    username: str,
    post_id: int,
    values: PostUpdate,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    user_obj = await crud_users.get(db, username=username, is_deleted=False)
    if not user_obj:
        raise NotFoundException("کاربر یافت نشد")
    if current_user["id"] != user_obj.id:
        raise ForbiddenException()
    post_obj = await crud_posts.get(db, id=post_id, is_deleted=False)
    if not post_obj:
        raise NotFoundException("پست یافت نشد")
    await crud_posts.update(db, object=values, id=post_id)
    return {"message": "پست به‌روز شد"}

@router.delete("/{username}/post/{post_id}")
@cache("{username}_single_post_cache", resource_id_name="post_id", to_invalidate_extra={"{username}_posts_cache": "{username}"})
async def delete_post(
    req: Request,
    username: str,
    post_id: int,
    current_user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(async_get_db)],
) -> dict[str, str]:
    user_obj = await crud_users.get(db, username=username, is_deleted=False)
    if not user_obj:
        raise NotFoundException("کاربر یافت نشد")
    if current_user["id"] != user_obj.id:
        raise ForbiddenException()
    post_obj = await crud_posts.get(db, id=post_id, is_deleted=False)
    if not post_obj:
        raise NotFoundException("پست یافت نشد")
    await crud_posts.delete(db, id=post_id)
    return {"message": "پست حذف شد"}

@router.delete("/{username}/db_post/{post_id}", dependencies=[Depends(get_current_superuser)])
@cache("{username}_single_post_cache", resource_id_name="post_id", to_invalidate_extra={"{username}_posts_cache": "{username}"})
async def hard_delete_post(
    req: Request, username: str, post_id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    user_obj = await crud_users.get(db, username=username, is_deleted=False)
    if not user_obj:
        raise NotFoundException("کاربر یافت نشد")
    post_obj = await crud_posts.get(db, id=post_id, is_deleted=False)
    if not post_obj:
        raise NotFoundException("پست یافت نشد")
    await crud_posts.db_delete(db, id=post_id)
    return {"message": "پست از پایگاه داده حذف شد"}
