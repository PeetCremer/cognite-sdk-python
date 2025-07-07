from __future__ import annotations

import functools
import random
import socket
import time
from collections.abc import Callable, Iterable, MutableMapping
from http import cookiejar
from typing import Any, Literal

import httpx
import urllib3

from cognite.client.config import global_config
from cognite.client.exceptions import CogniteConnectionError, CogniteConnectionRefused, CogniteReadTimeout
from cognite.client.utils.useful_types import SupportsRead


class BlockAll(cookiejar.CookiePolicy):
    def no(*args: Any, **kwargs: Any) -> Literal[False]:
        return False

    return_ok = set_ok = domain_return_ok = path_return_ok = no
    netscape = True
    rfc2965 = hide_cookie2 = False


@functools.lru_cache(1)
def get_global_httpx_client() -> httpx.Client:
    # Configure timeout - httpx uses a different timeout structure
    timeout = httpx.Timeout(
        connect=30.0,  # connection timeout
        read=30.0,     # read timeout
        write=30.0,    # write timeout
        pool=30.0      # pool timeout
    )
    
    # Configure limits for connection pooling
    limits = httpx.Limits(
        max_keepalive_connections=global_config.max_connection_pool_size,
        max_connections=global_config.max_connection_pool_size * 2,
        keepalive_expiry=30.0
    )
    
    # Handle proxies - httpx expects mounts or proxy configuration differently
    proxies = None
    if global_config.proxies:
        proxies = global_config.proxies
    
    client = httpx.Client(
        timeout=timeout,
        limits=limits,
        verify=not global_config.disable_ssl,
        proxies=proxies,
        http2=False,  # Can be enabled later if needed
    )
    
    # Note: httpx doesn't use the same cookie policy system as requests
    # For now, we'll handle cookie blocking at the application level if needed
    
    return client


# Keep the old function name for backward compatibility during migration
get_global_requests_session = get_global_httpx_client


class HTTPClientConfig:
    def __init__(
        self,
        status_codes_to_retry: set[int],
        backoff_factor: float,
        max_backoff_seconds: int,
        max_retries_total: int,
        max_retries_status: int,
        max_retries_read: int,
        max_retries_connect: int,
    ) -> None:
        self.status_codes_to_retry = status_codes_to_retry
        self.backoff_factor = backoff_factor
        self.max_backoff_seconds = max_backoff_seconds
        self.max_retries_total = max_retries_total
        self.max_retries_status = max_retries_status
        self.max_retries_read = max_retries_read
        self.max_retries_connect = max_retries_connect


class _RetryTracker:
    def __init__(self, config: HTTPClientConfig) -> None:
        self.config = config
        self.status = 0
        self.read = 0
        self.connect = 0

    @property
    def total(self) -> int:
        return self.status + self.read + self.connect

    def _max_backoff_and_jitter(self, t: int) -> int:
        return int(min(t, self.config.max_backoff_seconds) * random.uniform(0, 1.0))

    def get_backoff_time(self) -> int:
        backoff_time = self.config.backoff_factor * (2**self.total)
        backoff_time_adjusted = self._max_backoff_and_jitter(backoff_time)
        return backoff_time_adjusted

    def should_retry(self, status_code: int | None, is_auto_retryable: bool = False) -> bool:
        if self.total >= self.config.max_retries_total:
            return False
        if self.status > 0 and self.status >= self.config.max_retries_status:
            return False
        if self.read > 0 and self.read >= self.config.max_retries_read:
            return False
        if self.connect > 0 and self.connect >= self.config.max_retries_connect:
            return False
        if status_code and status_code not in self.config.status_codes_to_retry and not is_auto_retryable:
            return False
        return True


