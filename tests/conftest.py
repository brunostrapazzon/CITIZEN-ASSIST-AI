"""Configuração compartilhada dos testes.

Adiciona a pasta src/ ao caminho de importação, da mesma forma que acontece
quando o programa é executado com `python src/sistema.py`.
"""

import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
SRC = RAIZ / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from core.base_conhecimento import carregar_base  # noqa: E402
from core.respostas import Assistente  # noqa: E402


@pytest.fixture(scope="session")
def base_real():
    return carregar_base()


@pytest.fixture(scope="session")
def assistente(base_real):
    return Assistente(base_real)


def registro_valido(**alteracoes):
    """Registro mínimo e válido, usado para montar bases de teste."""
    registro = {
        "id": "DOC001",
        "tema": "documentacao",
        "titulo": "Titulo de teste",
        "pergunta": "Como fazer um teste?",
        "palavras_chave": ["teste"],
        "resumo": "Resumo.",
        "orientacao": "Orientação.",
        "passos": ["Passo 1"],
        "limitacoes": ["Limitação"],
        "fonte": {"nome": "Órgão", "url": "https://www.gov.br/exemplo"},
        "data_verificacao": "2026-11-17",
        "aviso": "Aviso.",
        "relacionados": [],
    }
    registro.update(alteracoes)
    return registro


def base_valida(registros=None):
    return {
        "categorias": {"documentacao": "Documentação"},
        "registros": registros if registros is not None else [registro_valido()],
    }


@pytest.fixture
def gravar_json(tmp_path):
    """Grava um conteúdo (objeto ou texto) em um arquivo temporário."""

    def _gravar(conteudo, nome="base.json"):
        caminho = tmp_path / nome
        texto = conteudo if isinstance(conteudo, str) else json.dumps(conteudo, ensure_ascii=False)
        caminho.write_text(texto, encoding="utf-8")
        return caminho

    return _gravar
