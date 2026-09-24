import types

import pytest
from paramiko.client import SSHClient

from cronboard.app import CronBoard
from cronboard.services.cron_encrypt_service import CronEncryptService


@pytest.fixture
async def app() -> types.AsyncGeneratorType:
    cronboard_app: CronBoard = CronBoard()
    yield cronboard_app


@pytest.fixture
async def encrypted_password() -> tuple[str, str]:
    test_password: str = "test"
    return CronEncryptService.encrypt_password(test_password), test_password


@pytest.fixture
async def encrypted_token() -> tuple[str, str]:
    test_token: str = "test"
    return CronEncryptService.encrypt_telegram_token(test_token), test_token


@pytest.fixture
async def generate_ssh_client():
    ssh_client: SSHClient | None = SSHClient()
    yield ssh_client
