"""Testes da base de conhecimento e das validações (src/core/validacoes.py)."""

import pytest

from conftest import base_valida, registro_valido
from core.base_conhecimento import carregar_base
from core.erros import BaseConhecimentoInvalida, EntradaInvalida, RegistroNaoEncontrado
from core.validacoes import validar_dados_base, validar_entrada, validar_opcao_menu, validar_url


# ---------------------------------------------------------------- base real
def test_base_real_e_valida(base_real):
    assert len(base_real.registros) >= 15


def test_base_real_tem_pelo_menos_tres_categorias_com_registros(base_real):
    temas_usados = {r.tema for r in base_real.registros.values()}
    assert len(temas_usados) >= 3
    assert temas_usados <= set(base_real.categorias)


def test_todas_as_fontes_tem_url_https_oficial(base_real):
    for registro in base_real.registros.values():
        assert validar_url(registro.fonte.url), registro.id


def test_obter_registro_inexistente_lanca_erro(base_real):
    with pytest.raises(RegistroNaoEncontrado):
        base_real.obter("XYZ999")


def test_obter_aceita_id_em_minusculas(base_real):
    assert base_real.obter("doc001").id == "DOC001"


# ------------------------------------------------------- carregamento seguro
def test_arquivo_ausente(tmp_path):
    with pytest.raises(BaseConhecimentoInvalida, match="não encontrado"):
        carregar_base(tmp_path / "nao_existe.json")


def test_arquivo_vazio(gravar_json):
    with pytest.raises(BaseConhecimentoInvalida, match="vazio"):
        carregar_base(gravar_json("   \n"))


def test_json_malformado(gravar_json):
    with pytest.raises(BaseConhecimentoInvalida, match="malformado"):
        carregar_base(gravar_json('{"registros": [ {"id": "DOC001", } ]'))


def test_base_invalida_lista_todos_os_problemas(gravar_json):
    dados = base_valida([registro_valido(titulo=""), registro_valido(id="DOC002", fonte={"nome": "X", "url": "ftp://x"})])
    with pytest.raises(BaseConhecimentoInvalida) as erro:
        carregar_base(gravar_json(dados))
    assert len(erro.value.problemas) == 2


# ------------------------------------------------------------- validações
def test_base_minima_valida_nao_tem_problemas():
    assert validar_dados_base(base_valida()) == []


def test_raiz_precisa_ser_objeto():
    assert validar_dados_base([1, 2]) != []


def test_campo_obrigatorio_ausente():
    registro = registro_valido()
    del registro["fonte"]
    problemas = validar_dados_base(base_valida([registro]))
    assert any("fonte" in p for p in problemas)


def test_campo_com_tipo_errado():
    problemas = validar_dados_base(base_valida([registro_valido(passos="não é lista")]))
    assert any("passos" in p for p in problemas)


def test_id_duplicado():
    problemas = validar_dados_base(base_valida([registro_valido(), registro_valido()]))
    assert any("duplicado" in p for p in problemas)


def test_id_com_formato_invalido():
    problemas = validar_dados_base(base_valida([registro_valido(id="doc-1")]))
    assert any("formato" in p for p in problemas)


def test_referencia_inexistente():
    problemas = validar_dados_base(base_valida([registro_valido(relacionados=["SER999"])]))
    assert any("SER999" in p for p in problemas)


def test_autorreferencia():
    problemas = validar_dados_base(base_valida([registro_valido(relacionados=["DOC001"])]))
    assert any("si mesmo" in p for p in problemas)


def test_tema_fora_das_categorias():
    problemas = validar_dados_base(base_valida([registro_valido(tema="esportes")]))
    assert any("esportes" in p for p in problemas)


def test_data_de_verificacao_invalida():
    problemas = validar_dados_base(base_valida([registro_valido(data_verificacao="17/11/2026")]))
    assert any("data_verificacao" in p for p in problemas)


def test_titulo_duplicado_e_sinalizado():
    problemas = validar_dados_base(base_valida([registro_valido(), registro_valido(id="DOC002", titulo="TÍTULO de teste")]))
    assert any("título repetido" in p for p in problemas)


@pytest.mark.parametrize("url,esperado", [
    ("https://www.gov.br/pt-br/servicos", True),
    ("http://www.gov.br", False),
    ("https://", False),
    ("gov.br/servicos", False),
    ("https://exemplo .com", False),
])
def test_validar_url(url, esperado):
    assert validar_url(url) is esperado


# ---------------------------------------------------------- entrada do usuário
@pytest.mark.parametrize("texto", [None, "", "     ", "\t\n"])
def test_entrada_vazia(texto):
    with pytest.raises(EntradaInvalida, match="vazia"):
        validar_entrada(texto)


@pytest.mark.parametrize("texto", ["???!!!", "@#$%", "...."])
def test_entrada_sem_letras_ou_numeros(texto):
    with pytest.raises(EntradaInvalida, match="letras ou números"):
        validar_entrada(texto)


def test_entrada_com_caractere_de_controle():
    with pytest.raises(EntradaInvalida, match="caracteres inválidos"):
        validar_entrada("cpf\x00")


def test_entrada_longa_demais():
    with pytest.raises(EntradaInvalida, match="longa"):
        validar_entrada("a" * 301)


def test_entrada_valida_e_limpa():
    assert validar_entrada("  Como tirar o CPF?  ") == "Como tirar o CPF?"


def test_opcao_de_menu_inexistente():
    with pytest.raises(EntradaInvalida, match="não existe"):
        validar_opcao_menu("9", {"1", "2"})


def test_opcao_de_menu_valida():
    assert validar_opcao_menu(" 2 ", {"1", "2"}) == "2"
