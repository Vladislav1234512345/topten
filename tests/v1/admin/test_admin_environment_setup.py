import pytest

import logging
from src.container import configure_logging
from src.config import logging_settings

logger = logging.getLogger(__name__)
configure_logging(level=logging_settings.logging_level)


@pytest.mark.asyncio
async def test_admin_environment_setup(client, create_db_and_tables_and_user_admin):
    all_setup_created = await create_db_and_tables_and_user_admin
    assert all_setup_created == True
    logger.info("Tested setting up environment for admin.")
