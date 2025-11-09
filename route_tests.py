import pytest
from curator import route_memory

@pytest.mark.parametrize("content,expected", [
    ("A 2015 paper on topological codes was dismissed but may be relevant later.", "archivist"),
    ("Theorem: For any stabilizer code, symplectic transform preserves error distance.", "formalist"),
    ("What if we combine symplectic methods with neural error correction?", "synthesist"),
    ("12% decoherence reduction → enables 1000-qubit scale-up by 2027.", "strategist"),
])
def test_route(content, expected):
    res = route_memory(content, phase="discovery")
    assert res["routing"]["primary_owner"] == expected
