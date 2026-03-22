"""Internal HTTPS transport helpers for PollyWeb message delivery."""

import http.client
import io
import threading
import urllib.error
from urllib.parse import urlsplit


class _HttpsConnectionPool:
    """Keep a small cache of HTTPS connections keyed by destination host."""

    def __init__(self):
        """Initialize the empty connection cache."""

        self._connections: dict[tuple[str, int], http.client.HTTPSConnection] = {}
        self._lock = threading.Lock()

    def _get_connection(
        self,
        host: str,
        port: int,
        *,
        timeout: float
    ) -> http.client.HTTPSConnection:
        """Return a cached HTTPS connection, creating one when needed."""

        cache_key = (host, port)

        with self._lock:
            connection = self._connections.get(cache_key)
            if connection is not None:
                return connection

            # Reuse one connection per destination host so repeated sends can
            # avoid a fresh TCP/TLS handshake when the server keeps the socket
            # alive between requests.
            connection = http.client.HTTPSConnection(
                host,
                port = port,
                timeout = timeout)
            self._connections[cache_key] = connection
            return connection

    def _drop_connection(
        self,
        host: str,
        port: int
    ) -> None:
        """Close and remove one cached connection when it becomes unusable."""

        cache_key = (host, port)

        with self._lock:
            connection = self._connections.pop(cache_key, None)

        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass

    def close(self) -> None:
        """Close every cached connection and clear the pool."""

        with self._lock:
            connections = list(self._connections.values())
            self._connections.clear()

        for connection in connections:
            try:
                connection.close()
            except Exception:
                pass

    def post(
        self,
        url: str,
        body: bytes,
        *,
        headers: dict[str, str] | None = None,
        timeout: float = 10.0
    ) -> bytes:
        """POST *body* to *url* and return the raw response bytes."""

        request_headers = {
            "Content-Type": "application/json",
        }
        if headers:
            request_headers.update(headers)

        parsed = urlsplit(url)
        if parsed.scheme != "https":
            raise ValueError("PollyWeb transport only supports https URLs")
        if not parsed.hostname:
            raise ValueError("PollyWeb transport requires a hostname")

        host = parsed.hostname
        port = parsed.port or 443
        path = parsed.path or "/"
        if parsed.query:
            path = f"{path}?{parsed.query}"

        connection = self._get_connection(
            host,
            port,
            timeout = timeout)

        try:
            connection.request(
                "POST",
                path,
                body = body,
                headers = request_headers)
            response = connection.getresponse()
            raw = response.read()

            # Drop sockets the server marked for closure so the next send
            # starts with a fresh connection instead of reusing a dead one.
            if response.will_close:
                self._drop_connection(host, port)

            if response.status >= 400:
                raise urllib.error.HTTPError(
                    url,
                    response.status,
                    response.reason,
                    response.headers,
                    io.BytesIO(raw))

            return raw
        except (
            OSError,
            http.client.HTTPException,
        ):
            self._drop_connection(host, port)
            raise


_HTTPS_CONNECTION_POOL = _HttpsConnectionPool()


def post_json_bytes(
    url: str,
    body: bytes,
    *,
    timeout: float = 10.0
) -> bytes:
    """POST JSON bytes to a PollyWeb HTTPS endpoint and return the response body."""

    return _HTTPS_CONNECTION_POOL.post(
        url,
        body,
        timeout = timeout)


def close_cached_https_connections() -> None:
    """Close all cached PollyWeb HTTPS connections."""

    _HTTPS_CONNECTION_POOL.close()
