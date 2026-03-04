"""GraphQL client module."""

import requests


class GraphQLClient:
    def __init__(self, endpoint: str, timeout: int = 30):
        self.endpoint = endpoint
        self.timeout = timeout

    def query(self, query: str, variables: dict | None = None) -> dict:
        payload = {"query": query, "variables": variables or {}}
        response = requests.post(self.endpoint, json=payload, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
