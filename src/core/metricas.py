"""Avaliação automática do Citizen Assist AI.

Executa os cenários de data/testes.json no núcleo real, classifica cada
resultado comparando com o comportamento esperado e calcula os indicadores.
Nenhum número é digitado à mão: tudo sai da execução.

Classificação:
- correta ............. respondeu a orientação esperada (ou ofereceu as opções esperadas)
- incorreta ........... respondeu algo diferente do esperado, ou respondeu quando devia se abster
- abstencao_correta ... não respondeu, e a consulta não tinha suporte na base
- abstencao_incorreta . não respondeu (ou só ofereceu opções), mas a base tinha a orientação
- falha_tecnica ....... exceção durante a consulta
"""

from __future__ import annotations

import json
import statistics
import subprocess
from datetime import datetime
from pathlib import Path

from core.base_conhecimento import RAIZ_PROJETO
from core.respostas import Assistente, ResultadoConsulta

CAMINHO_CENARIOS = RAIZ_PROJETO / "data" / "testes.json"
CAMINHO_RESULTADOS = RAIZ_PROJETO / "data" / "resultados_testes.json"
STATUS_ABSTENCAO = {"sem_resultado", "entrada_invalida"}


def carregar_cenarios(caminho: Path = CAMINHO_CENARIOS) -> list[dict]:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def _ids_opcoes(resultado: ResultadoConsulta) -> list[str]:
    return [c.registro_id for c in resultado.opcoes]


def classificar(cenario: dict, resultado: ResultadoConsulta) -> str:
    esperado = cenario.get("orientacao_esperada")
    comportamento = cenario.get("comportamento_esperado", "responder" if esperado else "abster")

    if comportamento == "abster":
        return "abstencao_correta" if resultado.status in STATUS_ABSTENCAO else "incorreta"

    if comportamento == "opcoes":
        esperadas = set(cenario.get("opcoes_esperadas", []))
        if resultado.status in ("ambiguo", "baixa_confianca") and esperadas <= set(_ids_opcoes(resultado)):
            return "correta"
        if resultado.status in STATUS_ABSTENCAO:
            return "abstencao_incorreta"
        return "incorreta"

    # comportamento == "responder"
    if resultado.status == "encontrado":
        return "correta" if resultado.resposta.registro_id == esperado else "incorreta"
    if resultado.status in ("ambiguo", "baixa_confianca"):
        # Ofereceu opções em vez de responder: não conta como acerto.
        return "abstencao_incorreta"
    return "abstencao_incorreta"


def _descrever(resultado: ResultadoConsulta) -> str:
    if resultado.status == "encontrado":
        return f"encontrado: {resultado.resposta.registro_id}"
    if resultado.opcoes:
        return f"{resultado.status}: opções {', '.join(_ids_opcoes(resultado))}"
    return resultado.status


def _proporcao(parte: int, total: int) -> float | None:
    return round(parte / total, 4) if total else None


def calcular_indicadores(registros: list[dict]) -> dict:
    total = len(registros)
    contagem = {c: sum(1 for r in registros if r["classificacao"] == c) for c in
                ("correta", "incorreta", "abstencao_correta", "abstencao_incorreta", "falha_tecnica")}
    corretas = contagem["correta"] + contagem["abstencao_correta"]
    respondiveis = [r for r in registros if r["comportamento_esperado"] != "abster"]
    devem_abster = [r for r in registros if r["comportamento_esperado"] == "abster"]
    tempos = [r["tempo_ms"] for r in registros if r.get("tempo_ms") is not None]
    return {
        "total_testes": total,
        "total_corretas": corretas,
        "total_incorretas": total - corretas,
        "detalhe_classificacoes": contagem,
        "taxa_acerto": _proporcao(corretas, total),
        "taxa_cobertura": _proporcao(sum(1 for r in respondiveis if r["respondeu"]), len(respondiveis)),
        "taxa_abstencao_correta": _proporcao(contagem["abstencao_correta"], len(devem_abster)),
        "tempo_medio_ms": round(statistics.fmean(tempos), 4) if tempos else None,
        "tempo_min_ms": round(min(tempos), 4) if tempos else None,
        "tempo_max_ms": round(max(tempos), 4) if tempos else None,
    }


def executar_avaliacao(assistente: Assistente, cenarios: list[dict], modelo: str = "B") -> dict:
    resultados = []
    for cenario in cenarios:
        comportamento = cenario.get("comportamento_esperado", "responder")
        try:
            resultado = assistente.consultar(cenario["pergunta"], modelo=modelo)
        except Exception as erro:  # registrado como falha técnica, nunca escondido
            resultados.append({**_cabecalho(cenario, comportamento), "resultado_obtido": f"erro: {erro}",
                               "classificacao": "falha_tecnica", "tempo_ms": None, "respondeu": False,
                               "observacoes": cenario.get("observacao", "")})
            continue
        resultados.append({
            **_cabecalho(cenario, comportamento),
            "resultado_obtido": _descrever(resultado),
            "classificacao": classificar(cenario, resultado),
            "tempo_ms": round(resultado.tempo_ms, 4),
            "respondeu": resultado.status not in STATUS_ABSTENCAO,
            "observacoes": cenario.get("observacao", ""),
        })
    return {"modelo_usado": modelo, "indicadores": calcular_indicadores(resultados), "resultados": resultados}


def _cabecalho(cenario: dict, comportamento: str) -> dict:
    return {
        "id": cenario["id"],
        "tipo": cenario.get("tipo", ""),
        "pergunta": cenario["pergunta"],
        "categoria_esperada": cenario.get("categoria_esperada"),
        "orientacao_esperada": cenario.get("orientacao_esperada") or cenario.get("opcoes_esperadas"),
        "comportamento_esperado": comportamento,
    }


