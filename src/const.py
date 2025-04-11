"""
Constant value
"""

import config

MAIN_URL = config.MAIN_URL
LOGIN_URL = f'{MAIN_URL}/Login.action?schNo={config.SCHNO}'
VALIDATE_URL = f'{MAIN_URL}/Validate.action'
INDEX_URL = f'{MAIN_URL}/Index.action'
