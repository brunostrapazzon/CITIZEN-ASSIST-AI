"""Testes do grafo de assuntos e do algoritmo de Dijkstra (src/core/grafo.py)."""

import random
from math import inf

import pytest

from core.erros import CaminhoInexistente, RegistroNaoEncontrado
from core.grafo import (
    PESO_PERTENCE_CATEGORIA,
    PESO_RELACAO_ENTRE_CATEGORIAS,
    PESO_RELACAO_MESMA_CATEGORIA,
    caminho_minimo,
    construir_grafo,
    dijkstra,
    matriz_adjacencia,
    relacionados_por_proximidade,
)


def floyd_warshall(grafo):
    """Oráculo independente: todas as distâncias mínimas em O(V³)."""
    nos = list(grafo)
    dist = {a: {b: (0.0 if a == b else inf) for b in nos} for a in nos}
    for u in grafo:
        for v, peso in grafo[u]:
            dist[u][v] = min(dist[u][v], peso)
    for k in nos:
        for i in nos:
            for j in nos:
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
    return dist


# ------------------------------------------------------------ casos à mão
GRAFO_MANUAL = {
    # A --1--> B --2--> D ;  A --4--> C --1--> D ;  A --10--> D
    "A": [("B", 1.0), ("C", 4.0), ("D", 10.0)],
    "B": [("D", 2.0)],
    "C": [("D", 1.0)],
    "D": [],
    "E": [],
}


def test_caso_calculado_a_mao():
    # Caminhos de A até D: direto = 10; A-C-D = 5; A-B-D = 3 (mínimo).
    caminho, custo = caminho_minimo(GRAFO_MANUAL, "A", "D")
    assert caminho == ["A", "B", "D"]
    assert custo == 3.0


def test_origem_igual_destino():
    assert caminho_minimo(GRAFO_MANUAL, "A", "A") == (["A"], 0.0)


def test_destino_inalcancavel():
    with pytest.raises(CaminhoInexistente):
        caminho_minimo(GRAFO_MANUAL, "A", "E")


def test_no_inexistente():
    with pytest.raises(RegistroNaoEncontrado):
        dijkstra(GRAFO_MANUAL, "Z")


def test_peso_negativo_rejeitado():
    with pytest.raises(ValueError):
        dijkstra({"A": [("B", -1.0)], "B": []}, "A")


def test_dijkstra_igual_ao_oraculo_em_grafos_aleatorios():
    gerador = random.Random(2026)
    for _ in range(100):
        n = gerador.randint(1, 10)
        nos = [f"n{i}" for i in range(n)]
        grafo = {v: [] for v in nos}
        for u in nos:
            for v in nos:
                if u != v and gerador.random() < 0.3:
                    grafo[u].append((v, float(gerador.randint(0, 9))))
        oraculo = floyd_warshall(grafo)
        for origem in nos:
            dist, _ = dijkstra(grafo, origem)
            for destino in nos:
                assert dist[destino] == oraculo[origem][destino]


def test_caminho_em_empate_e_valido():
    grafo = {"A": [("B", 1.0), ("C", 1.0)], "B": [("D", 1.0)], "C": [("D", 1.0)], "D": []}
    caminho, custo = caminho_minimo(grafo, "A", "D")
    assert custo == 2.0
    for u, v in zip(caminho, caminho[1:]):
        assert any(destino == v for destino, _ in grafo[u])


# --------------------------------------------------------- grafo do projeto
@pytest.fixture(scope="module")
def grafo(base_real):
    return construir_grafo(base_real)


def test_grafo_tem_registros_e_categorias(grafo, base_real):
    assert set(base_real.registros) <= set(grafo.adjacencia)
    assert {"CAT:documentacao", "CAT:servicos_publicos", "CAT:direitos_cidadania"} <= set(grafo.adjacencia)


def test_grafo_nao_direcionado_e_sem_vertices_orfaos(grafo):
    adj = grafo.adjacencia
    for u, arestas in adj.items():
        for v, peso in arestas:
            assert v in adj
            assert peso >= 0
            assert any(w == u and p == peso for w, p in adj[v])


def test_pesos_documentados(grafo):
    pesos = {p for arestas in grafo.adjacencia.values() for _, p in arestas}
    assert pesos <= {PESO_RELACAO_MESMA_CATEGORIA, PESO_RELACAO_ENTRE_CATEGORIAS, PESO_PERTENCE_CATEGORIA}


def test_grafo_real_e_conexo(grafo):
    dist, _ = dijkstra(grafo.adjacencia, "DOC001")
    assert all(d < inf for d in dist.values())


def test_trilha_entre_categorias_passa_por_assuntos(grafo):
    caminho, custo = caminho_minimo(grafo.adjacencia, "CAT:documentacao", "CAT:servicos_publicos")
    assert caminho[0] == "CAT:documentacao" and caminho[-1] == "CAT:servicos_publicos"
    assert custo > 0
    assert len(caminho) >= 3


def test_dijkstra_do_grafo_real_igual_ao_oraculo(grafo):
    oraculo = floyd_warshall(grafo.adjacencia)
    for origem in grafo.adjacencia:
        dist, _ = dijkstra(grafo.adjacencia, origem)
        assert dist == oraculo[origem]


def test_relacionados_por_proximidade(grafo):
    proximos = relacionados_por_proximidade(grafo.adjacencia, "DOC004", limite=3)
    ids = [i for i, _ in proximos]
    assert "DOC004" not in ids
    assert all(not i.startswith("CAT:") for i in ids)
    distancias = [d for _, d in proximos]
    assert distancias == sorted(distancias)
    assert ids[0] in {"DOC001", "DOC002"}


def test_rotulo_dos_nos(grafo):
    assert grafo.rotulo("CAT:documentacao") == "Documentação"
    assert "Passaporte" in grafo.rotulo("DOC004")


def test_matriz_de_adjacencia(grafo):
    nos, matriz = matriz_adjacencia(grafo.adjacencia)
    assert len(matriz) == len(nos) == len(grafo.adjacencia)
    i, j = nos.index("DOC004"), nos.index("DOC001")
    assert matriz[i][j] == matriz[j][i] > 0
