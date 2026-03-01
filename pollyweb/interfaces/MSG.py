# 📚 MSG

from __future__ import annotations

import json
from typing import Any, Optional, cast
from urllib import request

from ..utils import LOG
from ..utils import STRUCT
from ..utils import UTILS


class MSG(STRUCT):
    ''' 👉 Structure of a message: { Header, Body, Hash, Signature }.
    * https://quip.com/NiUhAQKbj7zi

    Usage:
    * MSG({}) -> ${}
    * MSG(${}) -> ${}

    Example:
    {
        "Header": {
            "Code": "pollyweb.org/msg",
            "Version": "1",
            "From": "any-sender.com",
            "To": "any-receiver.com",
            "Subject": "AnyMethod",
            "Correlation": "125a5c75-cb72-43d2-9695-37026dfcaa48",
            "SentAt": "2018-12-10T13:45:00.000Z"
        },
        "Body": {}
        "Hash": "..."
        "Signature": <{ Header, Body } signed>
    }
    '''

    def __init__(self, event):
        LOG.Print(f'💌 MSG.__init__()', 'event=', event)

        if event is None:
            LOG.RaiseValidationException(
                f'Messages cannot be instanciated with None!', event)

        # Verify the input.
        UTILS.AssertIsAnyType(event, [dict, STRUCT, MSG])

        # Get the internal object of a STRUCT.
        if isinstance(event, STRUCT):
            event = event.Obj()

        # parse eventBridge payloads.
        if 'detail-type' in event \
        and 'source' in event \
        and 'detail' in event:
            event = event['detail']

        # Transform into a native object.
        try:
            event = json.loads(json.dumps(event))
        except Exception as exc:
            LOG.RaiseException(
                f'Failed to convert event to json! '
                f'Confirm if there is not a complex object inside of event={event}')

        # instanciate the parent class: STRUCT
        super().__init__(event)

        # create an empty header/body, if one is missing.
        self.Default('Header', {})
        self.Default('Body', {})

        # print in the beggining of all handlers.
        LOG.Print(f'💌 MSG:', 'after marshelling', self)

        # set the Body as the root for the Att() method.
        self.SetAttRoot('Body')

    def Envelope(self) -> Any:
        ''' 👉 Returns the internal envelope object.
        * ${Header:h, Body:b}.Envelope() -> {Header:h, Body:b}
        '''
        return super().Obj()

    def RequireHeader(self, header: Any = None) -> STRUCT:
        ''' 👉 Gets or sets the Header.
        * ${Header:h, Body:b}.Header() -> $h (gets)
        * ${}.Header() -> Exception! (requires for get)
        * m=${}; m.Header(h); m.Envelope() -> ${Header:h} (sets)
        * m=${}; m.Header($h); m.Envelope() -> ${Header:h} (unboxes structs on set)
        '''
        ret = super().RequireStruct('Header', set=header)
        super().MoveAtt('Header', 0)
        return ret

    def RequireSubject(self, subject: Optional[str] = None) -> str:
        ''' 👉 Gets or sets the Subject.
        * ${Header:{Subject:x}}.Subject() -> 'x' (getter)
        * m=${Header:{}}; m.Subject(x); m.Envelope() -> {Header:{Subject:x}} (setter)
        * m=${}; m.Subject(x); -> Untested behaviour!
        '''
        header = self.RequireHeader()
        if subject is not None:
            return header.RequireStr('Subject', set=subject)
        return header.RequireStr('Subject')

    def RequireFrom(self, set: Optional[str] = None, default: Optional[str] = None) -> str:
        ''' 👉 Gets or sets the From. '''

        header = self.RequireHeader()

        if default is not None:
            if header.IsMissingOrEmpty('From'):
                set = default

        if set is not None:
            if set == header.GetAtt('To'):
                old = header.GetAtt('From')
                LOG.RaiseValidationException(
                    f"Invalid operation, setting From==To! From=({old}->{set}), Subject={self.RequireSubject()}.")

            header.SetAtt('From', set=set)
            header.MoveAtt('From', new_position=0)

        return header.RequireStr(att='From')

    def RequireTo(self, set: Optional[str] = None) -> str:
        ''' 👉 Gets or sets the To. '''
        header = self.RequireHeader()
        if set is not None:
            return header.RequireStr('To', set=set)
        return header.RequireStr('To')

    def GetTimestamp(self, set: Optional[str] = None) -> str:
        ''' 👉 Gets or sets the Timestamp. '''
        header = self.RequireHeader()
        if set is not None:
            return header.RequireTimestamp('SentAt', set=set)
        return header.RequireTimestamp('SentAt')

    def RequireCorrelation(self, set: Optional[str] = None) -> str:
        ''' 👉 Gets or sets the Correlation. '''
        header = self.RequireHeader()
        if set is not None:
            return header.RequireUUID('Correlation', set=set)
        return header.RequireUUID('Correlation')

    def Body(self, body=None) -> STRUCT:
        ''' 👉 Updates or returns a copy of the body.

        Getter:
        * ${Body:x}.Body() -> $x
        * ${}.Body() -> ${} (safe gatter)
        * m=${Body:{x:1}}; a=m.Body(); a.Att(x,2); b=m.Body(); f'{a.Att(x)},{b.Att(x)}' -> '2,1'  (safe copy)

        Setter:
        * m=${}; m.Body(1); m.Envelope() -> {Body:1} (safe setter)
        * m=${Body:1}; m.Body(2); m.Envelope() -> {Body:2} (replace)
        * m=${Body:1}; m.Body($2); m.Envelope() -> {Body:2} (unboxing)
        '''
        envelope = self.Envelope()

        # setter
        if body:
            envelope['Body'] = STRUCT.Unstruct(body)

        # existing getter, returns a copy
        if 'Body' in envelope and envelope['Body'] != '':
            ret = self.Copy().GetStruct('Body')

            if 'Header' in self._obj:
                super().MoveAtt('Header', 0)

            return ret

        # empty getter
        return STRUCT({})

    def RequireSignature(self, set: Optional[str] = None) -> str:
        ''' 👉 Gets or sets the Signature. '''
        if set is not None:
            return self.RequireStr('Signature', set=set)
        return self.RequireStr('Signature')

    def RequireHash(self, set: Optional[str] = None) -> str:
        ''' 👉 Gets or sets the Hash. '''
        if set is not None:
            return self.RequireStr('Hash', set=set)
        return self.RequireStr('Hash')

    def MatchMsg(self, msg: "MSG"):
        ''' 👉 Verifies if messsages have the same hash. '''
        UTILS.AssertEqual(
            expect=self.Canonicalize(),
            given=msg.Canonicalize())

    @classmethod
    def Wrap(cls, to: str, subject: str, body: Any = None) -> "MSG":
        ''' 👉 Returns a stamped message, with header and body.
        * Wrap(to, subject, body) -> ${Header: {To, Subject, SentAt, Correlation}, Body}
        '''

        UTILS.RequireArgs([to, subject])
        UTILS.AssertIsType(to, str)
        UTILS.AssertIsType(subject, str)

        ret = MSG({
            '🤝': 'pollyweb.org/MSG:1.0',
            'Header': {
                'To': to,
                'Subject': subject
            },
            'Body': STRUCT.Unstruct(body)
        })

        ret.Stamp()
        return ret

    def Stamp(self):
        ''' 👉 Adds correlation and timestamp, if they don't exist.
        * ${Header:*}.Stamp() -> ${Header:{*, SentAt, Correlation}}
        '''

        self.GetAtt('🤝', default='pollyweb.org/MSG:1.0')
        self.GetAtt('Header', default={})
        self.GetAtt('Body', default={})
        self.RequireHeader().DefaultGuid('Correlation')
        self.RequireHeader().DefaultTimestamp('SentAt')
        self.RequireHeader().GetAtt('Code', 'pollyweb.org/msg')
        self.RequireHeader().GetAtt('Version', '1')

    def Canonicalize(self) -> str:
        ''' 👉️ Removes the signature and hash, then removes the spaces and new lines.
        * Source: https://bobbyhadz.com/blog/python-json-dumps-no-spaces
        * ${Header:*, Body:*, Signature, Hash}.Canonicalize() -> '{Header:*,Body:*}'
        '''
        copy = self.Copy()
        cast(Any, copy).RemoveAtt('Signature')
        cast(Any, copy).RemoveAtt('Hash')
        return copy.Canonicalize()

    def VerifyHeader(self):
        ''' 👉 Throws an exception if any of the header attributes are missing.
        * ${Header:{From,To,Subject,SentAt,Correlation, *}, *} -> OK
        * ${Header:{From,To,Subject,SentAt,Correlation}, Body, *} -> OK
        * anything else -> Exception!
        '''

        msg = self
        msg.RequireTo()
        msg.RequireSubject()
        msg.RequireFrom()
        msg.GetTimestamp()
        msg.RequireCorrelation()

        if msg.RequireFrom() == msg.RequireTo():
            LOG.RaiseValidationException(
                f'Any reason for sending yourself messages, {msg.RequireFrom()}?')

        if 'graph' in msg.RequireFrom() and 'vault' in msg.RequireTo():
            LOG.RaiseValidationException(
                f'Graphs sending messages to vaults???')

        if self.Body().ContainsAtt('ItemVersion'):
            LOG.RaiseValidationException('ItemVersion should not be exposed!')

    def VerifySignature(self, publicKey: Optional[str] = None, validator: Optional[Any] = None):
        ''' 👉 Throws an exception if the Hash or Signature dont match the public key.

        Usage:
        * self.VerifySignature(publicKey, validator) -> offline validation.
        * validator can be a callable or an object with ValidateSignature().
        '''
        if publicKey is None:
            raise ValueError('publicKey is required to verify the signature.')
        if validator is None:
            raise ValueError('validator is required to verify the signature.')

        if hasattr(validator, 'ValidateSignature'):
            validator_result = validator.ValidateSignature(
                text=self.Canonicalize(),
                hash=self.RequireHash(),
                publicKey=publicKey,
                signature=self.RequireSignature())
        else:
            validator_result = validator(
                text=self.Canonicalize(),
                hash=self.RequireHash(),
                publicKey=publicKey,
                signature=self.RequireSignature())

        def _get_value(result, key: str):
            if hasattr(result, key):
                return getattr(result, key)()
            if isinstance(result, dict):
                return result.get(key)
            return None

        expected = _get_value(validator_result, 'Hash')
        if expected is None and isinstance(validator_result, dict):
            expected = validator_result.get('hash')

        received = self.RequireHash()

        isHashValid = (expected == received)
        if not isHashValid:
            LOG.RaiseException(
                f'Wrong hash: expected [{expected}] but received [{received}]!')

        isVerified = _get_value(validator_result, 'IsVerified')
        if isVerified is None and isinstance(validator_result, dict):
            isVerified = validator_result.get('isVerified')

        if not isVerified:
            LOG.RaiseException('Invalid signature!')

    def Sign(self, hash: str, signature: str):
        ''' 👉 Adds the signature and the hash to the message.
        This needs to be done in 2 steps: a) generate the signature, b) add to the message.'''
        self.RequireSignature(signature)
        self.RequireHash(hash)

    def Send(self) -> STRUCT:
        '''👉 Sends the message to the Inbox endpoint of the destination Domain.'''
        LOG.Print(f' MSG.Send(to={self.RequireTo()}, subject={self.RequireSubject()})')

        # Verify if it contains all required fields.
        self.VerifyHeader()
        self.RequireSignature()
        self.RequireHash()

        # Send it.
        to = self.RequireTo()
        url = f'https://pollyweb.{to}/inbox'

        data = bytes(json.dumps(self.Obj()), encoding='utf-8')
        req = request.Request(url=url, method='POST', data=data)
        req.add_header('Content-Type', 'application/json')
        resp = request.urlopen(req)

        charset = resp.info().get_content_charset()
        if charset is None:
            charset = 'utf-8'
        response = resp.read().decode(charset)

        # Try to convert the string into an object.
        try:
            obj = json.loads(response)
            if isinstance(obj, str):
                ret = response
            else:
                ret = obj
        except Exception:
            ret = response

        # Verify if a dictionary was returned.
        if type(ret).__name__ == 'dict':
            return ret
        else:
            LOG.RaiseValidationException(
                'Not authorized: domains must return dictionaries!',
                f'Received= {type(ret).__name__}', ret)

    def MatchSubject(self, subject: str, msg: Optional[str] = None, ignoreTo: bool = False, expectedTo: Optional[str] = None):
        '''👉 Raises an exception if the subject does not match.'''

        if msg is None:
            msg = f'Unexpected subject in the message.'

        UTILS.AssertEqual(
            given=self.RequireSubject(),
            expect=subject,
            msg=msg)

        if ignoreTo is not True:
            if expectedTo is None:
                raise ValueError('expectedTo is required when ignoreTo is False.')
            UTILS.AssertEqual(
                given=self.RequireTo(),
                expect=expectedTo)

    def RequireCode(self, att: str) -> str:
        code = self.RequireStr(att)
        from .CODE import CODE
        CODE.Verify(code)
        return code
