# 👉 https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class
from __future__ import annotations

from EPHEMERAL_TALKER import EPHEMERAL_TALKER
from TRANSCRIBER_TALKER import TRANSCRIBER_TALKER
from SELFIE_TALKER import SELFIE_TALKER

from TALKER_BASE import TALKER_BASE


class TALKER(
    EPHEMERAL_TALKER,
    SELFIE_TALKER,
    TRANSCRIBER_TALKER,
    TALKER_BASE):
    '''😃 Talker
    * https://quip.com/J24GAMbu7HKF/-Talker'''
    
    pass
