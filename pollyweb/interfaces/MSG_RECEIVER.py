# 📚 MSG_RECEIVER

import json
from typing import Any, Callable, Optional

from ..utils import LOG
from ..utils import UTILS
from .MSG import MSG


class MSG_RECEIVER:
    """Lightweight message receiver for inbox-like endpoints.

    Responsibilities:
    - Parse incoming events
    - Validate headers (and optionally signatures)
    - Execute a handler with the envelope
    """

    def __init__(self):
        self._timer = UTILS.Timer()

    def _elapsed(self):
        return self._timer.Elapsed()

    def _parse(self, event: dict[str, Any]) -> dict[str, Any]:
        UTILS.Require(event)

        envelope = {}
        if 'httpMethod' not in event:
            envelope = event
        elif 'body' in event and event['body'] is not None:
            envelope = json.loads(event['body'])
        elif event['httpMethod'] == 'GET':
            envelope = {}

        return envelope

    def _validate(
        self,
        msg: MSG,
        speed: dict[str, Any],
        expected_to: Optional[str] = None,
        validator: Optional[Any] = None,
        public_key: Optional[str] = None,
        public_key_provider: Optional[Callable[[MSG], str]] = None,
        ignore_validation: bool = False,
    ) -> dict[str, Any]:
        error = None
        checks: list[str] = []

        try:
            msg.VerifyHeader()
            checks.append('Header ok')

            if expected_to is not None:
                UTILS.AssertEqual(
                    given=msg.RequireTo().lower(),
                    expect=expected_to.lower(),
                    msg=f'Wrong domain. Expected [{expected_to}], but received [{msg.RequireTo()}]!')
                checks.append('Recipient ok')

            if not ignore_validation:
                if public_key_provider is not None and public_key is None:
                    public_key = public_key_provider(msg)

                if validator is not None:
                    if public_key is None:
                        raise ValueError('public_key is required when validator is provided.')
                    started = self._timer.StartWatch()
                    msg.VerifySignature(publicKey=public_key, validator=validator)
                    checks.append('Signature ok')
                    speed['Verify signature'] = self._timer.StopWatch(started)

        except Exception as exc:
            error = str(exc)

        return {
            'Error': error,
            'Checks': checks,
        }

    def _execute(self, validation: dict[str, Any], envelope: dict[str, Any], handler: Optional[Callable[[dict[str, Any]], Any]] = None) -> dict[str, Any]:
        if validation['Error']:
            return {
                'Result': 'Ignored, invalid envelope!'
            }

        if handler is None:
            return {
                'Result': 'No handler'
            }

        answer = handler(envelope)
        return {
            'Result': 'Executed',
            'Answer': answer,
        }

    def Handle(
        self,
        event: dict[str, Any],
        handler: Optional[Callable[[dict[str, Any]], Any]] = None,
        expected_to: Optional[str] = None,
        validator: Optional[Any] = None,
        public_key: Optional[str] = None,
        public_key_provider: Optional[Callable[[MSG], str]] = None,
        ignore_validation: bool = False,
    ) -> dict[str, Any]:
        LOG.Print(f'📮 MSG_RECEIVER.Handle():', event)

        UTILS.Require(event)
        envelope = self._parse(event)
        LOG.Print(f'📮 MSG_RECEIVER.Handle:', 'envelope=', envelope)

        if envelope == {}:
            return {
                'Result': 'Inbox is working :)'
            }

        speed: dict[str, Any] = {}
        started = self._timer.StartWatch()
        msg = MSG(envelope)

        validation = self._validate(
            msg=msg,
            speed=speed,
            expected_to=expected_to,
            validator=validator,
            public_key=public_key,
            public_key_provider=public_key_provider,
            ignore_validation=ignore_validation,
        )
        execution = self._execute(validation, envelope, handler)
        speed['Total handling'] = self._timer.StopWatch(started)

        output = execution if execution is not None else {}
        if isinstance(output, dict):
            output['Insights'] = {
                'Speed': speed,
                'Validation': validation,
                'Received': envelope,
            }

        if validation['Error']:
            output['Error'] = validation['Error']

        return output
