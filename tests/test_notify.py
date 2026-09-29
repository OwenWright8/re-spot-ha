"""Notification behavior checks without requiring a running Home Assistant."""
import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
import unittest

class HomeAssistantError(Exception):
    pass

class NotificationTests(unittest.TestCase):
    def test_offline_rejected_online_dispatched(self):
        source = Path(__file__).resolve().parents[1] / 'custom_components/respot/notify.py'
        tree = ast.parse(source.read_text(encoding='utf-8'))
        method = next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == 'async_send_message')
        namespace = {'HomeAssistantError': HomeAssistantError, 'EVENT_NOTIFY': 'respot_notify'}
        exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), 'exec'), namespace)
        events = []
        obj = SimpleNamespace(_spot=SimpleNamespace(online=False, spot_id='spot'), hass=SimpleNamespace(bus=SimpleNamespace(async_fire=lambda *args: events.append(args))))
        with self.assertRaises(HomeAssistantError):
            asyncio.run(namespace['async_send_message'](obj, 'Hello'))
        self.assertEqual(events, [])
        obj._spot.online = True
        asyncio.run(namespace['async_send_message'](obj, 'Hello', 'Title'))
        self.assertEqual(events, [('respot_notify', {'spot_id': 'spot', 'message': 'Hello', 'title': 'Title'})])

if __name__ == '__main__':
    unittest.main()
