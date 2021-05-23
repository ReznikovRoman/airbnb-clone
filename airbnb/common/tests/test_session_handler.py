from django.test import SimpleTestCase
from django.contrib.sessions.backends.db import SessionStore

from ..services import create_name_with_prefix
from ..session_handler import SessionHandler


class SessionHandlerTests(SimpleTestCase):
    def test_init_object_success_with_given_prefix(self):
        """Test that instance's attributes are correct (if `session_prefix` is given)."""
        session = self.client.session
        keys_collector_name = 'keys_collector'
        prefix = 'prefix'
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        self.assertEqual(session_handler._session, session)
        self.assertEqual(session_handler._prefix, f"{prefix}_")
        self.assertEqual(session_handler._keys_collector_name, keys_collector_name)
        self.assertListEqual(session_handler._keys_collector, [])

    def test_init_object_success_without_prefix(self):
        """Test that instance's attributes are correct (if `session_prefix` is not given)."""
        session = self.client.session
        keys_collector_name = 'keys_collector'
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
        )

        self.assertEqual(session_handler._session, session)
        self.assertEqual(session_handler._prefix, '')
        self.assertEqual(session_handler._keys_collector_name, keys_collector_name)
        self.assertListEqual(session_handler._keys_collector, [])

    def test_init_object_success_with_existing_keys_collector(self):
        """Test that instance's attributes are correct (if `keys_collector` already exists)."""
        session: SessionStore = self.client.session
        keys_collector_name = 'keys_collector'

        existing_keys = ['key1', 'key2']
        session[keys_collector_name] = existing_keys

        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
        )

        self.assertEqual(session_handler._session, session)
        self.assertEqual(session_handler._prefix, '')
        self.assertEqual(session_handler._keys_collector_name, keys_collector_name)

        # item with the key `keys_collector_name` already exists in session, so `_keys_collector` is the same item
        self.assertListEqual(session_handler._keys_collector, existing_keys)

    def test_get_items_by_keys(self):
        """get_items_by_keys() returns dict with session data by the given `keys`."""
        session = self.client.session
        keys_collector_name = 'keys_collector'
        prefix = 'prefix'
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        test_items = {'key1': 1, 'key2': 2}
        session_handler.add_new_item(*list(test_items.items())[0])
        session_handler.add_new_item(*list(test_items.items())[1])

        items = session_handler.get_items_by_keys(keys=list(test_items.keys()))

        self.assertDictEqual(items, test_items)

    def test_add_new_key_to_collector(self):
        """add_new_key_to_collector() appends new `key` to the `_keys_collector`."""
        session = self.client.session
        keys_collector_name = 'keys_collector'
        prefix = 'prefix'
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        session_handler.add_new_key_to_collector(new_session_key='key1')

        self.assertListEqual(session_handler._keys_collector, ['key1'])

    def test_add_new_item_success(self):
        """add_new_item() creates new item in the session and adds item's key to the `_keys_collector`."""
        session = self.client.session
        keys_collector_name = 'keys_collector'
        prefix = 'prefix'
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        new_key1 = 'key1'
        new_value1 = 1
        new_key1_with_prefix = create_name_with_prefix(new_key1, prefix)
        session_handler.add_new_item(new_key=new_key1, new_value=new_value1)

        self.assertEqual(session_handler._session.get(new_key1_with_prefix), new_value1)
        self.assertListEqual(session_handler._keys_collector, [new_key1_with_prefix])

    def test_create_or_update_items(self):
        """create_or_update_items() creates or updates items by the given keys and values from `data`."""
        session = self.client.session
        keys_collector_name = 'keys_collector'
        prefix = 'prefix'
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        key1 = 'key1'
        value1 = 1
        key1_with_prefix = create_name_with_prefix(key1, prefix)
        session_handler.add_new_item(new_key=key1, new_value=value1)

        new_key = 'key2'
        new_key_with_prefix = create_name_with_prefix(new_key, prefix)
        session_handler.create_or_update_items(data={key1: 2, new_key: 3})

        self.assertEqual(session_handler._session.get(key1_with_prefix), 2)
        self.assertEqual(session_handler._session.get(new_key_with_prefix), 3)
        self.assertListEqual(session_handler._keys_collector, [key1_with_prefix, new_key_with_prefix])

    def test_delete_given_keys(self):
        """delete_given_keys() deletes given `keys_to_delete` from the session and from the `_keys_collector`."""
        session = self.client.session
        keys_collector_name = 'keys_collector'
        prefix = 'prefix'
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        key1 = 'key1'
        value1 = 1
        key1_with_prefix = create_name_with_prefix(key1, prefix)
        session_handler.add_new_item(new_key=key1, new_value=value1)

        key2 = 'key2'
        value2 = 2
        key2_with_prefix = create_name_with_prefix(key2, prefix)
        session_handler.add_new_item(new_key=key2, new_value=value2)

        session_handler.delete_given_keys(keys_to_delete=[key1_with_prefix, 'invalid_key'])

        self.assertIsNone(session_handler._session.get(key1_with_prefix, None))
        self.assertListEqual(session_handler._keys_collector, [key2_with_prefix])

    def test_flush_keys_collector(self):
        """flush_keys_collector() deletes all items from session with `_keys_collector` keys."""
        session = self.client.session
        keys_collector_name = 'keys_collector'
        prefix = 'prefix'
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        key1 = 'key1'
        value1 = 1
        key1_with_prefix = create_name_with_prefix(key1, prefix)
        session_handler.add_new_item(new_key=key1, new_value=value1)

        key2 = 'key2'
        value2 = 2
        key2_with_prefix = create_name_with_prefix(key2, prefix)
        session_handler.add_new_item(new_key=key2, new_value=value2)

        session_handler.flush_keys_collector()

        self.assertIsNone(session_handler._session.get(key1_with_prefix, None))
        self.assertIsNone(session_handler._session.get(key2_with_prefix, None))
        self.assertListEqual(session_handler._keys_collector, [])

    def test_get_session(self):
        """get_session() returns `_session`."""
        session = self.client.session
        keys_collector_name = 'keys_collector'
        prefix = 'prefix'
        session_handler = SessionHandler(
            session=session,
            keys_collector_name=keys_collector_name,
            session_prefix=prefix,
        )

        self.assertEqual(session_handler.get_session(), session)
