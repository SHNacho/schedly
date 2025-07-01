import asyncio
import pprint
from datetime import datetime
from datetime import timedelta

import httpx

from config import load_config

config = load_config()


class CalendlyClient:
    def __init__(self):
        self.personal_token = config["calendly"]["personal_token"]
        self.base_url = "https://api.calendly.com"

        with httpx.Client() as client:
            user = self.get_current_user(client)

        self.user_uri = user["resource"]["uri"]
        self.user_uuid = self.user_uri.split("/")[-1]
        self.current_organization = user["resource"]["current_organization"]
        self.org_uuid = self.current_organization.split("/")[-1]

    def get_current_user(self, client: httpx.Client) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.personal_token}",
        }

        response = client.get(
            f"{self.base_url}/users/me",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def aget_current_user(self, client: httpx.AsyncClient) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.personal_token}",
        }

        response = await client.get(
            f"{self.base_url}/users/me",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def aget_scheduled_events(self, client: httpx.AsyncClient) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.personal_token}",
        }
        params = {"organization": self.current_organization}

        response = await client.get(
            f"{self.base_url}/scheduled_events",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def aget_event_types(self, client: httpx.Client) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.personal_token}",
        }
        params = {"organization": self.current_organization}

        response = await client.get(
            f"{self.base_url}/event_types",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


async def main():
    calendly = CalendlyClient()

    async with httpx.AsyncClient() as client:
        response = await calendly.aget_event_types(client)
    pprint.pp(response)
    return response


if __name__ == "__main__":

    asyncio.run(main())
