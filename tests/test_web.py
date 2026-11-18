"""Testes da interface web com o executor oficial do Streamlit (AppTest).

São ignorados automaticamente se o Streamlit não estiver instalado, porque a
interface web é um diferencial e a CLI precisa funcionar sem ela.
"""

from pathlib import Path

import pytest

pytest.importorskip("streamlit")
from streamlit.testing.v1 import AppTest  # noqa: E402

from core.respostas import Assistente  # noqa: E402

APP = str(Path(__file__).resolve().parents[1] / "src" / "web_app.py")


def iniciar() -> AppTest:
    app = AppTest.from_file(APP, default_timeout=30)
    app.run()
    assert not app.exception, app.exception
    return app


def consultar(app: AppTest, pergunta: str) -> AppTest:
    app.text_input[0].input(pergunta)
    app.button[0].click()  # botão "Consultar" do formulário
    app.run()
    assert not app.exception, app.exception
    return app


def html_da_pagina(app: AppTest) -> str:
    return "\n".join(m.value for m in app.markdown)


def test_web_inicia_com_apresentacao():
    app = iniciar()
    assert "CITIZEN ASSIST AI" in html_da_pagina(app)
    assert app.sidebar.radio[0].value == "Início e consulta"


def test_web_consulta_mostra_resposta_e_fonte():
    app = consultar(iniciar(), "Como tirar o passaporte?")
    pagina = html_da_pagina(app)
    assert "Passaporte comum" in pagina
    assert 'href="https://www.gov.br/pt-br/servicos/obter-passaporte-comum-para-brasileiro"' in pagina


def test_web_e_cli_mostram_a_mesma_fonte(base_real):
    pergunta = "Como fazer a inscrição no Cadastro Único?"
    resposta_nucleo = Assistente(base_real).consultar(pergunta, modelo="B").resposta
    app = consultar(iniciar(), pergunta)
    assert resposta_nucleo.fonte.url in html_da_pagina(app)


def test_web_sem_resultado():
    app = consultar(iniciar(), "previsão do tempo amanhã")
    assert any("não possui" in i.value for i in app.info)


def test_web_entrada_vazia():
    app = consultar(iniciar(), "   ")
    assert any("vazia" in e.value for e in app.error)


def test_web_consulta_ambigua_oferece_opcoes():
    app = consultar(iniciar(), "reclamação")
    assert app.warning
    rotulos = [b.label for b in app.button]
    assert any("Consumidor.gov.br" in r for r in rotulos)
    assert any("Fala.BR" in r for r in rotulos)


@pytest.mark.parametrize("pagina", ["Temas", "Navegar entre assuntos", "Fontes oficiais", "Como funciona",
                                    "Privacidade e limitações"])
def test_web_todas_as_paginas_abrem(pagina):
    app = iniciar()
    app.sidebar.radio[0].set_value(pagina)
    app.run()
    assert not app.exception, app.exception


def test_web_trilha_dijkstra():
    app = iniciar()
    app.sidebar.radio[0].set_value("Navegar entre assuntos")
    app.run()
    assert any("Trilha de menor custo" in s.value for s in app.success)


def test_web_modelo_a_tambem_oferece_continuidade():
    app = iniciar()
    app.radio[0].set_value("A")
    consultar(app, "Como tirar o passaporte?")
    rotulos = [b.label for b in app.button]
    assert any("Carteira de Identidade Nacional" in r for r in rotulos)


def test_web_mostra_situacao_da_usabilidade():
    app = iniciar()
    app.sidebar.radio[0].set_value("Como funciona")
    app.run()
    assert any(s.value == "Facilidade de uso" for s in app.subheader)