def comparar_modelos(assistente: Assistente, perguntas: list[str]) -> dict:
    """Compara A e B nas mesmas perguntas, com medidas objetivas da resposta."""
    medidas: dict[str, list[dict]] = {"A": [], "B": []}
    fontes_consistentes = True
    for pergunta in perguntas:
        respostas = {}
        for modelo in ("A", "B"):
            resultado = assistente.consultar(pergunta, modelo=modelo)
            if resultado.resposta is None:
                break
            r = resultado.resposta
            respostas[modelo] = r
            palavras = sum(len((s.conteudo if isinstance(s.conteudo, str) else " ".join(s.conteudo)).split())
                           for s in r.secoes)
            titulos = {s.titulo for s in r.secoes}
            medidas[modelo].append({
                "secoes": len(r.secoes),
                "palavras": palavras,
                "tem_fonte": "Fonte oficial" in titulos,
                "tem_aviso": "Aviso" in titulos,
                "tem_limitacoes": "Limitações e ressalvas" in titulos,
                "tem_relacionados": "Assuntos relacionados" in titulos,
            })
        if len(respostas) == 2 and respostas["A"].fonte != respostas["B"].fonte:
            fontes_consistentes = False

    def resumo(lista: list[dict]) -> dict:
        n = len(lista)
        return {
            "consultas": n,
            "media_secoes": round(statistics.fmean(m["secoes"] for m in lista), 2) if n else None,
            "media_palavras": round(statistics.fmean(m["palavras"] for m in lista), 1) if n else None,
            "com_fonte": sum(m["tem_fonte"] for m in lista),
            "com_aviso": sum(m["tem_aviso"] for m in lista),
            "com_limitacoes": sum(m["tem_limitacoes"] for m in lista),
            "com_relacionados": sum(m["tem_relacionados"] for m in lista),
        }

    return {"A": resumo(medidas["A"]), "B": resumo(medidas["B"]), "fontes_consistentes": fontes_consistentes}


CAMINHO_USABILIDADE = RAIZ_PROJETO / "data" / "usabilidade.json"
RESULTADOS_USABILIDADE = {"concluiu", "com_dificuldade", "nao_concluiu"}


def carregar_usabilidade(caminho: Path = CAMINHO_USABILIDADE) -> dict:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))


def calcular_usabilidade(dados: dict) -> dict:
    """Indicadores de facilidade de uso a partir das sessões REAIS registradas.

    Sem sessões registradas, o status fica "pendente" e nenhum número é gerado.
    """
    sessoes = dados.get("sessoes", [])
    resultados = [r for s in sessoes for r in s.get("resultados", [])]
    for r in resultados:
        if r.get("resultado") not in RESULTADOS_USABILIDADE:
            raise ValueError(f"Resultado de usabilidade inválido: {r.get('resultado')!r} "
                             f"(use {', '.join(sorted(RESULTADOS_USABILIDADE))}).")
    if not resultados:
        return {"status": "pendente", "participantes": 0, "tarefas_registradas": 0,
                "taxa_conclusao_sem_ajuda": None, "taxa_conclusao_total": None,
                "tempo_medio_tarefa_s": None, "nota_media_facilidade": None, "dificuldades": []}
    tempos = [r["tempo_s"] for r in resultados if isinstance(r.get("tempo_s"), (int, float))]
    notas = [s["nota_facilidade"] for s in sessoes if isinstance(s.get("nota_facilidade"), (int, float))]
    return {
        "status": "realizado",
        "participantes": len(sessoes),
        "tarefas_registradas": len(resultados),
        "taxa_conclusao_sem_ajuda": _proporcao(sum(r["resultado"] == "concluiu" for r in resultados), len(resultados)),
        "taxa_conclusao_total": _proporcao(sum(r["resultado"] != "nao_concluiu" for r in resultados), len(resultados)),
        "tempo_medio_tarefa_s": round(statistics.fmean(tempos), 1) if tempos else None,
        "nota_media_facilidade": round(statistics.fmean(notas), 2) if notas else None,
        "dificuldades": [f"{r['tarefa']}: {r['dificuldade']}" for r in resultados if r.get("dificuldade")],
    }


def carregar_resultados(caminho: Path = CAMINHO_RESULTADOS) -> dict | None:
    """Últimos resultados gerados por `python src/avaliar.py` (None se não existir)."""
    try:
        return json.loads(Path(caminho).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def versao_codigo() -> str:
    try:
        saida = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ_PROJETO,
                               capture_output=True, text=True, timeout=5)
        return saida.stdout.strip() if saida.returncode == 0 and saida.stdout.strip() else "sem-git"
    except (OSError, subprocess.SubprocessError):
        return "sem-git"


def gerar_relatorio(assistente: Assistente | None = None, caminho_saida: Path = CAMINHO_RESULTADOS) -> dict:
    assistente = assistente or Assistente()
    cenarios = carregar_cenarios()
    avaliacao = executar_avaliacao(assistente, cenarios, modelo="B")
    perguntas_comparacao = [c["pergunta"] for c in cenarios if c.get("comportamento_esperado") == "responder"]
    relatorio = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "versao_codigo": versao_codigo(),
        "observacao": "Arquivo gerado automaticamente por `python src/avaliar.py`. Não editar à mão.",
        **avaliacao,
        "comparacao_modelos": comparar_modelos(assistente, perguntas_comparacao),
        "usabilidade": calcular_usabilidade(carregar_usabilidade()),
    }
    Path(caminho_saida).write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding="utf-8")
    return relatorio
