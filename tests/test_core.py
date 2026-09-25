from memora.core import Memora


def test_graph_and_compression(tmp_path):
    path = tmp_path / "memory.db"
    m = Memora(path)
    chat = m.add_chat("Proyecto memoria")
    msg = m.add_message(chat, "user", "Las redes conectadas permiten reconstruir contexto.")
    assert m.get(msg).content.startswith("Las redes")
    assert any(x.kind == "concept" for x in m.neighbors(msg))
    assert path.exists()
    m.close()


def test_persistence_after_reopen(tmp_path):
    path = tmp_path / "memory.db"
    m = Memora(path)
    chat = m.add_chat("Persistencia")
    msg = m.add_message(chat, "user", "La memoria debe sobrevivir al cierre.")
    m.close()

    reopened = Memora(path)
    recovered = reopened.get(msg)
    assert recovered is not None
    assert recovered.content == "La memoria debe sobrevivir al cierre."
    reopened.close()


def test_search_and_recall(tmp_path):
    m = Memora(tmp_path / "memory.db")
    chat = m.add_chat("A")
    m.add_message(chat, "user", "SQLite conserva la memoria de forma compacta.")
    m.add_message(chat, "assistant", "El grafo conecta conceptos con mensajes.")
    assert m.search("memoria compacta")
    result = m.recall("grafo conceptos", limit=4)
    assert result["matches"] and result["reconstruction"]
    assert all("id" in item and "kind" in item for item in result["reconstruction"])
    m.close()


def test_cross_chat_recall(tmp_path):
    m = Memora(tmp_path / "memory.db")
    chat_a = m.add_chat("Diseño")
    chat_b = m.add_chat("Implementación")
    first = m.add_message(chat_a, "user", "MEMORA necesita reconstruir contexto mediante un grafo.")
    second = m.add_message(chat_b, "assistant", "El grafo permite conectar memoria entre conversaciones.")
    result = m.recall("grafo memoria conversaciones", limit=8, depth=1)
    ids = {item["id"] for item in result["reconstruction"]}
    assert first in ids
    assert second in ids
    m.close()


def test_deduplication(tmp_path):
    m = Memora(tmp_path / "memory.db")
    chat = m.add_chat("A")
    a = m.add_message(chat, "user", "mismo contenido")
    b = m.add_message(chat, "user", "mismo contenido")
    assert a == b
    m.close()
