import json
from typing import List

import requests


ENDPOINT_URL = "https://esi.evetech.net/latest/"

ACCEPT_JSON_HEADER = {"accept": "application/json"}


def get(endpoint: str, header=ACCEPT_JSON_HEADER) -> requests.Response:
    return _api_call(requests.get, endpoint, header)

def post(endpoint: str, data: dict = {}, header=ACCEPT_JSON_HEADER) -> requests.Response:
    return _api_call(requests.post, endpoint, header, data=data)

def delete(endpoint: str, header=ACCEPT_JSON_HEADER) -> requests.Response:
    return _api_call(requests.delete, endpoint, header)


def _api_call(method, endpoint: str, header: dict, **kwargs) -> requests.Response:
    # Remove the backend url first (if present) so it's never doubled
    endpoint = endpoint.replace(ENDPOINT_URL, "")
    resp = method(
        url=url_join(ENDPOINT_URL, endpoint),
        headers=header,
        **kwargs,
    )
    # print("URL:", url_join(ENDPOINT_URL, endpoint))
    _check_status_code(resp, endpoint, method, header)
    return resp


def _check_status_code(resp: requests.Response, endpoint: str, method, header: dict):
    if resp.status_code < 200 or resp.status_code > 299:
        print(resp.content.decode())
        print(f"Something went wrong. Status Code: {resp.status_code}")
        print(f"Requested endpoint: {endpoint}")
        print(f"Method: {method}")
        print(f"Header: {header}")


def url_join(base: str, *args: List[str]) -> str:
    url = base.strip("/")
    for arg in args:
        url += "/" + arg.strip("/")
    # If the last arg ended with a '/', add it again.
    if len(args) > 0 and args[-1].endswith("/"):
        url += "/"
    return url


def response_to_json(response: requests.Response) -> dict:
    return json.loads(response.content.decode())


def build_query_args(**kwargs) -> str:
    query_args = "?"
    for i, (key, value) in enumerate(kwargs.items()):
        query_args += f"{key}={value}"
        if i != len(kwargs)-1:
            query_args += "&"
    return query_args