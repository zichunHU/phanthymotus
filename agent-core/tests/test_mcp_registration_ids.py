import asyncio
import unittest
from unittest.mock import patch

from api import mcp_manage


class TestMCPRegistrationIDs(unittest.IsolatedAsyncioTestCase):
    async def test_two_services_registered_in_one_second_get_distinct_ids(self):
        entries = []

        def save(new_entries):
            entries[:] = new_entries

        async def ping(_mcp_id):
            pass

        requests = (
            mcp_manage.MCPAddRequest(name="3D Pose", url="http://localhost:15713/mcp"),
            mcp_manage.MCPAddRequest(name="vision2pose", url="http://localhost:15712/mcp"),
        )
        with patch("time.time", return_value=1_795_154_481), patch.object(
            mcp_manage, "_get_mcp_list", side_effect=lambda: list(entries)
        ), patch.object(mcp_manage, "_save_mcp_list", side_effect=save), patch.object(
            mcp_manage, "_do_ping", new=ping
        ):
            first, second = await asyncio.gather(*(mcp_manage.mcp_add(req) for req in requests))
            self.assertNotEqual(first["data"]["id"], second["data"]["id"])
            repeated = await mcp_manage.mcp_add(requests[0])
            self.assertEqual(repeated["data"]["id"], first["data"]["id"])
            self.assertEqual(len(entries), 2)


if __name__ == "__main__":
    unittest.main()
