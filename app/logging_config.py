import logging
import sys
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', mode='a')
    ]
)

logger = logging.getLogger('share_up_app')

if settings.debug:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
