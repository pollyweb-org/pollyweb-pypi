# 📚 MSG - compatibility adapter over PW_DOMAIN.MSG
#
# Keep legacy call signatures used across this repo while delegating the
# implementation to pollyweb-domain.
from __future__ import annotations

from PW_DOMAIN import MSG as _MSG


class MSG(_MSG):
    """Compatibility wrapper around PW_DOMAIN.MSG."""

    def VerifySignature(self, publicKey: str = None):
        """Throws an exception if the Hash or Signature dont match the public key.

        Usage:
        * self.VerifySignature(publicKey) -> offline validation.
        * self.VerifySignature() -> online validation, gets the remote DKIM.
        """
        from PW import PW

        if publicKey is None:
            domain = PW.DOMAIN(name=self.RequireFrom())
            publicKey = domain.GetPublicKey()

        dkim = PW.BEHAVIORS().SYNCAPI().DKIM()
        return super().VerifySignature(
            publicKey=publicKey,
            validator=dkim)

    def MatchSubject(
        self,
        subject: str,
        msg: str = None,
        ignoreTo: bool = False,
        expectedTo: str = None
    ):
        """Raises an exception if the subject does not match."""
        if msg is None:
            msg = 'Unexpected subject in the message.'
        from PW import PW

        if not ignoreTo and expectedTo is None:
            expectedTo = PW.CONFIG().RequireDomain()

        return super().MatchSubject(
            subject=subject,
            msg=msg,
            ignoreTo=ignoreTo,
            expectedTo=expectedTo)


__all__ = ['MSG']
