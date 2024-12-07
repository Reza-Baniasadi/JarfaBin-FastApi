from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Request
from fastcrud.paginated import PaginatedListResponse, compute_offset, paginated_response
from sqlalchemy.ext.asyncio import AsyncSession

from ...api.dependencies import get_current_superuser
from ...core.db.database import async_get_db
from ...core.exceptions.http_exceptions import DuplicateValueException, NotFoundException
from ...crud.crud_rate_limit import crud_rate_limits
from ...crud.crud_tier import crud_tiers
from ...schemas.rate_limit import RateLimitCreate, RateLimitCreateInternal, RateLimitRead, RateLimitUpdate
from ...schemas.tier import TierRead

router = APIRouter(tags=["rate_limits"])


@router.post("/tier/{tier_name}/rate_limit", dependencies=[Depends(get_current_superuser)], status_code=201)
async def write_rate_limit(
    request: Request, tier_name: str, rate_limit: RateLimitCreate, db: Annotated[AsyncSession, Depends(async_get_db)]
) -> RateLimitRead:
    db_tier = await crud_tiers.get(db=db, name=tier_name, schema_to_select=TierRead)
    if not db_tier:
        raise NotFoundException("Tier not found")

    db_tier = cast(TierRead, db_tier)
    rate_limit_internal_dict = rate_limit.model_dump()
    rate_limit_internal_dict["tier_id"] = db_tier.id

    db_rate_limit = await crud_rate_limits.exists(db=db, name=rate_limit_internal_dict["name"])
    if db_rate_limit:
        raise DuplicateValueException("Rate Limit Name not available")

    rate_limit_internal = RateLimitCreateInternal(**rate_limit_internal_dict)
    created_rate_limit = await crud_rate_limits.create(db=db, object=rate_limit_internal)

    rate_limit_read = await crud_rate_limits.get(db=db, id=created_rate_limit.id, schema_to_select=RateLimitRead)
    if rate_limit_read is None:
        raise NotFoundException("Created rate limit not found")

    return cast(RateLimitRead, rate_limit_read)