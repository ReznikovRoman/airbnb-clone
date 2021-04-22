from typing import List, Optional, Union, Tuple

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

        if not self._session.get(keys_collector_name, None):
            self._session[keys_collector_name] = []
        self._keys_collector: List[str] = self._session.get(keys_collector_name)

    def create_initial_dict_with_session_data(self, initial_keys: Union[List[str], Tuple[str]]) -> dict:
        return {initial_key: self._session.get(create_name_with_prefix(initial_key, self._prefix), None)
                for initial_key in initial_keys}

    def add_new_key_to_collector(self, new_session_key: str) -> None:
        self._keys_collector.append(new_session_key)

    def add_new_item(self, new_key: str, new_value) -> None:
        session_key = create_name_with_prefix(new_key, self._prefix)
        try:
            self._session[session_key] = new_value
            self.add_new_key_to_collector(session_key)
        except TypeError:
            pass

    def update_values_with_given_data(self, data: dict) -> None:
        for field_name, field_value in data.items():
            self.add_new_item(new_key=field_name, new_value=field_value)

    def delete_given_keys(self, keys_to_delete: List[str]) -> None:
        for key in keys_to_delete:
            try:
                del self._session[str(key)]
            except KeyError:
                pass
        self._session.modified = True

    def flush_keys_collector(self) -> None:
        self.delete_given_keys(self._keys_collector)
        self._keys_collector = []
        self._session.modified = True

    def get_session(self) -> SessionBase:
        return self._session
