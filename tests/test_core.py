from memora.core import Memora

def test_graph_and_compression(tmp_path):
    m = Memora(tmp_path/"memory.db")
    chat = m.add_chat("Proyecto memoria")
    msg = m.add_message(chat, "user", "Las redes conectadas permiten reconstruir contexto.")
    assert m.get(msg).content.startswith("Las redes")
    assert any(x.kind == "concept" for x in m.neighbors(msg))
    m.close()

def test_search_and_recall(tmp_path):
    m = Memora(tmp_path/"memory.db")
    chat = m.add_chat("A")
    m.add_message(chat, "user", "SQLite conserva la memoria de forma compacta.")
    m.add_message(chat, "assistant", "El grafo conecta conceptos con mensajes.")
    assert m.search("memoria compacta")
    result = m.recall("grafo conceptos", limit=4)
    assert result["matches"] and result["reconstruction"]
    m.close()

def test_deduplication(tmp_path):
    m = Memora(tmp_path/"memory.db")
    chat = m.add_chat("A")
    a = m.add_message(chat, "user", "mismo contenido")
    b = m.add_message(chat, "user", "mismo contenido")
    assert a == b
    m.close()
