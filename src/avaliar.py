"""Executa a avaliação automática e grava data/resultados_testes.json.

Uso (a partir da raiz do projeto):
    python src/avaliar.py
"""

import sys

from core.erros import CitizenAssistError
from core.metricas import CAMINHO_RESULTADOS, gerar_relatorio


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        relatorio = gerar_relatorio()
    except CitizenAssistError as erro:
        print(f"Não foi possível executar a avaliação: {erro}")
        return 1
    ind = relatorio["indicadores"]
    print(f"Avaliação gravada em {CAMINHO_RESULTADOS}")
    print(f"Testes: {ind['total_testes']} | corretas: {ind['total_corretas']} | incorretas: {ind['total_incorretas']}")
    print(f"Taxa de acerto: {ind['taxa_acerto']} | cobertura: {ind['taxa_cobertura']} | "
          f"abstenção correta: {ind['taxa_abstencao_correta']}")
    print(f"Tempo (ms): médio {ind['tempo_medio_ms']} | mínimo {ind['tempo_min_ms']} | máximo {ind['tempo_max_ms']}")
    usab = relatorio["usabilidade"]
    if usab["status"] == "pendente":
        print("Facilidade de uso: PENDENTE (nenhuma sessão real registrada em data/usabilidade.json)")
    else:
        print(f"Facilidade de uso: {usab['participantes']} participante(s) | concluídas sem ajuda: "
              f"{usab['taxa_conclusao_sem_ajuda']} | nota média: {usab['nota_media_facilidade']}")
    for item in relatorio["resultados"]:
        if item["classificacao"] not in ("correta", "abstencao_correta"):
            print(f"  - {item['id']} [{item['classificacao']}] {item['pergunta']!r} -> {item['resultado_obtido']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
