"""Motor de busca do Citizen Assist AI.

Estratégia (documentada no README):

1. Normalização: minúsculas, remoção de acentos e de pontuação.
2. Tokenização com remoção de palavras vazias (stopwords) e redução simples
   de plural ("direitos" -> "direito", "reclamações" -> "reclamacao").
3. Índice invertido: termo -> {id do registro: peso do campo onde aparece}.
   Pesos: título e palavras-chave = 3, pergunta = 2, resumo e orientação = 1.
4. Pontuação de relevância (estilo TF-IDF simplificado):
       pontuacao(d) = soma, para cada termo t da consulta, de
                      fator(t) * idf(t) * peso_campo(t, d)
   com idf(t) = ln(1 + N / df(t)). Termos raros pesam mais que termos comuns.
   fator(t) = 1 para termo exato e 0,7 para termo corrigido por semelhança
   (erros de digitação, via difflib da biblioteca padrão).
5. Cobertura: parte da informação da consulta (soma dos idf) que o registro
   contém. Palavras desconhecidas reduzem a cobertura, o que impede que uma
   única palavra em comum gere uma resposta "confiável".
6. Classificação: sem_resultado, baixa_confianca, ambiguo ou encontrado,
   segundo os limiares abaixo. Empates são desfeitos pelo id do registro.
   Para responder direto, a orientação precisa de confiança >= 0,6 E cobertura
   >= 0,6; entre 0,5 e 0,6 de cobertura, ela só aparece como opção.

Histórico de ajustes (motivados por testes, ver docs/relatorio):
- v2: plural "-ais" -> "-al"; correção ortográfica exige mesma inicial;
  cobertura mínima de 0,6 para resposta direta ("receita de bolo" -> CPF).
"""

from __future__ import annotations

import difflib
import math
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Literal

from core.base_conhecimento import BaseConhecimento, Registro

PESOS_CAMPO: dict[str, float] = {
    "titulo": 3.0,
    "palavras_chave": 3.0,
    "pergunta": 2.0,
    "resumo": 1.0,
    "orientacao": 1.0,
}
PESO_REFERENCIA = 2.0          # peso de uma correspondência "boa" (nível da pergunta)
FATOR_CORRECAO = 0.7           # termo corrigido vale menos que termo exato
SEMELHANCA_MINIMA = 0.8        # corte do difflib para aceitar uma correção
COBERTURA_MINIMA = 0.5         # ao menos metade da informação da consulta (para virar opção)
COBERTURA_ALTA = 0.6           # mínimo para responder diretamente
CONFIANCA_MINIMA = 0.35        # abaixo disso: sem resultado
CONFIANCA_ALTA = 0.6           # abaixo disso: baixa confiança
MARGEM_AMBIGUIDADE = 0.8       # 2º colocado com >= 80% da pontuação do 1º = ambíguo
LIMITE_RESULTADOS = 5

STOPWORDS = frozenset(
    """a o as os um uma uns umas de da do das dos em no na nos nas ao aos à às
    para pra pro por pelo pela pelos pelas com sem e ou que qual quais como onde
    quando quem eu meu minha meus minhas me mim voce voces se seu sua seus suas
    lhe isso isto esse essa este esta sobre quero queria preciso precisa gostaria
    saber posso pode podem devo faco faz fazer ter tem tenho ja nao sim mais muito
    ser sao e esta estou foi vai vou ha hoje agora oi ola bom dia tarde noite
    obrigado obrigada favor ajuda ajudar""".split()
)

Status = Literal["encontrado", "ambiguo", "baixa_confianca", "sem_resultado"]


