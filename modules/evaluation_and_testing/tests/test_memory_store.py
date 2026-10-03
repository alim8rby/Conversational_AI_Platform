from modules.memory_store_setup import memory_store


class FakeIndex:
    def __init__(self):
        self.upserts = []
        self.queries = []

    def upsert(self, **kwargs):
        self.upserts.append(kwargs)

    def query(self, **kwargs):
        self.queries.append(kwargs)
        return type("Response", (), {"matches": []})()


def test_memory_operations_are_scoped_to_each_session(monkeypatch):
    fake_index = FakeIndex()
    monkeypatch.setattr(memory_store, "_get_index", lambda: fake_index)
    monkeypatch.setattr(memory_store, "embed_text", lambda text: [0.1, 0.2])

    memory_store.upsert_memory("turn-1", "hello", "session-a", {"role": "user"})
    memory_store.query_memory("session-b", "hello")

    assert fake_index.upserts[0]["namespace"] == "user:session-a"
    assert fake_index.queries[0]["namespace"] == "user:session-b"
