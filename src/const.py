"""
Constant value
"""

import config

MAIN_URL = 'https://hschool-mlife.k12ea.gov.tw/ecampus_KH'
LOGIN_URL = f'{MAIN_URL}/Login.action?schNo={config.SCHNO}'
VALIDATE_URL = f'{MAIN_URL}/Validate.action'
INDEX_URL = f'{MAIN_URL}/Index.action'