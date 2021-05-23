from typing import List, Optional, Union, Tuple, Set
from contextlib import suppress

from django.contrib.sessions.backends.base import SessionBase

from .services import create_name_with_prefix


class SessionHandler:
    """Basic session handler.

    Attributes:
        session (SessionBase): current session
        keys_collector_name (str): name of the session variable that stores all app-specific keys
        session_prefix (Optional[str]): optional prefix that all keys will start with (<prefix>_<key>)
    """
    def __init__(self, session: SessionBase, keys_collector_name: str, session_prefix: Optional[str] = None):
        self._session = session
        self._prefix = f"{session_prefix}_" if session_prefix else ''
        self._keys_collector_name = keys_collector_name

        if self._session.get(keys_collector_name, None) is None:
            self._session[keys_collector_name] = set()

        self._keys_collector: Set[str] = self._session.get(keys_collector_name)

    def get_items_by_keys(self, keys: Union[List[str], Tuple[str]]) -> dict:
        return {key: self._session.get(create_name_with_prefix(key, self._prefix), None)
                for key in keys}

    def add_new_key_to_collector(self, new_session_key: str) -> None:
        self._keys_collector.add(new_session_key)

    def add_new_item(self, new_key: str, new_value) -> None:
        session_key = create_name_with_prefix(new_key, self._prefix)
        with suppress(TypeError):
            self._session[session_key] = new_value
            self.add_new_key_to_collector(session_key)

    def create_or_update_items(self, data: dict) -> None:
        for key, value in data.items():
            self.add_new_item(new_key=key, new_value=value)

    def delete_given_keys(self, keys_to_delete: Union[Set[str], List[str]]) -> None:
        for key in keys_to_delete.copy():
            with suppress(KeyError):
                del self._session[str(key)]
                self._keys_collector.remove(key)
        self._session.modified = True

    def flush_keys_collector(self) -> None:
        self.delete_given_keys(self._keys_collector)
        self._keys_collector = set()
        self._session.modified = True

    def get_session(self) -> SessionBase:
        return self._session
