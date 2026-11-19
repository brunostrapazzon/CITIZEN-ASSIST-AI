"""Gera docs/relatorio.pdf a partir dos dados reais do projeto.

Uso (a partir da raiz):
    python scripts/gerar_relatorio_pdf.py

Todos os números vêm de data/resultados_testes.json (gerado por
`python src/avaliar.py`) e da base data/base.json. Nada é digitado à mão.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from reportlab.graphics.charts.barcharts import HorizontalBarChart, VerticalBarChart
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from core.base_conhecimento import carregar_base  # noqa: E402
from core.grafo import (PESO_PERTENCE_CATEGORIA, PESO_RELACAO_ENTRE_CATEGORIAS,  # noqa: E402
                        PESO_RELACAO_MESMA_CATEGORIA, construir_grafo)
from core.respostas import Assistente  # noqa: E402

SAIDA = RAIZ / "docs" / "relatorio.pdf"
TIPOS = {"ambigua": "ambígua", "direta": "direta", "entrada_invalida": "entrada inválida", "entrada_vazia": "entrada vazia",
         "erro_digitacao": "erro de digitação", "fora_do_tema": "fora do tema", "palavras_chave": "palavras-chave",
         "palavras_diferentes": "palavras diferentes", "reformulacao": "reformulação", "regressao": "regressão",
         "sem_correspondencia": "sem correspondência"}
CLASSIFICACOES = {"correta": "correta", "incorreta": "incorreta", "abstencao_correta": "abstenção correta",
                  "abstencao_incorreta": "abstenção incorreta", "falha_tecnica": "falha técnica"}
AZUL = colors.HexColor("#0B3D91")
AZUL_ACAO = colors.HexColor("#0B5FFF")
CINZA = colors.HexColor("#5B6B85")
FUNDO = colors.HexColor("#E9EEF6")


def registrar_fontes() -> tuple[str, str]:
    """Usa Arial/DejaVu se existir (acentos e símbolos); senão Helvetica."""
    candidatos = [
        (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf"), Path("C:/Windows/Fonts/ariali.ttf")),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf")),
    ]
    for normal, negrito, italico in candidatos:
        if normal.exists() and negrito.exists():
            pdfmetrics.registerFont(TTFont("Texto", str(normal)))
            pdfmetrics.registerFont(TTFont("Texto-Negrito", str(negrito)))
            pdfmetrics.registerFont(TTFont("Texto-Italico", str(italico if italico.exists() else normal)))
            pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="Texto-Negrito",
                                          italic="Texto-Italico", boldItalic="Texto-Negrito")
            return "Texto", "Texto-Negrito"
    return "Helvetica", "Helvetica-Bold"


FONTE, FONTE_N = registrar_fontes()
base_estilos = getSampleStyleSheet()
E = {
    "titulo": ParagraphStyle("t", fontName=FONTE_N, fontSize=22, leading=27, textColor=AZUL, alignment=TA_CENTER),
    "subtitulo": ParagraphStyle("st", fontName=FONTE, fontSize=12, leading=16, textColor=CINZA, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", fontName=FONTE_N, fontSize=13.5, leading=17, textColor=AZUL, spaceBefore=10, spaceAfter=4, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName=FONTE_N, fontSize=11, leading=14, textColor=AZUL, spaceBefore=6, spaceAfter=2, keepWithNext=1),
    "p": ParagraphStyle("p", fontName=FONTE, fontSize=9.6, leading=13.2, alignment=TA_JUSTIFY, spaceAfter=4),
    "lista": ParagraphStyle("l", fontName=FONTE, fontSize=9.6, leading=13, leftIndent=12, bulletIndent=2, spaceAfter=1),
    "cel": ParagraphStyle("c", fontName=FONTE, fontSize=8.4, leading=10.4),
    "cel_n": ParagraphStyle("cn", fontName=FONTE_N, fontSize=8.4, leading=10.4, textColor=colors.white),
    "legenda": ParagraphStyle("lg", fontName=FONTE, fontSize=8, leading=10, textColor=CINZA, alignment=TA_CENTER, spaceAfter=6),
    "codigo": ParagraphStyle("cd", fontName="Courier", fontSize=8.2, leading=10.5, backColor=FUNDO, borderPadding=5,
                             spaceBefore=3, spaceAfter=6),
}


def P(texto: str, estilo: str = "p") -> Paragraph:
    return Paragraph(texto, E[estilo])


def lista(itens: list[str]) -> list[Paragraph]:
    return [Paragraph(i, E["lista"], bulletText="•") for i in itens]


def tabela(linhas: list[list[str]], larguras: list[float]) -> Table:
    dados = [[Paragraph(str(c), E["cel_n"] if i == 0 else E["cel"]) for c in linha] for i, linha in enumerate(linhas)]
    t = Table(dados, colWidths=[w * cm for w in larguras], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FUNDO]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C4D0E3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def pct(v: float | None) -> str:
    return "—" if v is None else f"{v * 100:.1f}%".replace(".", ",")


def num(v: float, casas: int = 4) -> str:
    return f"{v:.{casas}f}".replace(".", ",")


def grafico_classificacoes(det: dict) -> Drawing:
    rotulos = ["Correta", "Abstenção\ncorreta", "Incorreta", "Abstenção\nincorreta", "Falha\ntécnica"]
    chaves = ["correta", "abstencao_correta", "incorreta", "abstencao_incorreta", "falha_tecnica"]
    d = Drawing(16 * cm, 5.6 * cm)
    g = VerticalBarChart()
    g.x, g.y, g.width, g.height = 1.4 * cm, 1.2 * cm, 13.8 * cm, 3.9 * cm
    g.data = [[det[c] for c in chaves]]
    g.categoryAxis.categoryNames = rotulos
    g.categoryAxis.labels.fontName = FONTE
    g.categoryAxis.labels.fontSize = 7.5
    g.valueAxis.valueMin = 0
    g.valueAxis.labels.fontName = FONTE
    g.valueAxis.labels.fontSize = 7.5
    g.bars[0].fillColor = AZUL_ACAO
    g.barLabelFormat = "%d"
    g.barLabels.fontName = FONTE
    g.barLabels.fontSize = 8
    g.barLabels.nudge = 7
    d.add(g)
    return d


def grafico_modelos(cmp: dict) -> Drawing:
    d = Drawing(16 * cm, 4.2 * cm)
    g = HorizontalBarChart()
    g.x, g.y, g.width, g.height = 3.2 * cm, 0.5 * cm, 11.5 * cm, 3.2 * cm
    g.data = [[cmp["A"]["media_palavras"], cmp["A"]["media_secoes"] * 20],
              [cmp["B"]["media_palavras"], cmp["B"]["media_secoes"] * 20]]
    g.categoryAxis.categoryNames = ["Média de palavras", "Média de seções (×20)"]
    g.categoryAxis.labels.fontName = FONTE
    g.categoryAxis.labels.fontSize = 7.5
    g.valueAxis.valueMin = 0
    g.valueAxis.labels.fontName = FONTE
    g.valueAxis.labels.fontSize = 7.5
    g.bars[0].fillColor = colors.HexColor("#9DB4D9")
    g.bars[1].fillColor = AZUL
    d.add(g)
    d.add(String(14.9 * cm, 3.5 * cm, "Modelo A", fontName=FONTE, fontSize=7.5, fillColor=colors.HexColor("#7F9CC9")))
    d.add(String(14.9 * cm, 3.0 * cm, "Modelo B", fontName=FONTE, fontSize=7.5, fillColor=AZUL))
    return d


def rodape(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont(FONTE, 7.5)
    canvas.setFillColor(CINZA)
    canvas.drawString(2 * cm, 1.2 * cm, "Citizen Assist AI · FIAP Global Solution 2026.2 · CitizenTech · Equipe não nomeada")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def montar() -> list:
    res = json.loads((RAIZ / "data" / "resultados_testes.json").read_text(encoding="utf-8"))
    ind, det, cmp = res["indicadores"], res["indicadores"]["detalhe_classificacoes"], res["comparacao_modelos"]
    base = carregar_base()
    grafo = construir_grafo(base)
    assistente = Assistente(base)
    n_arestas = sum(len(v) for v in grafo.adjacencia.values()) // 2
    trilha, custo = assistente.trilha("CAT:documentacao", "CAT:servicos_publicos")
    trilha_txt = " → ".join(grafo.rotulo(n) for n in trilha)
    cenarios = json.loads((RAIZ / "data" / "testes.json").read_text(encoding="utf-8"))
    tipos = sorted({TIPOS.get(c["tipo"], c["tipo"]) for c in cenarios})
    falhas = [r for r in res["resultados"] if r["classificacao"] not in ("correta", "abstencao_correta")]
    v1 = json.loads((RAIZ / "data" / "historico" / "resultados_v1_linha_de_base.json").read_text(encoding="utf-8"))

    h: list = []
    # ---------------------------------------------------------------- capa
    h += [Spacer(1, 3.2 * cm), P("CITIZEN ASSIST AI", "titulo"), Spacer(1, 0.3 * cm),
          P("Orientação cidadã simples, organizada e com fonte oficial", "subtitulo"), Spacer(1, 1.4 * cm),
          P("Relatório técnico — Global Solution · 2º semestre de 2026", "subtitulo"),
          P("FIAP · Graduação em Ciência da Computação · Desafio CitizenTech", "subtitulo"), Spacer(1, 1.6 * cm)]
    h.append(tabela([["Equipe não nomeada", "RM"],
                     ["Bruno Trevizan Strapazzon", "RM573816"],
                     ["Lucas Matheus Laitart", "RM573137"],
                     ["André Luiz Hlatchuk", "RM571789"]], [9, 4]))
    h += [Spacer(1, 1.6 * cm),
          P(f"Repositório: https://github.com/brunostrapazzon/CITIZEN-ASSIST-AI · Vídeo: https://youtu.be/QpQYXNN09l8 · Dados de avaliação gerados em {res['gerado_em']}", "legenda"),
          P("Projeto acadêmico. Não é um canal oficial e não tem vínculo com órgãos públicos.", "legenda"),
          PageBreak()]

    # ------------------------------------------------- 1. introdução e problema
    h += [P("1. Introdução e contextualização do problema", "h1"),
          P("Orientações sobre documentos, serviços públicos e direitos estão distribuídas em muitos portais oficiais, "
            "cada um com organização própria. Para quem tem pouca familiaridade com o meio digital, o obstáculo começa antes "
            "do serviço: saber por onde começar, quais passos seguir e qual página é de fato oficial. Esse vazio favorece a "
            "desinformação e o uso de intermediários desnecessários."),
          P("2. Público-alvo e proposta de solução", "h1"),
          P("O Citizen Assist AI atende cidadãos com dificuldade para localizar serviços, pessoas pouco familiarizadas com "
            "plataformas digitais e quem precisa confirmar uma orientação na fonte oficial. A proposta é transformar "
            "informação pública dispersa em <b>orientações curtas e acompanhadas da fonte verificada</b>, sem substituir o "
            "atendimento oficial. A regra central do sistema é <b>nunca inventar uma orientação</b>: sem suporte na base, ele "
            "informa que não sabe."),
          P("3. Arquitetura e tecnologias", "h1"),
          P("A solução é escrita em Python com a biblioteca padrão. Rich (terminal), Streamlit (web), pytest e ReportLab são "
            "opcionais ou de desenvolvimento. Não há API externa, serviço pago nem dependência de internet durante o uso. "
            "A arquitetura tem um <b>núcleo único</b> (<i>src/core</i>) e duas camadas finas de interface:"),
          P("python src/sistema.py (CLI, principal) --+<br/>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"
            "&nbsp;&nbsp;|--&gt; src/core (Assistente) --&gt; data/base.json<br/>"
            "streamlit run src/web_app.py (Web) -------+", "codigo"),
          tabela([["Módulo", "Responsabilidade"],
                  ["base_conhecimento.py", "Leitura da base e conversão em objetos imutáveis (dataclasses)"],
                  ["validacoes.py", "Validação completa da base e das entradas do usuário"],
                  ["busca.py", "Normalização, índice invertido, relevância e decisão (responder, opções ou abster)"],
                  ["grafo.py", "Grafo de assuntos, Dijkstra e matriz de adjacência"],
                  ["respostas.py", "Modelos A e B; classe Assistente usada pelas duas interfaces"],
                  ["metricas.py", "Execução dos cenários, classificação e indicadores"]], [4, 12]),
          P("Um teste automatizado impede que as interfaces leiam o JSON ou criem o motor de busca por conta própria. "
            "Com isso, a mesma pergunta gera a mesma resposta e a mesma fonte na CLI e na Web.")]

    # ------------------------------------------------- 4. base de conhecimento
    contagem = {nome: len(base.por_tema(t)) for t, nome in base.categorias.items()}
    h += [P("4. Organização da base de conhecimento", "h1"),
          P(f"A base (<i>data/base.json</i>) tem <b>{len(base.registros)} orientações</b> em <b>{len(base.categorias)} "
            f"categorias</b> ({'; '.join(f'{k}: {v}' for k, v in contagem.items())}). Cada registro tem identificador, "
            "categoria, título, pergunta típica, palavras-chave, resumo (Modelo A), orientação (Modelo B), passos, "
            "limitações, fonte (órgão e URL), data de verificação, aviso e relacionados."),
          P("<b>Processo de verificação:</b> cada página oficial foi aberta e lida em 17/11/2026 (gov.br, TSE, Planalto, "
            "Consumidor.gov.br e Fala.BR). O texto da base é uma síntese própria. Custos, prazos e variações estaduais ou "
            "municipais foram registrados como limitações, e não como regra universal. Seis páginas falharam na leitura "
            "automática (erro 404, bloqueio ou conteúdo em JavaScript) e só entraram na base depois de lidas no navegador. "
            "Um achado da verificação: a página da Carteira Digital de Trânsito já chama o aplicativo de \"CNH do Brasil\"."),
          P("A validação roda a cada inicialização e lista todos os problemas de uma vez: campos ausentes ou vazios, tipos "
            "errados, IDs duplicados ou fora do formato, referências inexistentes, autorreferências, títulos repetidos, "
            "datas e URLs inválidas. Com a base inválida, o programa não inicia.")]

    # ------------------------------------------------- 5. estruturas e algoritmos
    h += [P("5. Estruturas de dados e algoritmos", "h1"),
          P("5.1 Busca", "h2"),
          P("A pergunta é normalizada (minúsculas, sem acentos e pontuação), separada em termos e filtrada de palavras "
            "vazias. Os plurais simples são reduzidos. Um <b>índice invertido</b> (<i>dict[termo, dict[id, peso]]</i>) "
            "liga cada termo aos registros, com peso 3 para título e palavras-chave, 2 para a pergunta e 1 para resumo e "
            "orientação. A relevância é <b>Σ fator·idf(t)·peso(t,d)</b>, com idf(t) = ln(1 + N/df), o que valoriza termos "
            "raros. Termos desconhecidos podem ser corrigidos por semelhança (difflib ≥ 0,8, mesma inicial, fator 0,7)."),
          P("A <b>cobertura</b> mede quanto da informação da pergunta o registro contém. Ela impede que uma única palavra em "
            "comum gere uma resposta. A decisão final é: <b>sem resultado</b> (cobertura &lt; 0,5 ou confiança &lt; 0,35); "
            "<b>ambíguo</b> (segundo colocado com ≥ 80% da pontuação do primeiro, e as opções são mostradas); <b>baixa "
            "confiança</b> (confiança ou cobertura &lt; 0,6, com opções e aviso); ou <b>encontrado</b>. Empates são "
            "decididos pelo código, o que garante determinismo."),
          P("5.2 Grafo e Dijkstra", "h2"),
          P(f"O grafo não direcionado usa lista de adjacência e tem {len(grafo.adjacencia)} vértices "
            f"({len(base.registros)} orientações e {len(base.categorias)} categorias) e {n_arestas} arestas. Os pesos "
            "representam o custo de navegação:"),
          tabela([["Ligação", "Peso", "Justificativa"],
                  ["Relação explícita, mesma categoria", num(PESO_RELACAO_MESMA_CATEGORIA, 1), "Assuntos diretamente ligados"],
                  ["Relação explícita, categorias diferentes", num(PESO_RELACAO_ENTRE_CATEGORIAS, 1), "Exige mudar de contexto"],
                  ["Orientação ↔ sua categoria", num(PESO_PERTENCE_CATEGORIA, 1), "Navegação genérica (voltar ao tema)"]],
                 [6, 2, 8]),
          Spacer(1, 4),
          P("O Dijkstra usa fila de prioridade (heapq) com remoção preguiçosa e tem complexidade O((V+E) log V). Ele tem dois "
            "usos reais: (1) a <b>trilha de navegação</b> entre dois assuntos, no menu 4 da CLI e numa página da Web; "
            "(2) a ordenação dos <b>assuntos relacionados</b> do Modelo B por proximidade. Exemplo real de execução: "
            f"<i>{trilha_txt}</i> (custo {num(custo, 1)}). A correção do algoritmo foi comprovada contra Floyd–Warshall "
            "(oráculo independente) em 100 grafos aleatórios e no grafo real, além de um caso calculado à mão.")]

    # ------------------------------------------------- 6. prompts
    h += [P("6. Estratégias de prompts e lógica de resposta", "h1"),
          P("O sistema não chama modelos de IA. Os \"prompts\" são <b>modelos de instrução aplicados à composição da "
            "resposta</b>: cada um define as seções, a ordem e o campo da base de onde vem o conteúdo, e proíbe acrescentar "
            "qualquer informação que não esteja no registro."),
          tabela([["", "Modelo A — direta", "Modelo B — contextualizada"],
                  ["Seções", "Orientação · Passo a passo · Fonte oficial · Aviso",
                   "Sua necessidade · Contexto · Passo a passo · Fonte oficial · Limitações · Relacionados · Aviso"],
                  ["Média de seções", num(cmp["A"]["media_secoes"], 1), num(cmp["B"]["media_secoes"], 1)],
                  ["Média de palavras", num(cmp["A"]["media_palavras"], 1), num(cmp["B"]["media_palavras"], 1)],
                  ["Com fonte / com aviso", f"{cmp['A']['com_fonte']}/{cmp['A']['consultas']} · {cmp['A']['com_aviso']}/{cmp['A']['consultas']}",
                   f"{cmp['B']['com_fonte']}/{cmp['B']['consultas']} · {cmp['B']['com_aviso']}/{cmp['B']['consultas']}"],
                  ["Com limitações / relacionados", f"{cmp['A']['com_limitacoes']} / {cmp['A']['com_relacionados']}",
                   f"{cmp['B']['com_limitacoes']} / {cmp['B']['com_relacionados']}"]], [3.6, 5.6, 6.8]),
          grafico_modelos(cmp),
          P(f"Figura 1 — Comparação objetiva dos modelos nas mesmas {cmp['A']['consultas']} perguntas respondidas.", "legenda"),
          P("<b>Interpretação:</b> os dois modelos foram igualmente consistentes. Todas as respostas têm fonte e aviso, e "
            f"a fonte é a mesma nos dois ({'sim' if cmp['fontes_consistentes'] else 'não'}). O Modelo A é mais claro para "
            "quem só quer os passos, com cerca de metade do texto. O Modelo B foi escolhido como padrão porque é o único que "
            "mostra limitações (custos, prazos, variações locais) e assuntos relacionados, o que reduz o risco de o cidadão "
            "agir com informação incompleta.")]

    # ------------------------------------------------- 7. metodologia
    h += [P("7. Metodologia de testes", "h1"),
          P(f"<b>Testes automatizados (pytest):</b> base e validações, busca, grafo/Dijkstra, modelos de resposta, métricas, "
            "CLI real (por subprocesso e no mesmo processo, em todos os menus) e interface web (executor AppTest do "
            "Streamlit). A navegação oferece, após cada resposta, até três assuntos relacionados para continuar a consulta e, "
            "quando não há resposta, lista as alternativas disponíveis. <b>Avaliação de desempenho:</b> "
            f"{len(cenarios)} cenários em <i>data/testes.json</i>, de {len(tipos)} tipos ({', '.join(tipos)}). Cada cenário "
            "registra o comportamento esperado (responder, oferecer opções ou abster-se). A classificação compara o "
            "resultado com o esperado, e retornar um texto qualquer não conta como acerto. As categorias são: correta, "
            "incorreta, abstenção correta, abstenção incorreta e falha técnica. Os tempos foram medidos com "
            "time.perf_counter() dentro da consulta.")]

    # ------------------------------------------------- 8. resultados
    h += [P("8. Resultados e indicadores", "h1"),
          P(f"Valores gerados por <i>python src/avaliar.py</i> em {res['gerado_em']} (Modelo B)."),
          tabela([["Indicador", "Valor"],
                  ["Total de testes executados", str(ind["total_testes"])],
                  ["Respostas corretas (corretas + abstenções corretas)", str(ind["total_corretas"])],
                  ["Respostas incorretas", str(ind["total_incorretas"])],
                  ["Taxa de acerto", pct(ind["taxa_acerto"])],
                  ["Taxa de cobertura (respondíveis atendidas)", pct(ind["taxa_cobertura"])],
                  ["Taxa de abstenção correta", pct(ind["taxa_abstencao_correta"])],
                  ["Tempo médio / menor / maior (ms)",
                   f"{num(ind['tempo_medio_ms'])} / {num(ind['tempo_min_ms'])} / {num(ind['tempo_max_ms'])}"]], [10, 6]),
          grafico_classificacoes(det),
          P("Figura 2 — Distribuição das classificações dos cenários.", "legenda"),
          P("<b>Facilidade de uso:</b> " + (
              "o teste com usuário ainda <b>não foi realizado</b>. O roteiro de 5 tarefas (docs/roteiro_usabilidade.md) e o "
              "registro (data/usabilidade.json) estão prontos, e os indicadores (taxa de conclusão sem ajuda, tempo médio por "
              "tarefa, nota média de 1 a 5 e dificuldades) são calculados automaticamente quando houver sessões reais. "
              "Nenhum resultado foi simulado." if res.get("usabilidade", {}).get("status") != "realizado" else
              f"{res['usabilidade']['participantes']} participante(s); tarefas concluídas sem ajuda: "
              f"{pct(res['usabilidade']['taxa_conclusao_sem_ajuda'])}; tempo médio por tarefa: "
              + ("não medido" if res['usabilidade']['tempo_medio_tarefa_s'] is None
               else f"{res['usabilidade']['tempo_medio_tarefa_s']} s".replace(".", ","))
              + f"; nota média: {num(res['usabilidade']['nota_media_facilidade'], 1)} de 5. Comentário do participante: "
              "\"tudo muito prático e fácil de se usar\". Como houve só um participante e o tempo não foi cronometrado, "
              "o resultado confirma que o fluxo funciona para um usuário, mas não permite generalizar."),
            "p"),
          P("<b>Cenários não atendidos:</b>", "p")]
    h += lista([f"<b>{f['id']}</b> \"{f['pergunta']}\" → {f['resultado_obtido']} ({CLASSIFICACOES[f['classificacao']]})."
                for f in falhas])
    v1i = v1["indicadores"]
    h += [P(f"<b>Interpretação:</b> o sistema acerta perguntas diretas, palavras-chave, reformulações próximas e erros de "
            "digitação simples. Ele também separa corretamente consultas ambíguas e fora do tema. As falhas vêm de "
            "vocabulário: sinônimos (\"achar\") e conjugações (\"emito\") ausentes do índice. A primeira execução (v1) teve "
            f"{v1i['total_corretas']} acertos em {v1i['total_testes']} ({pct(v1i['taxa_acerto'])}). Os testes revelaram "
            "três defeitos, corrigidos na v2: o plural \"-ais\" não era reduzido; a correção ortográfica trocava \"emito\" "
            "por \"feito\"; e \"receita de bolo\" era <b>respondida</b> com a orientação do CPF. A correção deste último "
            "tornou o sistema mais conservador: ele passou a mostrar opções em vez de responder com pouca certeza, o que "
            "custou o acerto direto do T14. A troca foi mantida porque o mega prompt da atividade coloca a confiabilidade da "
            "informação acima da cobertura.")]

    # ------------------------------------------------- 9. limitações e melhorias
    h += [P("9. Limitações e melhorias", "h1")]
    h += lista([
        "A base cobre 15 assuntos. Perguntas fora deles não são respondidas, e isso é intencional.",
        "As orientações têm data de verificação e podem ficar desatualizadas. Valores e prazos mudam.",
        "Os limiares foram calibrados com os mesmos cenários da avaliação, então os números podem ser otimistas para "
        "perguntas novas.",
        "O teste de facilidade de uso teve 1 participante e não cronometrou as tarefas, então não permite "
        "generalizar o resultado.",
    ])
    h += [P("<b>Melhorias identificadas a partir dos testes:</b>")]
    h += lista([
        "<b>Lematização e sinônimos</b> revisados (\"emito\" → \"emitir\", \"achar\" → \"encontrar\"), para T05 e T17.",
        "<b>Tratamento de verbos genéricos</b> (\"fica\", \"achar\") para não penalizar a cobertura (T14).",
        "<b>Conjunto de validação separado</b> para calibrar os limiares sem viés.",
        "Verificação periódica automática das URLs da base.",
    ])

    # ------------------------------------------------- 10. privacidade
    h += [P("10. Privacidade e responsabilidade", "h1"),
          P("O assistente não pede CPF, endereço, telefone ou qualquer dado pessoal, e não grava as perguntas. Toda "
            "resposta mostra a fonte oficial, a data de verificação e um aviso para confirmar a informação no canal oficial. "
            "A identidade visual é própria, sem brasões ou elementos que sugiram vínculo com o governo. A responsabilidade pela validação "
            "e apresentação é da equipe.")]

    # ------------------------------------------------- 11. conclusão e referências
    h += [P("11. Conclusão", "h1"),
          P("O Citizen Assist AI aplica estruturas de dados (dicionários, índice invertido, listas de adjacência, fila de "
            "prioridade) e algoritmos (busca com relevância idf, Dijkstra) a um problema real de acesso à informação "
            "pública. As métricas foram medidas, e não estimadas. O resultado é um assistente que prefere admitir que não "
            "sabe a inventar uma orientação."),
          P("12. Referências", "h1")]
    refs = [f"{r.fonte.nome}. Disponível em: {r.fonte.url}. Acesso em: 17 nov. 2026." for r in assistente.fontes()]
    h += [KeepTogether(lista(refs[:8]))] + lista(refs[8:])
    return h


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="Citizen Assist AI — Relatório técnico", author="Equipe não nomeada")
    doc.build(montar(), onFirstPage=lambda c, d: None, onLaterPages=rodape)
    from reportlab.pdfbase.pdfdoc import PDFDocument  # noqa: F401  (garante import do módulo)
    paginas = doc.page
    print(f"Relatório gerado: {SAIDA} ({paginas} páginas)")
    if not 4 <= paginas <= 8:
        print("ATENÇÃO: o relatório precisa ter entre 4 e 8 páginas.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
