
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.app.api.v1.users import erase_user, patch_user, read_user, read_users, write_user
from src.app.core.exceptions.http_exceptions import DuplicateValueException, ForbiddenException, NotFoundException
from src.app.schemas.user import UserCreate, UserRead, UserUpdate


class TestWriteUser:

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


    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, mock_db, sample_user_data):
        user_create = UserCreate(**sample_user_data)

        with patch("src.app.api.v1.users.crud_users") as mock_crud:
            mock_crud.exists = AsyncMock(return_value=True)

            with pytest.raises(DuplicateValueException, match="Email is already registered"):
                await write_user(Mock(), user_create, mock_db)


    @pytest.mark.asyncio
    async def test_create_user_duplicate_username(self, mock_db, sample_user_data):
        user_create = UserCreate(**sample_user_data)

        with patch("src.app.api.v1.users.crud_users") as mock_crud:
            mock_crud.exists = AsyncMock(side_effect=[False, True])

            with pytest.raises(DuplicateValueException, match="Username not available"):
                await write_user(Mock(), user_create, mock_db)

class TestReadUser:

    @pytest.mark.asyncio
    async def test_read_user_success(self, mock_db, sample_user_read):
        username = "test_user"

        with patch("src.app.api.v1.users.crud_users") as mock_crud:
            mock_crud.get = AsyncMock(return_value=sample_user_read)

            result = await read_user(Mock(), username, mock_db)

            assert result == sample_user_read
            mock_crud.get.assert_called_once_with(
                db=mock_db, username=username, is_deleted=False, schema_to_select=UserRead
            )

    @pytest.mark.asyncio
    async def test_read_user_not_found(self, mock_db):
        username = "nonexistent_user"

        with patch("src.app.api.v1.users.crud_users") as mock_crud:
            mock_crud.get = AsyncMock(return_value=None)

            with pytest.raises(NotFoundException, match="User not found"):
                await read_user(Mock(), username, mock_db)

class TestReadUsers:

    @pytest.mark.asyncio
    async def test_read_users_success(self, mock_db):
        mock_users_data = {"data": [{"id": 1}, {"id": 2}], "count": 2}

        with patch("src.app.api.v1.users.crud_users") as mock_crud:
            mock_crud.get_multi = AsyncMock(return_value=mock_users_data)

            with patch("src.app.api.v1.users.paginated_response") as mock_paginated:
                expected_response = {"data": [{"id": 1}, {"id": 2}], "pagination": {}}
                mock_paginated.return_value = expected_response

                result = await read_users(Mock(), mock_db, page=1, items_per_page=10)

                assert result == expected_response
                mock_crud.get_multi.assert_called_once()
                mock_paginated.assert_called_once()

class TestReadUsers:

    @pytest.mark.asyncio
    async def test_read_users_success(self, mock_db):
        mock_users_data = {"data": [{"id": 1}, {"id": 2}], "count": 2}

        with patch("src.app.api.v1.users.crud_users") as mock_crud:
            mock_crud.get_multi = AsyncMock(return_value=mock_users_data)

            with patch("src.app.api.v1.users.paginated_response") as mock_paginated:
                expected_response = {"data": [{"id": 1}, {"id": 2}], "pagination": {}}
                mock_paginated.return_value = expected_response

                result = await read_users(Mock(), mock_db, page=1, items_per_page=10)

                assert result == expected_response
                mock_crud.get_multi.assert_called_once()
                mock_paginated.assert_called_once()

class TestPatchUser:

    @pytest.mark.asyncio
    async def test_patch_user_success(self, mock_db, current_user_dict, sample_user_read):
        username = current_user_dict["username"]
        sample_user_read.username = username  
        user_update = UserUpdate(name="New Name")

        with patch("src.app.api.v1.users.crud_users") as mock_crud:
            mock_crud.get = AsyncMock(return_value=sample_user_read)
            mock_crud.exists = AsyncMock(return_value=False)
            mock_crud.update = AsyncMock(return_value=None)

            result = await patch_user(Mock(), user_update, username, current_user_dict, mock_db)

            assert result == {"message": "User updated"}
            mock_crud.update.assert_called_once()