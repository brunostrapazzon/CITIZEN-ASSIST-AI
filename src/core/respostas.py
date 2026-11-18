"""Composição das respostas: Modelo A (direta) e Modelo B (contextualizada).

Não há modelo de IA externo. Os "prompts" abaixo são modelos de instrução
aplicados à lógica de composição: cada um define quais seções a resposta tem,
em que ordem e de quais campos da base o conteúdo vem. Regra absoluta: todo
texto exibido vem de data/base.json. Se a base não tem a informação, o sistema
diz isso em vez de improvisar.

A classe Assistente é a porta de entrada única usada pela CLI e pela Web.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Literal

from core.base_conhecimento import BaseConhecimento, Fonte, Registro, carregar_base
from core.busca import Correspondencia, MotorBusca
from core.erros import EntradaInvalida
from core.grafo import GrafoAssuntos, caminho_minimo, construir_grafo, relacionados_por_proximidade
from core.validacoes import FORMATO_ID, validar_entrada

Modelo = Literal["A", "B"]
MODELOS: tuple[Modelo, ...] = ("A", "B")

INSTRUCAO_MODELO_A = """MODELO A — RESPOSTA DIRETA
Papel: assistente de orientação cidadã, não oficial, que organiza informações
verificadas e sempre indica onde confirmá-las.
Objetivo: resolver rápido, com o mínimo de leitura.
Formato:
1. Orientação: use somente o campo 'resumo' do registro, em linguagem simples.
2. Passo a passo: liste o campo 'passos' numerado, sem acrescentar passos.
3. Fonte oficial: nome do órgão e URL do campo 'fonte'.
4. Aviso: campo 'aviso' (necessidade de confirmar nos canais oficiais).
Proibido: incluir informação que não esteja no registro."""

INSTRUCAO_MODELO_B = """MODELO B — RESPOSTA CONTEXTUALIZADA
Papel: assistente de orientação cidadã, não oficial, que explica com calma,
mostra as ressalvas e sempre indica onde confirmar a informação.
Objetivo: explicar o contexto e preparar o cidadão para os próximos passos.
Formato:
1. Sua necessidade: reformule a necessidade com o campo 'pergunta' do registro.
2. Contexto: explique com o campo 'orientacao'.
3. Passo a passo: liste o campo 'passos' numerado.
4. Fonte oficial: nome do órgão e URL do campo 'fonte'.
5. Limitações e ressalvas: campo 'limitacoes' (condições, custos, variações locais).
6. Assuntos relacionados: orientações mais próximas no grafo (Dijkstra).
7. Aviso: campo 'aviso'.
Proibido: incluir informação que não esteja no registro."""

MENSAGENS = {
    "sem_resultado": (
        "A base do Citizen Assist AI não possui uma orientação verificada para essa pergunta. "
        "Tente outras palavras, explore os temas disponíveis ou consulte o portal oficial gov.br."
    ),
    "ambiguo": "Encontrei mais de uma orientação parecida. Escolha a que corresponde à sua dúvida:",
    "baixa_confianca": (
        "Não tenho certeza de que entendi a pergunta. Estas orientações podem ajudar; "
        "escolha uma ou reformule a pergunta:"
    ),
    "encontrado": "",
}


@dataclass(frozen=True)
class Secao:
    titulo: str
    conteudo: str | tuple[str, ...]


@dataclass(frozen=True)
class Resposta:
    modelo: Modelo
    registro_id: str
    titulo: str
    categoria: str
    secoes: tuple[Secao, ...]
    fonte: Fonte
    data_verificacao: str


@dataclass(frozen=True)
class ResultadoConsulta:
    pergunta: str
    status: str  # encontrado | ambiguo | baixa_confianca | sem_resultado | entrada_invalida
    mensagem: str
    resposta: Resposta | None
    opcoes: tuple[Correspondencia, ...]
    termos_corrigidos: tuple[tuple[str, str], ...]
    tempo_ms: float


def _fonte_texto(registro: Registro) -> str:
    return f"{registro.fonte.nome} — {registro.fonte.url} (verificado em {registro.data_verificacao})"


def gerar_resposta_modelo_a(registro: Registro, base: BaseConhecimento) -> Resposta:
    secoes = (
        Secao("Orientação", registro.resumo),
        Secao("Passo a passo", registro.passos),
        Secao("Fonte oficial", _fonte_texto(registro)),
        Secao("Aviso", registro.aviso),
    )
    return Resposta("A", registro.id, registro.titulo, base.nome_categoria(registro.tema),
                    secoes, registro.fonte, registro.data_verificacao)


def gerar_resposta_modelo_b(registro: Registro, base: BaseConhecimento, relacionados: list[Registro]) -> Resposta:
    relacionados_txt = tuple(f"{r.id} — {r.titulo}" for r in relacionados) or ("Nenhum assunto relacionado na base.",)
    secoes = (
        Secao("Sua necessidade", f"Você quer saber: {registro.pergunta}"),
        Secao("Contexto", registro.orientacao),
        Secao("Passo a passo", registro.passos),
        Secao("Fonte oficial", _fonte_texto(registro)),
        Secao("Limitações e ressalvas", registro.limitacoes),
        Secao("Assuntos relacionados", relacionados_txt),
        Secao("Aviso", registro.aviso),
    )
    return Resposta("B", registro.id, registro.titulo, base.nome_categoria(registro.tema),
                    secoes, registro.fonte, registro.data_verificacao)


class Assistente:
    """Fachada do núcleo: tudo o que as interfaces precisam passa por aqui."""

    def __init__(self, base: BaseConhecimento | None = None) -> None:
        self.base = base or carregar_base()
        self.motor = MotorBusca(self.base)
        self.grafo: GrafoAssuntos = construir_grafo(self.base)

    # ------------------------------------------------------------ respostas
    def responder_registro(self, registro_id: str, modelo: Modelo = "B") -> Resposta:
        if modelo not in MODELOS:
            raise ValueError(f"Modelo de resposta desconhecido: {modelo!r}. Use 'A' ou 'B'.")
        registro = self.base.obter(registro_id)
        if modelo == "A":
            return gerar_resposta_modelo_a(registro, self.base)
        proximos = relacionados_por_proximidade(self.grafo.adjacencia, registro.id, limite=3)
        return gerar_resposta_modelo_b(registro, self.base, [self.base.obter(i) for i, _ in proximos])

    def consultar(self, pergunta: str | None, modelo: Modelo = "B", categoria: str | None = None) -> ResultadoConsulta:
        if modelo not in MODELOS:
            raise ValueError(f"Modelo de resposta desconhecido: {modelo!r}. Use 'A' ou 'B'.")
        inicio = time.perf_counter()
        try:
            texto = validar_entrada(pergunta)
        except EntradaInvalida as erro:
            return ResultadoConsulta(pergunta or "", "entrada_invalida", str(erro), None, (), (),
                                     (time.perf_counter() - inicio) * 1000)

        if FORMATO_ID.match(texto.upper()) and self.motor.buscar_por_id(texto):
            resposta = self.responder_registro(texto, modelo)
            return ResultadoConsulta(texto, "encontrado", "", resposta, (), (),
                                     (time.perf_counter() - inicio) * 1000)

        busca = self.motor.buscar(texto, categoria=categoria)
        resposta = None
        if busca.status == "encontrado":
            resposta = self.responder_registro(busca.melhor.registro_id, modelo)
        opcoes = busca.correspondencias if busca.status in ("ambiguo", "baixa_confianca") else ()
        return ResultadoConsulta(
            pergunta=texto,
            status=busca.status,
            mensagem=MENSAGENS[busca.status],
            resposta=resposta,
            opcoes=opcoes,
            termos_corrigidos=tuple(sorted(busca.termos_corrigidos.items())),
            tempo_ms=(time.perf_counter() - inicio) * 1000,
        )

    def pesquisar_palavras_chave(self, texto: str, categoria: str | None = None) -> tuple[Correspondencia, ...]:
        """Lista ranqueada de correspondências (menu 'Pesquisar por palavras-chave')."""
        limpo = validar_entrada(texto)
        return self.motor.buscar(limpo, categoria=categoria).correspondencias

    # ------------------------------------------------------------ navegação
    def categorias(self) -> dict[str, str]:
        return dict(self.base.categorias)

    def registros_da_categoria(self, tema: str) -> list[Registro]:
        return self.motor.listar_categoria(tema)

    def relacionados(self, registro_id: str) -> list[tuple[Registro, float]]:
        registro = self.base.obter(registro_id)
        proximos = relacionados_por_proximidade(self.grafo.adjacencia, registro.id, limite=5)
        return [(self.base.obter(i), d) for i, d in proximos]

    def trilha(self, origem: str, destino: str) -> tuple[list[str], float]:
        """Caminho de menor custo entre dois assuntos (ids ou CAT:<tema>)."""
        origem, destino = origem.strip(), destino.strip()
        origem = origem if origem.startswith("CAT:") else origem.upper()
        destino = destino if destino.startswith("CAT:") else destino.upper()
        return caminho_minimo(self.grafo.adjacencia, origem, destino)

    def fontes(self) -> list[Registro]:
        return sorted(self.base.registros.values(), key=lambda r: r.id)
