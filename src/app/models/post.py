import uuid as uuid_pkg
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column

from ..core.db.database import Base


class Post(Base):
    __tablename__ = "post"

    # شناسه عددی خودکار
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        nullable=False,
        unique=True,
        init=False,
    )

    # شناسه کاربر ایجادکننده
    created_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"),
        index=True,
        nullable=False,
    )

    # محتوا
    title: Mapped[str] = mapped_column(String(30), nullable=False)
    text: Mapped[str] = mapped_column(String(63206), nullable=False)
    media_url: Mapped[str | None] = mapped_column(String, default=None, nullable=True)

    # شناسه UUID
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        default_factory=uuid_pkg.uuid4,
        unique=True,
        nullable=False,
    )

    # زمان‌بندی
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False,
    )
