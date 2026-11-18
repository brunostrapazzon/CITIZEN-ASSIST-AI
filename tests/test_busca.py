"""Testes do motor de busca (src/core/busca.py)."""

import pytest

from core.busca import IndiceInvertido, MotorBusca, normalizar, tokenizar


def test_normalizar_remove_acentos_caixa_e_pontuacao():
    assert normalizar("Ação SOCIAL!") == "acao social"
    assert normalizar("  Título   de  eleitor?? ") == "titulo de eleitor"


def test_tokenizar_remove_stopwords():
    assert tokenizar("Como eu tiro o meu passaporte?") == ["tiro", "passaporte"]


def test_tokenizar_reduz_plural_simples():
    assert tokenizar("direitos") == tokenizar("direito")


@pytest.mark.parametrize("plural,singular", [
    ("federais", "federal"), ("digitais", "digital"), ("sociais", "social"),
    ("reclamações", "reclamação"), ("níveis", "nível"),
])
def test_tokenizar_reduz_plurais_irregulares(plural, singular):
    # Regressão: "federais" não era reduzido a "federal" (cenário T17 da avaliação v1).
    assert tokenizar(plural) == tokenizar(singular)


def test_indice_invertido_aponta_registros_corretos(base_real):
    indice = IndiceInvertido(base_real)
    assert "DOC004" in indice.postings[tokenizar("passaporte")[0]]
    assert indice.idf(tokenizar("passaporte")[0]) > indice.idf(tokenizar("gov")[0])


def test_peso_do_titulo_maior_que_orientacao(base_real):
    indice = IndiceInvertido(base_real)
    termo = tokenizar("passaporte")[0]
    assert indice.postings[termo]["DOC004"] >= 3.0


@pytest.fixture(scope="module")
def motor(base_real):
    return MotorBusca(base_real)


@pytest.mark.parametrize("pergunta,esperado", [
    ("Como tirar o passaporte?", "DOC004"),
    ("quero tirar meu titulo de eleitor", "DOC005"),
    ("cadunico inscrição", "SER002"),
    ("CPF suspenso, como regularizar", "DOC002"),
    ("o que o CRAS oferece", "DIR004"),
])
def test_busca_encontra_orientacao_esperada(motor, pergunta, esperado):
    resultado = motor.buscar(pergunta)
    assert resultado.status == "encontrado"
    assert resultado.melhor.registro_id == esperado


def test_busca_igual_com_e_sem_acentos(motor):
    com = motor.buscar("título de eleitor")
    sem = motor.buscar("titulo de eleitor")
    assert com.melhor.registro_id == sem.melhor.registro_id


def test_busca_corrige_erro_de_digitacao(motor):
    resultado = motor.buscar("passaprote")
    assert resultado.melhor is not None
    assert resultado.melhor.registro_id == "DOC004"
    assert resultado.termos_corrigidos


def test_correcao_nao_troca_palavra_sem_relacao(motor):
    # Regressão (avaliação v1, T05): "emito" era corrigido para "feito".
    alvo, _ = motor.indice.resolver("emito")
    assert alvo is None or alvo[0] == "e"


def test_consulta_fora_do_tema_nao_responde(motor):
    resultado = motor.buscar("receita de bolo de chocolate")
    assert resultado.status == "sem_resultado"


def test_metade_da_pergunta_desconhecida_nao_gera_resposta(motor):
    # Regressão: "receita de bolo" respondia a orientação do CPF ("Receita Federal").
    assert motor.buscar("receita de bolo").status in {"sem_resultado", "baixa_confianca"}


def test_palavra_isolada_comum_nao_gera_resposta_confiavel(motor):
    resultado = motor.buscar("como fazer")
    assert resultado.status in {"sem_resultado", "baixa_confianca"}


def test_consulta_ambigua_apresenta_opcoes(motor):
    resultado = motor.buscar("reclamação")
    assert resultado.status == "ambiguo"
    ids = {c.registro_id for c in resultado.correspondencias}
    assert {"DIR002", "DIR005"} <= ids


def test_ordem_estavel_em_empate(motor):
    primeira = [c.registro_id for c in motor.buscar("reclamação").correspondencias]
    segunda = [c.registro_id for c in motor.buscar("reclamação").correspondencias]
    assert primeira == segunda


def test_confianca_entre_zero_e_um(motor):
    for c in motor.buscar("conta gov.br nível prata").correspondencias:
        assert 0.0 < c.confianca <= 1.0


def test_filtro_por_categoria(motor):
    resultado = motor.buscar("reclamação", categoria="servicos_publicos")
    assert all(c.registro_id.startswith("SER") for c in resultado.correspondencias)


def test_busca_por_id(motor):
    assert motor.buscar_por_id("dir001").id == "DIR001"
    assert motor.buscar_por_id("ABC999") is None


def test_listar_categoria(motor):
    ids = [r.id for r in motor.listar_categoria("documentacao")]
    assert ids == ["DOC001", "DOC002", "DOC003", "DOC004", "DOC005"]


def test_busca_sem_termos_validos(motor):
    assert motor.buscar("o a de").status == "sem_resultado"