def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos, sem pontuação e com espaços simples."""
    texto = unicodedata.normalize("NFKD", texto.casefold())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return " ".join(texto.split())


def _radical(termo: str) -> str:
    """Redução simples de plural do português (suficiente para a base)."""
    if len(termo) <= 4:
        return termo
    for sufixo, troca in (("coes", "cao"), ("soes", "sao"), ("oes", "ao"), ("aes", "ao"), ("ais", "al"), ("eis", "el"), ("ns", "m")):
        if termo.endswith(sufixo):
            return termo[: -len(sufixo)] + troca
    if termo.endswith("s"):
        return termo[:-1]
    return termo


def tokenizar(texto: str) -> list[str]:
    return [_radical(t) for t in normalizar(texto).split() if t not in STOPWORDS]


class IndiceInvertido:
    """Termo -> {id do registro: maior peso de campo em que o termo aparece}."""

    def __init__(self, base: BaseConhecimento) -> None:
        self.n_docs = len(base.registros)
        self.postings: dict[str, dict[str, float]] = {}
        for registro in base.registros.values():
            for campo, peso in PESOS_CAMPO.items():
                valor = getattr(registro, campo)
                textos = valor if isinstance(valor, tuple) else (valor,)
                for texto in textos:
                    for termo in tokenizar(texto):
                        docs = self.postings.setdefault(termo, {})
                        docs[registro.id] = max(docs.get(registro.id, 0.0), peso)
        self.vocabulario = sorted(self.postings)

    def idf(self, termo: str) -> float:
        df = len(self.postings.get(termo, {}))
        return math.log(1 + self.n_docs / max(df, 1))

    @property
    def idf_maximo(self) -> float:
        return math.log(1 + self.n_docs)

    def resolver(self, termo: str) -> tuple[str | None, float]:
        """Devolve (termo do índice, fator). Tenta correção para erros de digitação."""
        if termo in self.postings:
            return termo, 1.0
        if len(termo) >= 4:
            # Erros de digitação raramente afetam a primeira letra; exigir a mesma
            # inicial evita correções sem relação (ex.: "emito" -> "feito").
            candidatos = [v for v in self.vocabulario if v[0] == termo[0]]
            parecidos = difflib.get_close_matches(termo, candidatos, n=1, cutoff=SEMELHANCA_MINIMA)
            if parecidos:
                return parecidos[0], FATOR_CORRECAO
        return None, 0.0


@dataclass(frozen=True)
class Correspondencia:
    registro_id: str
    pontuacao: float
    confianca: float
    cobertura: float
    termos_encontrados: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoBusca:
    status: Status
    correspondencias: tuple[Correspondencia, ...]
    termos: tuple[str, ...]
    termos_corrigidos: dict[str, str] = field(default_factory=dict)

    @property
    def melhor(self) -> Correspondencia | None:
        return self.correspondencias[0] if self.correspondencias else None


class MotorBusca:
    def __init__(self, base: BaseConhecimento, indice: IndiceInvertido | None = None) -> None:
        self.base = base
        self.indice = indice or IndiceInvertido(base)

    # -------------------------------------------------- buscas diretas
    def buscar_por_id(self, registro_id: str) -> Registro | None:
        return self.base.registros.get(registro_id.strip().upper())

    def listar_categoria(self, tema: str) -> list[Registro]:
        return sorted(self.base.por_tema(tema), key=lambda r: r.id)

    # -------------------------------------------------- busca textual
    def buscar(self, consulta: str, categoria: str | None = None, limite: int = LIMITE_RESULTADOS) -> ResultadoBusca:
        termos = tuple(dict.fromkeys(tokenizar(consulta)))  # sem repetição, ordem mantida
        if not termos:
            return ResultadoBusca("sem_resultado", (), termos)

        resolvidos: list[tuple[str, str | None, float]] = []
        corrigidos: dict[str, str] = {}
        for termo in termos:
            alvo, fator = self.indice.resolver(termo)
            resolvidos.append((termo, alvo, fator))
            if alvo is not None and alvo != termo:
                corrigidos[termo] = alvo

        informacao_total = sum(
            self.indice.idf(alvo) if alvo else self.indice.idf_maximo for _, alvo, _ in resolvidos
        )
        ideal = PESO_REFERENCIA * informacao_total

        pontos: dict[str, float] = {}
        informacao: dict[str, float] = {}
        encontrados: dict[str, list[str]] = {}
        for termo, alvo, fator in resolvidos:
            if alvo is None:
                continue
            idf = self.indice.idf(alvo)
            for rid, peso in self.indice.postings[alvo].items():
                if categoria and self.base.registros[rid].tema != categoria:
                    continue
                pontos[rid] = pontos.get(rid, 0.0) + fator * idf * peso
                informacao[rid] = informacao.get(rid, 0.0) + fator * idf
                encontrados.setdefault(rid, []).append(alvo)

        candidatos = [
            Correspondencia(
                registro_id=rid,
                pontuacao=round(pontos[rid], 4),
                confianca=round(min(1.0, pontos[rid] / ideal), 4),
                cobertura=round(informacao[rid] / informacao_total, 4),
                termos_encontrados=tuple(encontrados[rid]),
            )
            for rid in pontos
        ]
        candidatos.sort(key=lambda c: (-c.pontuacao, c.registro_id))
        validos = [c for c in candidatos if c.cobertura >= COBERTURA_MINIMA and c.confianca >= CONFIANCA_MINIMA]
        if not validos:
            return ResultadoBusca("sem_resultado", (), termos, corrigidos)

        melhor = validos[0]
        proximos = tuple(c for c in validos if c.pontuacao >= MARGEM_AMBIGUIDADE * melhor.pontuacao)
        if len(proximos) > 1:
            return ResultadoBusca("ambiguo", proximos[:limite], termos, corrigidos)
        confiavel = melhor.confianca >= CONFIANCA_ALTA and melhor.cobertura >= COBERTURA_ALTA
        status: Status = "encontrado" if confiavel else "baixa_confianca"
        return ResultadoBusca(status, tuple(validos[:limite]), termos, corrigidos)
