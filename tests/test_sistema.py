"""Testes de integração: núcleo de respostas, CLI e consistência entre interfaces."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from core.metricas import calcular_indicadores, classificar, comparar_modelos, executar_avaliacao
from core.respostas import Assistente

RAIZ = Path(__file__).resolve().parents[1]


# ------------------------------------------------------------- respostas
def test_consulta_bem_sucedida_modelo_a(assistente):
    resultado = assistente.consultar("Como tirar o passaporte?", modelo="A")
    assert resultado.status == "encontrado"
    resposta = resultado.resposta
    assert resposta.modelo == "A"
    assert resposta.registro_id == "DOC004"
    titulos = [s.titulo for s in resposta.secoes]
    assert titulos == ["Orientação", "Passo a passo", "Fonte oficial", "Aviso"]


def test_consulta_bem_sucedida_modelo_b(assistente):
    resposta = assistente.consultar("Como tirar o passaporte?", modelo="B").resposta
    titulos = [s.titulo for s in resposta.secoes]
    assert titulos == [
        "Sua necessidade", "Contexto", "Passo a passo", "Fonte oficial",
        "Limitações e ressalvas", "Assuntos relacionados", "Aviso",
    ]


def test_modelos_usam_a_mesma_fonte(assistente):
    a = assistente.consultar("cadastro único", modelo="A").resposta
    b = assistente.consultar("cadastro único", modelo="B").resposta
    assert a.fonte == b.fonte


def test_modelo_invalido(assistente):
    with pytest.raises(ValueError):
        assistente.consultar("cpf", modelo="C")


def test_resposta_nunca_inventa_conteudo(assistente, base_real):
    resposta = assistente.consultar("Como tirar o passaporte?", modelo="A").resposta
    registro = base_real.obter("DOC004")
    passos = next(s for s in resposta.secoes if s.titulo == "Passo a passo").conteudo
    assert list(passos) == list(registro.passos)


@pytest.mark.parametrize("entrada", ["", "    ", "???"])
def test_entrada_invalida_vira_status(assistente, entrada):
    resultado = assistente.consultar(entrada)
    assert resultado.status == "entrada_invalida"
    assert resultado.resposta is None
    assert resultado.mensagem


def test_sem_correspondencia_informa_claramente(assistente):
    resultado = assistente.consultar("previsão do tempo amanhã")
    assert resultado.status == "sem_resultado"
    assert resultado.resposta is None
    assert "não possui" in resultado.mensagem


def test_consulta_por_id(assistente):
    resultado = assistente.consultar("SER003")
    assert resultado.status == "encontrado"
    assert resultado.resposta.registro_id == "SER003"


def test_trilha_de_navegacao(assistente):
    caminho, custo = assistente.trilha("DOC002", "SER003")
    assert caminho[0] == "DOC002" and caminho[-1] == "SER003"
    assert custo > 0


def test_tempo_medido(assistente):
    assert assistente.consultar("cpf").tempo_ms >= 0


# --------------------------------------- mesma resposta nas duas interfaces
def test_web_e_cli_usam_o_mesmo_nucleo():
    """A Web e a CLI não podem ter regras próprias de busca."""
    web = (RAIZ / "src" / "web_app.py").read_text(encoding="utf-8")
    cli = (RAIZ / "src" / "sistema.py").read_text(encoding="utf-8")
    for codigo in (web, cli):
        assert "from core.respostas import Assistente" in codigo
        assert "json.load" not in codigo
        assert "MotorBusca(" not in codigo


def test_resposta_estruturada_identica_entre_instancias(base_real):
    cenarios = json.loads((RAIZ / "data" / "testes.json").read_text(encoding="utf-8"))
    a, b = Assistente(base_real), Assistente(base_real)
    for cenario in cenarios:
        ra, rb = a.consultar(cenario["pergunta"], "B"), b.consultar(cenario["pergunta"], "B")
        assert (ra.status, ra.resposta, ra.opcoes) == (rb.status, rb.resposta, rb.opcoes)


# -------------------------------------------------------------- métricas
def test_classificacao_dos_resultados(assistente):
    responder = {"orientacao_esperada": "DOC004", "comportamento_esperado": "responder"}
    abster = {"orientacao_esperada": None, "comportamento_esperado": "abster"}
    assert classificar(responder, assistente.consultar("passaporte")) == "correta"
    assert classificar(responder, assistente.consultar("cadastro único")) == "incorreta"
    assert classificar(responder, assistente.consultar("bolo de chocolate")) == "abstencao_incorreta"
    assert classificar(abster, assistente.consultar("bolo de chocolate")) == "abstencao_correta"
    assert classificar(abster, assistente.consultar("passaporte")) == "incorreta"


def test_indicadores_calculados_corretamente():
    registros = [
        {"classificacao": "correta", "tempo_ms": 1.0, "comportamento_esperado": "responder", "respondeu": True},
        {"classificacao": "incorreta", "tempo_ms": 3.0, "comportamento_esperado": "responder", "respondeu": True},
        {"classificacao": "abstencao_correta", "tempo_ms": 2.0, "comportamento_esperado": "abster", "respondeu": False},
        {"classificacao": "abstencao_incorreta", "tempo_ms": 2.0, "comportamento_esperado": "responder", "respondeu": False},
    ]
    ind = calcular_indicadores(registros)
    assert ind["total_testes"] == 4
    assert ind["total_corretas"] == 2
    assert ind["total_incorretas"] == 2
    assert ind["taxa_acerto"] == 0.5
    assert ind["taxa_cobertura"] == pytest.approx(2 / 3, abs=1e-4)  # indicadores têm 4 casas decimais
    assert ind["taxa_abstencao_correta"] == 1.0
    assert ind["tempo_medio_ms"] == 2.0
    assert ind["tempo_min_ms"] == 1.0 and ind["tempo_max_ms"] == 3.0


def test_indicadores_sem_cenarios_de_abstencao_ficam_nulos():
    ind = calcular_indicadores([{"classificacao": "correta", "tempo_ms": 1.0, "comportamento_esperado": "responder", "respondeu": True}])
    assert ind["taxa_abstencao_correta"] is None


def test_avaliacao_completa_tem_pelo_menos_12_cenarios(assistente):
    cenarios = json.loads((RAIZ / "data" / "testes.json").read_text(encoding="utf-8"))
    assert len(cenarios) >= 12
    relatorio = executar_avaliacao(assistente, cenarios)
    assert relatorio["indicadores"]["total_testes"] == len(cenarios)
    for item in relatorio["resultados"]:
        assert {"id", "pergunta", "categoria_esperada", "orientacao_esperada", "resultado_obtido",
                "classificacao", "tempo_ms", "observacoes"} <= set(item)


def test_comparacao_dos_modelos(assistente):
    comparacao = comparar_modelos(assistente, ["passaporte", "cadastro único"])
    assert comparacao["A"]["consultas"] == comparacao["B"]["consultas"] == 2
    assert comparacao["B"]["media_secoes"] > comparacao["A"]["media_secoes"]
    assert comparacao["fontes_consistentes"] is True


# -------------------------------------------------------------- CLI real
def executar_cli(entrada: str, extra_env=None):
    env = dict(os.environ, PYTHONIOENCODING="utf-8", CITIZEN_ASSIST_SEM_CORES="1")
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [sys.executable, "src/sistema.py"], input=entrada, capture_output=True,
        text=True, encoding="utf-8", cwd=RAIZ, timeout=60, env=env,
    )


def test_cli_inicia_e_encerra():
    processo = executar_cli("8\n")
    assert processo.returncode == 0, processo.stderr
    assert "CITIZEN ASSIST AI" in processo.stdout
    assert "Até logo" in processo.stdout


def test_cli_consulta_com_fonte_oficial():
    processo = executar_cli("1\nComo tirar o passaporte?\nA\n\n8\n")
    assert processo.returncode == 0, processo.stderr
    assert "Passaporte comum" in processo.stdout
    assert "https://www.gov.br/pt-br/servicos/obter-passaporte-comum-para-brasileiro" in processo.stdout


def test_cli_trata_opcao_invalida_e_entrada_vazia():
    processo = executar_cli("99\n1\n   \n\n8\n")
    assert processo.returncode == 0, processo.stderr
    assert "não existe" in processo.stdout
    assert "vazia" in processo.stdout


def test_cli_encerra_sem_erro_quando_entrada_termina():
    processo = executar_cli("1\n")
    assert processo.returncode == 0, processo.stderr
    assert "Traceback" not in processo.stderr


def test_cli_funciona_sem_rich():
    processo = executar_cli("5\n\n8\n", {"CITIZEN_ASSIST_SEM_RICH": "1"})
    assert processo.returncode == 0, processo.stderr
    assert "consumidor.gov.br" in processo.stdout


def test_cli_informa_base_invalida(tmp_path):
    base = tmp_path / "base.json"
    base.write_text("{ inválido", encoding="utf-8")
    processo = executar_cli("8\n", {"CITIZEN_ASSIST_BASE": str(base)})
    assert processo.returncode == 1
    assert "malformado" in processo.stdout
    assert "Traceback" not in processo.stderr


# ------------------------------------------------ CLI no mesmo processo
class TelaRoteirizada:
    """Tela de texto simples que lê respostas de uma lista (simula o teclado)."""

    def __new__(cls, entradas):
        from sistema import Tela

        class _Tela(Tela):
            def __init__(self):
                self.entradas = list(entradas)
                self.saida = []

            def ler(self, rotulo):
                from sistema import EncerrarPrograma
                if not self.entradas:
                    raise EncerrarPrograma
                return self.entradas.pop(0)

        return _Tela()


def rodar_menu(assistente, entradas, capsys):
    from sistema import AplicativoTerminal
    tela = TelaRoteirizada(entradas)
    try:
        AplicativoTerminal(assistente, tela).executar()
    except Exception as erro:  # EncerrarPrograma quando acabam as entradas
        assert type(erro).__name__ == "EncerrarPrograma"
    return capsys.readouterr().out


@pytest.mark.parametrize("entradas,esperado", [
    (["2", "1", "4", "A", "", "8"], "Passaporte comum"),                     # explorar temas
    (["2", "", "8"], "Documentação"),                                         # voltar sem escolher
    (["3", "CPF suspenso", "1", "B", "", "8"], "Sua necessidade".upper()),   # palavras-chave
    (["3", "bolo de chocolate", "", "8"], "Nenhuma orientação"),            # palavras-chave sem resultado
    (["3", "  ", "", "8"], "vazia"),                                         # palavras-chave vazia
    (["4", "7", "13", "", "8"], "Trilha de menor custo"),                    # grafo + Dijkstra
    (["5", "", "8"], "https://falabr.cgu.gov.br/v2/"),                       # fontes
    (["6", "", "8"], "Taxa de acerto"),                                       # funcionamento
    (["7", "", "8"], "não pede CPF"),                                         # privacidade
    (["1", "reclamação", "B", "2", "", "8"], "Fala.BR"),                     # ambígua -> escolhe opção
    (["1", "passaprote", "Z", "A", "", "8"], "Considerei"),                  # correção + modelo inválido
    (["1", "receita de bolo", "B", "", "", "8"], "Não tenho certeza"),       # baixa confiança
    (["1", "previsão do tempo amanhã", "B", "", "8"], "não possui"),         # sem resultado
    (["x", "8"], "não existe"),                                               # opção inválida
])
def test_cli_menus_no_mesmo_processo(assistente, capsys, entradas, esperado):
    assert esperado in rodar_menu(assistente, entradas, capsys)


def test_cli_escolha_numerica_invalida(assistente, capsys):
    saida = rodar_menu(assistente, ["2", "9", "", "8"], capsys)
    assert "não existe" in saida


# ------------------------------------- exigências do enunciado oficial da FIAP
def test_cli_sem_resultado_mostra_alternativas(assistente, capsys):
    saida = rodar_menu(assistente, ["1", "previsão do tempo amanhã", "B", "", "8"], capsys)
    assert "não possui" in saida
    assert "Alternativas" in saida
    assert "Passaporte comum" in saida  # lista orientações disponíveis


def test_cli_oferece_continuidade_apos_resposta(assistente, capsys):
    # Passaporte -> abre o 1º assunto relacionado (CIN) -> Enter volta ao menu
    saida = rodar_menu(assistente, ["1", "Como tirar o passaporte?", "A", "1", "", "8"], capsys)
    assert "Continue a consulta" in saida
    assert "Carteira de Identidade Nacional (CIN)" in saida
    assert saida.count("PASSO A PASSO") == 2


def test_cli_pergunta_dentro_de_um_tema(assistente, capsys):
    # Exemplo do enunciado: tema = documentos + pergunta em texto
    saida = rodar_menu(assistente, ["2", "1", "renovar passaporte", "B", "", "8"], capsys)
    assert "Passaporte comum" in saida
    assert "SUA NECESSIDADE" in saida


def test_modelos_documentam_papel_formato_e_fonte():
    from core.respostas import INSTRUCAO_MODELO_A, INSTRUCAO_MODELO_B
    for instrucao in (INSTRUCAO_MODELO_A, INSTRUCAO_MODELO_B):
        assert "Papel:" in instrucao
        assert "Fonte oficial" in instrucao
        assert "Proibido" in instrucao


def test_usabilidade_sem_sessoes_fica_pendente():
    from core.metricas import calcular_usabilidade
    ind = calcular_usabilidade({"tarefas": [{"id": "U1"}], "sessoes": []})
    assert ind["status"] == "pendente"
    assert ind["taxa_conclusao_sem_ajuda"] is None


def test_usabilidade_calcula_indicadores():
    from core.metricas import calcular_usabilidade
    dados = {"tarefas": [{"id": "U1"}, {"id": "U2"}], "sessoes": [{
        "participante": "P1", "nota_facilidade": 4,
        "resultados": [
            {"tarefa": "U1", "resultado": "concluiu", "tempo_s": 30, "dificuldade": ""},
            {"tarefa": "U2", "resultado": "com_dificuldade", "tempo_s": 90, "dificuldade": "não achou a fonte"},
        ]}]}
    ind = calcular_usabilidade(dados)
    assert ind["status"] == "realizado"
    assert ind["participantes"] == 1
    assert ind["taxa_conclusao_sem_ajuda"] == 0.5
    assert ind["taxa_conclusao_total"] == 1.0
    assert ind["tempo_medio_tarefa_s"] == 60.0
    assert ind["nota_media_facilidade"] == 4.0
    assert ind["dificuldades"] == ["U2: não achou a fonte"]


def test_usabilidade_rejeita_resultado_invalido():
    from core.metricas import calcular_usabilidade
    with pytest.raises(ValueError):
        calcular_usabilidade({"tarefas": [{"id": "U1"}], "sessoes": [
            {"participante": "P1", "resultados": [{"tarefa": "U1", "resultado": "talvez"}]}]})


def test_arquivo_de_usabilidade_real_e_valido():
    from core.metricas import calcular_usabilidade, carregar_usabilidade
    dados = carregar_usabilidade()
    assert len(dados["tarefas"]) >= 5
    calcular_usabilidade(dados)  # não pode lançar erro
