
import requests.adapters
import requests.packages.urllib3.util.retry


# should be __copy_paster__ = ... :-)
__author__ = "Jérémie Lumbroso <lumbroso@cs.princeton.edu>"

__all__ = [
    "get",
]


# all of this is thx to:
# https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/

DEFAULT_RETRY = 3

# in seconds, (connect timeout, read timeout)
DEFAULT_TIMEOUT = (3.05, 15)


class TimeoutHTTPAdapter(requests.adapters.HTTPAdapter):

    def __init__(self, *args, **kwargs):
        self.timeout = DEFAULT_TIMEOUT
        if "timeout" in kwargs:
            self.timeout = kwargs["timeout"]
            del kwargs["timeout"]
        super().__init__(*args, **kwargs)

    def send(self, request, **kwargs):
        timeout = kwargs.get("timeout")
        if timeout is None:
            kwargs["timeout"] = self.timeout
        return super().send(request, **kwargs)


retry_strategy = requests.packages.urllib3.util.retry.Retry(
    total=DEFAULT_RETRY,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"],
)

adapter = TimeoutHTTPAdapter(max_retries=retry_strategy)

session = requests.Session()

session.mount("https://", adapter)
session.mount("http://", adapter)


def get(*args, **kwargs):
    return session.get(*args, **kwargs)
