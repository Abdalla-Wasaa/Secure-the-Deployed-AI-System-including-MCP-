import re
import unicodedata
from fastapi import HTTPException
PATTERN = re.compile(r'ignore (?:all |the )?(?:previous |prior )?instructions|reveal (?:the )?(?:secrets|system prompt)|dump (?:the )?environment variables|print (?:your |the )?secret|you are now', re.I)
def guard(message):
    normalized = ' '.join(unicodedata.normalize('NFKC', message).split())
    if PATTERN.search(normalized):
        raise HTTPException(400, 'Instruction override rejected')
