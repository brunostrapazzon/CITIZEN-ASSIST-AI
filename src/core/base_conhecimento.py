"""Leitura da base de conhecimento (data/base.json).

O arquivo é lido uma única vez, validado por completo e convertido em objetos
imutáveis. Qualquer falha vira BaseConhecimentoInvalida, com uma mensagem clara.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from core.erros import BaseConhecimentoInvalida, RegistroNaoEncontrado
from core.validacoes import validar_dados_base

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
CAMINHO_PADRAO = RAIZ_PROJETO / "data" / "base.json"


@dataclass(frozen=True)
class Fonte:
    nome: str
    url: str


@dataclass(frozen=True)
class Registro:
    id: str
    tema: str
    titulo: str
    pergunta: str
    palavras_chave: tuple[str, ...]
    resumo: str
    orientacao: str
    passos: tuple[str, ...]
    limitacoes: tuple[str, ...]
    fonte: Fonte
    data_verificacao: str
    aviso: str
    relacionados: tuple[str, ...]


@dataclass(frozen=True)
class BaseConhecimento:
    categorias: dict[str, str]
    registros: dict[str, Registro]

    def obter(self, registro_id: str) -> Registro:
        chave = registro_id.strip().upper()
        if chave not in self.registros:
            raise RegistroNaoEncontrado(f"Orientação '{registro_id}' não encontrada.")
        return self.registros[chave]

    def por_tema(self, tema: str) -> list[Registro]:
        return [r for r in self.registros.values() if r.tema == tema]

    def nome_categoria(self, tema: str) -> str:
        return self.categorias.get(tema, tema)


def _converter(dados: dict) -> BaseConhecimento:
    registros = {}
    for item in dados["registros"]:
        registros[item["id"]] = Registro(
            id=item["id"],
            tema=item["tema"],
            titulo=item["titulo"],
            pergunta=item["pergunta"],
            palavras_chave=tuple(item["palavras_chave"]),
            resumo=item["resumo"],
            orientacao=item["orientacao"],
            passos=tuple(item["passos"]),
            limitacoes=tuple(item["limitacoes"]),
            fonte=Fonte(nome=item["fonte"]["nome"], url=item["fonte"]["url"]),
            data_verificacao=item["data_verificacao"],
            aviso=item["aviso"],
            relacionados=tuple(item["relacionados"]),
        )
    return BaseConhecimento(categorias=dict(dados["categorias"]), registros=registros)


def caminho_base_configurado() -> Path:
    """Permite trocar a base por variável de ambiente (usado nos testes)."""
    return Path(os.environ.get("CITIZEN_ASSIST_BASE", CAMINHO_PADRAO))


def carregar_base(caminho: Path | str | None = None) -> BaseConhecimento:
    caminho = Path(caminho) if caminho is not None else caminho_base_configurado()
    try:
        texto = caminho.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise BaseConhecimentoInvalida(f"Arquivo da base não encontrado: {caminho}") from None
    except (OSError, UnicodeDecodeError) as erro:
        raise BaseConhecimentoInvalida(f"Falha ao ler a base de conhecimento: {erro}") from None

    if not texto.strip():
        raise BaseConhecimentoInvalida("O arquivo da base de conhecimento está vazio.")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as erro:
        raise BaseConhecimentoInvalida(
            f"JSON malformado na base de conhecimento (linha {erro.lineno}, coluna {erro.colno})."
        ) from None

    problemas = validar_dados_base(dados)
    if problemas:
        raise BaseConhecimentoInvalida("A base de conhecimento tem dados inconsistentes:", problemas)
    return _converter(dados)
