"""Grafo de assuntos e algoritmo de Dijkstra.

Estrutura (lista de adjacência, grafo NÃO direcionado):
- Vértices: cada orientação da base (ex.: "DOC002") e cada categoria
  ("CAT:documentacao", "CAT:servicos_publicos", "CAT:direitos_cidadania").
- Arestas e pesos (custo de navegação; quanto menor, mais próximo):
    * relação explícita entre orientações da MESMA categoria ........ 1,0
    * relação explícita entre orientações de categorias DIFERENTES ... 1,5
    * orientação ligada à sua categoria ................................ 2,0
  As relações explícitas vêm do campo "relacionados" da base. A ligação com a
  categoria garante que todo assunto seja alcançável, mas custa mais, porque
  representa uma navegação genérica ("voltar ao tema e escolher outro").

Usos reais no sistema:
- Trilha de navegação entre dois assuntos (menu "Assuntos relacionados").
- Ordenação dos "Assuntos relacionados" do Modelo B por proximidade.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass
from math import inf

from core.base_conhecimento import BaseConhecimento
from core.erros import CaminhoInexistente, RegistroNaoEncontrado

PESO_RELACAO_MESMA_CATEGORIA = 1.0
PESO_RELACAO_ENTRE_CATEGORIAS = 1.5
PESO_PERTENCE_CATEGORIA = 2.0
PREFIXO_CATEGORIA = "CAT:"

Grafo = dict[str, list[tuple[str, float]]]


@dataclass(frozen=True)
class GrafoAssuntos:
    adjacencia: Grafo
    rotulos: dict[str, str]

    def rotulo(self, no: str) -> str:
        return self.rotulos.get(no, no)

    def vizinhos(self, no: str) -> list[tuple[str, float]]:
        if no not in self.adjacencia:
            raise RegistroNaoEncontrado(f"Assunto '{no}' não existe no grafo.")
        return sorted(self.adjacencia[no], key=lambda par: (par[1], par[0]))


def _adicionar_aresta(grafo: Grafo, u: str, v: str, peso: float) -> None:
    """Aresta não direcionada; se já existir, mantém o menor peso."""
    for a, b in ((u, v), (v, u)):
        arestas = grafo[a]
        for i, (destino, p) in enumerate(arestas):
            if destino == b:
                arestas[i] = (b, min(p, peso))
                break
        else:
            arestas.append((b, peso))


def construir_grafo(base: BaseConhecimento) -> GrafoAssuntos:
    grafo: Grafo = {}
    rotulos: dict[str, str] = {}
    for tema, nome in base.categorias.items():
        no = PREFIXO_CATEGORIA + tema
        grafo[no] = []
        rotulos[no] = nome
    for registro in base.registros.values():
        grafo[registro.id] = []
        rotulos[registro.id] = registro.titulo
    for registro in base.registros.values():
        _adicionar_aresta(grafo, registro.id, PREFIXO_CATEGORIA + registro.tema, PESO_PERTENCE_CATEGORIA)
        for outro_id in registro.relacionados:
            outro = base.registros[outro_id]
            peso = PESO_RELACAO_MESMA_CATEGORIA if outro.tema == registro.tema else PESO_RELACAO_ENTRE_CATEGORIAS
            _adicionar_aresta(grafo, registro.id, outro_id, peso)
    return GrafoAssuntos(adjacencia=grafo, rotulos=rotulos)


def dijkstra(grafo: Grafo, origem: str) -> tuple[dict[str, float], dict[str, str | None]]:
    """Distâncias mínimas a partir de `origem`.

    Usa fila de prioridade (heapq) com "remoção preguiçosa": entradas antigas
    da fila são ignoradas quando já existe uma distância menor registrada.
    Complexidade: O((V + E) log V).
    """
    if origem not in grafo:
        raise RegistroNaoEncontrado(f"Assunto '{origem}' não existe no grafo.")
    distancia: dict[str, float] = {no: inf for no in grafo}
    anterior: dict[str, str | None] = {no: None for no in grafo}
    distancia[origem] = 0.0
    fila: list[tuple[float, str]] = [(0.0, origem)]
    while fila:
        d, u = heapq.heappop(fila)
        if d > distancia[u]:
            continue
        for v, peso in grafo[u]:
            if peso < 0:
                raise ValueError("Dijkstra exige pesos não negativos.")
            nova = d + peso
            if nova < distancia[v]:
                distancia[v] = nova
                anterior[v] = u
                heapq.heappush(fila, (nova, v))
    return distancia, anterior


def caminho_minimo(grafo: Grafo, origem: str, destino: str) -> tuple[list[str], float]:
    if destino not in grafo:
        raise RegistroNaoEncontrado(f"Assunto '{destino}' não existe no grafo.")
    distancia, anterior = dijkstra(grafo, origem)
    if distancia[destino] == inf:
        raise CaminhoInexistente(f"Não há caminho entre '{origem}' e '{destino}'.")
    caminho: list[str] = []
    atual: str | None = destino
    while atual is not None:
        caminho.append(atual)
        atual = anterior[atual]
    return caminho[::-1], distancia[destino]


def relacionados_por_proximidade(grafo: Grafo, origem: str, limite: int = 3) -> list[tuple[str, float]]:
    """Orientações mais próximas de `origem` no grafo (categorias excluídas)."""
    distancia, _ = dijkstra(grafo, origem)
    candidatos = [
        (no, d) for no, d in distancia.items()
        if no != origem and d < inf and not no.startswith(PREFIXO_CATEGORIA)
    ]
    candidatos.sort(key=lambda par: (par[1], par[0]))
    return candidatos[:limite]


def matriz_adjacencia(grafo: Grafo) -> tuple[list[str], list[list[float]]]:
    """Representação em matriz (0 = sem aresta). Usada só para exibição e relatório."""
    nos = sorted(grafo)
    posicao = {no: i for i, no in enumerate(nos)}
    matriz = [[0.0] * len(nos) for _ in nos]
    for u, arestas in grafo.items():
        for v, peso in arestas:
            matriz[posicao[u]][posicao[v]] = peso
    return nos, matriz
