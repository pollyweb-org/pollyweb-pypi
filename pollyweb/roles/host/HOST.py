# 🤗 HOST


from pollyweb import LOG

from HOST_API_BASE import HOST_API_BASE
from HOST_API_BROKER import HOST_API_BROKER
from HOST_API_PROMPT import HOST_API_PROMPT
from HOST_API_PALMER import HOST_API_PALMER


class HOST(
    HOST_API_PROMPT,
    HOST_API_BROKER,
    HOST_API_PALMER,
    HOST_API_BASE
    ):
    ''' 🤗 https://quip.com/s9oCAO3UR38A/-Host \n
    Events:
     * OnCheckOut@Host (optional)
     * HandleFound@Host (required)
    '''

