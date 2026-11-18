"""Validações da base de conhecimento e das entradas do usuário.

A validação da base devolve a lista completa de problemas encontrados, e não
apenas o primeiro, para que a equipe consiga corrigir tudo de uma vez.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date
from urllib.parse import urlparse

from core.erros import EntradaInvalida

# Campo obrigatório -> tipo esperado
CAMPOS_OBRIGATORIOS: dict[str, type] = {
    "id": str,
    "tema": str,
    "titulo": str,
    "pergunta": str,
    "palavras_chave": list,
    "resumo": str,
    "orientacao": str,
    "passos": list,
    "limitacoes": list,
    "fonte": dict,
    "data_verificacao": str,
    "aviso": str,
    "relacionados": list,
}

FORMATO_ID = re.compile(r"^[A-Z]{3}\d{3}$")
TAMANHO_MAXIMO_ENTRADA = 300


def _normalizar_titulo(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in texto if not unicodedata.combining(c)).strip()


def validar_url(url: object) -> bool:
    """Aceita apenas URLs https completas (esquema + domínio, sem espaços)."""
    if not isinstance(url, str) or " " in url:
        return False
    partes = urlparse(url)
    return partes.scheme == "https" and "." in partes.netloc


def _validar_data(valor: str) -> bool:
    try:
        date.fromisoformat(valor)
    except ValueError:
        return False
    return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", valor))


def _validar_registro(reg: object, posicao: int, categorias: dict) -> list[str]:
    if not isinstance(reg, dict):
        return [f"registro na posição {posicao}: precisa ser um objeto"]
    rid = reg.get("id", f"posição {posicao}")
    problemas: list[str] = []

    for campo, tipo in CAMPOS_OBRIGATORIOS.items():
        if campo not in reg:
            problemas.append(f"{rid}: campo obrigatório '{campo}' ausente")
            continue
        valor = reg[campo]
        if not isinstance(valor, tipo):
            problemas.append(f"{rid}: campo '{campo}' deveria ser {tipo.__name__}")
        elif isinstance(valor, str) and not valor.strip():
            problemas.append(f"{rid}: campo '{campo}' está vazio")
        elif isinstance(valor, list) and campo != "relacionados":
            if not valor or not all(isinstance(x, str) and x.strip() for x in valor):
                problemas.append(f"{rid}: campo '{campo}' precisa ser uma lista de textos não vazia")

    if isinstance(reg.get("id"), str) and not FORMATO_ID.match(reg["id"]):
        problemas.append(f"{rid}: id fora do formato (ex.: DOC001)")
    if isinstance(reg.get("tema"), str) and reg["tema"] not in categorias:
        problemas.append(f"{rid}: tema '{reg['tema']}' não está nas categorias")
    if isinstance(reg.get("data_verificacao"), str) and not _validar_data(reg["data_verificacao"]):
        problemas.append(f"{rid}: data_verificacao deve estar no formato AAAA-MM-DD")

    fonte = reg.get("fonte")
    if isinstance(fonte, dict):
        if not isinstance(fonte.get("nome"), str) or not fonte["nome"].strip():
            problemas.append(f"{rid}: fonte sem nome do órgão")
        if not validar_url(fonte.get("url")):
            problemas.append(f"{rid}: fonte com URL inválida (use https://...)")
    return problemas


def validar_dados_base(dados: object) -> list[str]:
    """Valida a estrutura completa da base. Lista vazia = base válida."""
    if not isinstance(dados, dict):
        return ["a raiz do JSON precisa ser um objeto"]
    categorias = dados.get("categorias")
    registros = dados.get("registros")
    problemas: list[str] = []
    if not isinstance(categorias, dict) or not categorias:
        problemas.append("'categorias' precisa ser um objeto não vazio")
        categorias = {}
    if not isinstance(registros, list) or not registros:
        return problemas + ["'registros' precisa ser uma lista não vazia"]

    for i, reg in enumerate(registros):
        problemas.extend(_validar_registro(reg, i, categorias))

    # Duplicidades e referências (consideram somente registros com id textual)
    ids_vistos: set[str] = set()
    titulos_vistos: dict[str, str] = {}
    for reg in registros:
        if not isinstance(reg, dict) or not isinstance(reg.get("id"), str):
            continue
        rid = reg["id"]
        if rid in ids_vistos:
            problemas.append(f"{rid}: id duplicado")
        ids_vistos.add(rid)
        if isinstance(reg.get("titulo"), str) and reg["titulo"].strip():
            chave = _normalizar_titulo(reg["titulo"])
            if chave in titulos_vistos and titulos_vistos[chave] != rid:
                problemas.append(f"{rid}: título repetido de {titulos_vistos[chave]}")
            titulos_vistos.setdefault(chave, rid)

    for reg in registros:
        if not isinstance(reg, dict) or not isinstance(reg.get("relacionados"), list):
            continue
        for ref in reg["relacionados"]:
            if ref == reg.get("id"):
                problemas.append(f"{ref}: relacionado a si mesmo")
            elif ref not in ids_vistos:
                problemas.append(f"{reg.get('id')}: relacionado '{ref}' não existe")
    return problemas


def validar_entrada(texto: str | None) -> str:
    """Valida o texto digitado pelo cidadão e devolve a versão limpa."""
    if texto is None or not texto.strip():
        raise EntradaInvalida("A consulta está vazia. Digite uma pergunta, por exemplo: 'Como tirar o passaporte?'.")
    if any(unicodedata.category(c) == "Cc" and c not in "\t\n\r" for c in texto):
        raise EntradaInvalida("A consulta contém caracteres inválidos. Use apenas texto comum.")
    limpo = " ".join(texto.split())
    if len(limpo) > TAMANHO_MAXIMO_ENTRADA:
        raise EntradaInvalida(f"A consulta está longa demais (máximo de {TAMANHO_MAXIMO_ENTRADA} caracteres).")
    if not any(c.isalnum() for c in limpo):
        raise EntradaInvalida("A consulta precisa ter letras ou números.")
    return limpo


def validar_opcao_menu(texto: str | None, opcoes: set[str]) -> str:
    """Confere se a opção digitada existe no menu."""
    opcao = (texto or "").strip()
    if opcao not in opcoes:
        validas = ", ".join(sorted(opcoes, key=lambda o: (len(o), o)))
        raise EntradaInvalida(f"A opção '{opcao}' não existe. Escolha uma destas: {validas}.")
    return opcao
