import pytest
from src.container import logger


@pytest.mark.asyncio
async def test_jwt_environment_setup(client, create_db_and_tables_and_user_stuff):
    all_setup_created = await create_db_and_tables_and_user_stuff
    assert all_setup_created == True
    logger.info("Tested setting up environment for stuff successfully.")
