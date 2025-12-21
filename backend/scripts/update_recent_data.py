#!/usr/bin/env python3
"""
Incremental Data Update Script

Run this script periodically to update database with latest bars.
Should be run via cron every 15 minutes during market hours.

Usage:
    python3 -m backend.scripts.update_recent_data

Cron example (every 15 min, Mon-Fri, 9:30am-4pm ET):
    */15 9-16 * * 1-5 cd /app && python3 -m backend.scripts.update_recent_data >> /var/log/app/data_updates.log 2>&1
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
from datetime import datetime

# Add backend to path for imports
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.data_prewarming_service import DataPrewarmingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('data_updates.log')
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Run incremental data update."""
    try:
        logger.info("=" * 80)
        logger.info(f"INCREMENTAL UPDATE STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 80)

        service = DataPrewarmingService()
        result = await service.update_recent_data()

        logger.info("=" * 80)
        logger.info("INCREMENTAL UPDATE COMPLETED")
        logger.info(f"Datasets updated: {result['updated']}")
        logger.info(f"Errors: {result['errors']}")
        logger.info("=" * 80)

        if result['errors'] > 0:
            logger.warning(f"{result['errors']} errors occurred during update")
            return 1

        return 0

    except Exception as e:
        logger.error(f"❌ Incremental update failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
