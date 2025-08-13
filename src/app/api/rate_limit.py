from typing import Annotated, Any, cast
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response

from ...api.dependencies import get_current_superuser
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_rate_limit import crud_rate_limits
from ...crud.crud_tier import crud_tiers
from ...schemas.rate_limit import RateLimitCreate, RateLimitCreateInternal, RateLimitRead, RateLimitUpdate
from ...schemas.tier import TierRead

router = APIRouter(tags=["rate_limits"])

@router.post("/tier/{tier_name}/rate_limit", dependencies=[Depends(get_current_superuser)], status_code=201)
async def create_rate_limit(
    req: Request, tier_name: str, rate_limit_input: RateLimitCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> RateLimitRead:
    tier_obj = await crud_tiers.get(db=db, name=tier_name)
    if not tier_obj:
        raise NotFoundException("Tier not found")
    if await crud_rate_limits.exists(db=db, name=rate_limit_input.name):
        raise DuplicateValueException("Rate Limit Name not available")
    internal_rl = RateLimitCreateInternal(**{**rate_limit_input.model_dump(), "tier_id": tier_obj.id})
    new_rl = await crud_rate_limits.create(db=db, object=internal_rl)
    rl_out = await crud_rate_limits.get(db=db, id=new_rl.id)
    if not rl_out:
        raise NotFoundException("Created rate limit not found")
    return rl_out

@router.get("/tier/{tier_name}/rate_limits", response_model=PaginatedListResponse[RateLimitRead])
async def list_rate_limits(
    req: Request, tier_name: str, db: Annotated[AsyncSession, Depends(async_get_db)], page: int = 1, items_per_page: int = 10
) -> dict[str, Any]:
    tier_obj = await crud_tiers.get(db=db, name=tier_name)
    if not tier_obj:
        raise NotFoundException("Tier not found")
    rl_list = await crud_rate_limits.get_multi(
        db=db, tier_id=tier_obj.id, offset=(page-1)*items_per_page, limit=items_per_page
    )
    return paginated_response(rl_list, page=page, items_per_page=items_per_page)

@router.get("/tier/{tier_name}/rate_limit/{rl_id}", response_model=RateLimitRead)
async def get_rate_limit(
    req: Request, tier_name: str, rl_id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> RateLimitRead:
    tier_obj = await crud_tiers.get(db=db, name=tier_name)
    if not tier_obj:
        raise NotFoundException("Tier not found")
    rl_obj = await crud_rate_limits.get(db=db, tier_id=tier_obj.id, id=rl_id)
    if not rl_obj:
        raise NotFoundException("Rate Limit not found")
    return rl_obj

@router.patch("/tier/{tier_name}/rate_limit/{rl_id}", dependencies=[Depends(get_current_superuser)])
async def update_rate_limit(
    req: Request, tier_name: str, rl_id: int, values: RateLimitUpdate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    tier_obj = await crud_tiers.get(db=db, name=tier_name)
    if not tier_obj:
        raise NotFoundException("Tier not found")
    rl_obj = await crud_rate_limits.get(db=db, tier_id=tier_obj.id, id=rl_id)
    if not rl_obj:
        raise NotFoundException("Rate Limit not found")
    await crud_rate_limits.update(db=db, object=values, id=rl_id)
    return {"message": "Rate Limit updated"}

@router.delete("/tier/{tier_name}/rate_limit/{rl_id}", dependencies=[Depends(get_current_superuser)])
async def delete_rate_limit(
    req: Request, tier_name: str, rl_id: int, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> dict[str, str]:
    tier_obj = await crud_tiers.get(db=db, name=tier_name)
    if not tier_obj:
        raise NotFoundException("Tier not found")
    rl_obj = await crud_rate_limits.get(db=db, tier_id=tier_obj.id, id=rl_id)
    if not rl_obj:
        raise NotFoundException("Rate Limit not found")
    await crud_rate_limits.delete(db=db, id=rl_id)
    return {"message": "Rate Limit deleted"}
