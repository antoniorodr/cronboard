from cronboard.services.cron_encrypt_service import CronEncryptService


async def test_encrypt_password(encrypted_password) -> None:
    encrypted_password, password = encrypted_password
    assert encrypted_password != password and encrypted_password != ""


async def test_decrypt_password(encrypted_password) -> None:
    encrypted_password, password = encrypted_password
    decrypted_password = CronEncryptService.decrypt_password(encrypted_password)
    assert decrypted_password == password


async def test_encrypt_telegram_token(encrypted_token) -> None:
    encrypted_token, token = encrypted_token
    assert encrypted_token != token and encrypted_token != ""


async def test_decrypt_telegram_token(encrypted_token) -> None:
    encrypted_token, token = encrypted_token
    decrypted_token = CronEncryptService.decrypt_telegram_token(encrypted_token)
    assert decrypted_token == token