class HTTPClient:
    def __init__(
        self,
        config: HTTPClientConfig,
        session: httpx.Client,
        refresh_auth_header: Callable[[MutableMapping[str, Any]], None],
        retry_tracker_factory: Callable[[HTTPClientConfig], _RetryTracker] = _RetryTracker,
    ) -> None:
        self.session = session
        self.config = config
        self.refresh_auth_header = refresh_auth_header
        self.retry_tracker_factory = retry_tracker_factory  # needed for tests

    def request(
        self,
        method: str,
        url: str,
        data: str | bytes | Iterable[bytes] | SupportsRead | None = None,
        headers: MutableMapping[str, Any] | None = None,
        timeout: float | None = None,
        params: dict[str, Any] | str | bytes | None = None,
        stream: bool | None = None,
        allow_redirects: bool = False,
    ) -> httpx.Response:
        retry_tracker = self.retry_tracker_factory(self.config)
        accepts_json = (headers or {}).get("accept") == "application/json"
        is_auto_retryable = False
        while True:
            try:
                res = self._do_request(
                    method=method,
                    url=url,
                    data=data,
                    headers=headers,
                    timeout=timeout,
                    params=params,
                    stream=stream,
                    allow_redirects=allow_redirects,
                )
                if accepts_json:
                    # Cache .json() return value in order to avoid redecoding JSON if called multiple times
                    res.json = functools.lru_cache(maxsize=1)(res.json)  # type: ignore[assignment]
                    try:
                        is_auto_retryable = res.json().get("error", {}).get("isAutoRetryable", False)
                    except Exception:
                        # if the response is not JSON or it doesn't conform to the api design guide,
                        # we assume it's not auto-retryable
                        pass

                retry_tracker.status += 1
                if not retry_tracker.should_retry(status_code=res.status_code, is_auto_retryable=is_auto_retryable):
                    return res

            except CogniteReadTimeout as e:
                retry_tracker.read += 1
                if not retry_tracker.should_retry(status_code=None, is_auto_retryable=True):
                    raise e
            except CogniteConnectionError as e:
                retry_tracker.connect += 1
                if not retry_tracker.should_retry(status_code=None, is_auto_retryable=True):
                    raise e

            # During a backoff loop, our credentials might expire, so we check and maybe refresh:
            time.sleep(retry_tracker.get_backoff_time())
            if headers is not None:
                # TODO: Refactoring needed to make this "prettier"
                self.refresh_auth_header(headers)

    def _do_request(
        self,
        method: str,
        url: str,
        data: str | bytes | Iterable[bytes] | SupportsRead | None = None,
        headers: MutableMapping[str, Any] | None = None,
        timeout: float | None = None,
        params: dict[str, Any] | str | bytes | None = None,
        stream: bool | None = None,
        allow_redirects: bool = False,
    ) -> httpx.Response:
        """httpx has a different exception hierarchy compared to requests/urllib3.

        We need to map httpx exceptions to our custom Cognite exceptions to maintain
        compatibility with existing code.
        """
        try:
            # Convert timeout to httpx format if provided
            httpx_timeout = None
            if timeout is not None:
                httpx_timeout = httpx.Timeout(timeout)
            
            # Handle data parameter - httpx uses different parameter names
            request_kwargs = {
                "method": method,
                "url": url,
                "headers": headers,
                "timeout": httpx_timeout,
                "params": params,
                "follow_redirects": allow_redirects,
            }
            
            # Map data to appropriate httpx parameter
            if data is not None:
                if isinstance(data, (str, bytes)):
                    request_kwargs["content"] = data
                else:
                    # For other types (file-like objects, iterables), pass as-is
                    # httpx should handle these appropriately
                    request_kwargs["content"] = data
            
            res = self.session.request(**request_kwargs)
            return res
        except Exception as e:
            # Map httpx exceptions to Cognite exceptions
            if self._any_exception_in_context_isinstance(
                e, (socket.timeout, httpx.ReadTimeout, httpx.TimeoutException)
            ):
                raise CogniteReadTimeout from e
            if self._any_exception_in_context_isinstance(
                e,
                (
                    ConnectionError,
                    httpx.ConnectError,
                    httpx.NetworkError,
                ),
            ):
                if self._any_exception_in_context_isinstance(e, ConnectionRefusedError):
                    raise CogniteConnectionRefused from e
                raise CogniteConnectionError from e
            raise e

    @classmethod
    def _any_exception_in_context_isinstance(
        cls, exc: BaseException, exc_types: tuple[type[BaseException], ...] | type[BaseException]
    ) -> bool:
        """httpx exceptions have different context than requests exceptions.
        
        This method handles the exception context checking for both httpx and legacy requests patterns.
        """
        if isinstance(exc, exc_types):
            return True
        if exc.__context__ is None:
            return False
        return cls._any_exception_in_context_isinstance(exc.__context__, exc_types)
