
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.app.api.v1.users import erase_user, patch_user, read_user, read_users, write_user
from src.app.core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from src.app.schemas.user import UserCreate, UserRead, UserUpdate


class TestWriteUser:
    """Test user creation endpoint."""

    @pytest.mark.asyncio
    async def test_create_user_success(self, mock_db, sample_user_data, sample_user_read):
        user_create = UserCreate(**sample_user_data)

        with patch("src.app.api.v1.users.crud_users") as mock_crud:
            mock_crud.exists = AsyncMock(side_effect=[False, False]) 
            mock_crud.create = AsyncMock(return_value=Mock(id=1))
            mock_crud.get = AsyncMock(return_value=sample_user_read)

            with patch("src.app.api.v1.users.get_password_hash") as mock_hash:
                mock_hash.return_value = "hashed_password"

                result = await write_user(Mock(), user_create, mock_db)

                assert result == sample_user_read
                mock_crud.exists.assert_any_call(db=mock_db, email=user_create.email)
                mock_crud.exists.assert_any_call(db=mock_db, username=user_create.username)
                mock_crud.create.assert_called_once()