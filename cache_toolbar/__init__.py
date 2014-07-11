import logging
from django.utils.log import NullHandler

logging.basicConfig()

logger = logging.getLogger(__name__)
if not logger.handlers:
    logger.addHandler(NullHandler())
