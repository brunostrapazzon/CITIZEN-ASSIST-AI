"""CITIZEN ASSIST AI — interface web (Streamlit).

Execute a partir da raiz do projeto:
    streamlit run src/web_app.py

Camada fina: chama exatamente as mesmas funções do núcleo (src/core) que a
interface de terminal. Nenhuma regra de busca, grafo ou resposta fica aqui.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))  # garante "import core" no Streamlit

from core.erros import BaseConhecimentoInvalida, CitizenAssistError  # noqa: E402
from core.metricas import carregar_resultados  # noqa: E402
from core.respostas import Assistente, Resposta, ResultadoConsulta  # noqa: E402
from core.textos import AVISO_INSTITUCIONAL, COMO_FUNCIONA, LIMITACOES, NOME, PRIVACIDADE, SLOGAN  # noqa: E402

st.set_page_config(page_title="Citizen Assist AI", page_icon="🧭", layout="wide")

PAGINAS = ("Início e consulta", "Temas", "Navegar entre assuntos", "Fontes oficiais", "Como funciona", "Privacidade e limitações")
CHAVE_PAGINA = "pagina"
CHAVE_RESULTADO = "resultado"
CHAVE_REGISTRO = "registro_aberto"
CHAVE_MODELO = "modelo"

CSS = """
<style>
:root { --azul-profundo:#0B3D91; --azul-acao:#0B5FFF; --texto:#0F1E3D; --suave:#5B6B85; --borda:#D5DEEB; }
.block-container { max-width: 1100px; padding-top: 2rem; }
.ca-hero { background: linear-gradient(135deg, #0B3D91 0%, #0B5FFF 100%); color: #fff; border-radius: 16px;
           padding: 28px 32px; margin-bottom: 18px; }
.ca-hero h1 { color:#fff; font-size: 2rem; margin: 0 0 6px 0; letter-spacing: .5px; }
.ca-hero p { color:#EAF1FF; margin: 0; font-size: 1.05rem; }
.ca-hero small { display:block; margin-top: 12px; color:#C9D8F5; }
.ca-card { background:#fff; border:1px solid var(--borda); border-radius:12px; padding:16px 18px; margin-bottom:12px; height:100%; }
.ca-card h4 { margin:0 0 6px 0; color: var(--azul-profundo); font-size:1.02rem; }
.ca-card p { margin:0; color: var(--suave); font-size:.93rem; }
.ca-etiqueta { display:inline-block; background:#E9EEF6; color:var(--azul-profundo); border-radius:999px;
               padding:2px 10px; font-size:.78rem; margin-bottom:8px; }
.ca-resposta { background:#fff; border:1px solid var(--borda); border-left:5px solid var(--azul-acao);
               border-radius:12px; padding:20px 24px; margin-top:8px; }
.ca-resposta h3 { margin-top:0; color: var(--azul-profundo); }
.ca-secao { font-weight:700; color: var(--azul-profundo); margin:14px 0 4px 0; text-transform: uppercase;
            font-size:.82rem; letter-spacing:.6px; }
.ca-fonte { background:#F0F5FF; border-radius:8px; padding:10px 12px; }
.ca-fonte a { color: var(--azul-acao); font-weight:600; word-break: break-all; }
</style>
"""


# ------------------------------------------------------------------ estado
@st.cache_resource(show_spinner="Carregando a base de conhecimento...")
def obter_assistente() -> Assistente:
    return Assistente()


def ir_para(pagina: str, registro_id: str | None = None) -> None:
    """Callback de botões: troca de página e, se for o caso, abre uma orientação."""
    st.session_state[CHAVE_PAGINA] = pagina
    if registro_id:
        st.session_state[CHAVE_REGISTRO] = registro_id
        st.session_state[CHAVE_RESULTADO] = None


def esc(texto: str) -> str:
    return html.escape(texto, quote=True)


# ------------------------------------------------------------- componentes
def mostrar_resposta(resposta: Resposta, assistente: Assistente) -> None:
    nome_modelo = "Resposta direta" if resposta.modelo == "A" else "Resposta contextualizada"
    partes = [f'<div class="ca-resposta"><span class="ca-etiqueta">{esc(resposta.categoria)} · Modelo {resposta.modelo} — '
              f'{nome_modelo}</span><h3>{esc(resposta.titulo)}</h3>']
    # Opções de continuidade para os dois modelos (mesma função usada pela CLI)
    relacionados = [r.id for r, _ in assistente.relacionados(resposta.registro_id)[:3]]
    for secao in resposta.secoes:
        if secao.titulo == "Assuntos relacionados":
            continue  # exibido como botões logo abaixo
        partes.append(f'<div class="ca-secao">{esc(secao.titulo)}</div>')
        if secao.titulo == "Fonte oficial":
            partes.append(f'<div class="ca-fonte">{esc(resposta.fonte.nome)}<br>'
                          f'<a href="{esc(resposta.fonte.url)}" target="_blank" rel="noopener">{esc(resposta.fonte.url)}</a>'
                          f'<br><small>Verificado em {esc(resposta.data_verificacao)}</small></div>')
        elif secao.titulo == "Aviso":
            partes.append(f"<p>⚠️ {esc(secao.conteudo)}</p>")
        elif isinstance(secao.conteudo, tuple):
            tag = "ol" if secao.titulo == "Passo a passo" else "ul"
            itens = "".join(f"<li>{esc(item)}</li>" for item in secao.conteudo)
            partes.append(f"<{tag}>{itens}</{tag}>")
        else:
            partes.append(f"<p>{esc(secao.conteudo)}</p>")
    partes.append("</div>")
    st.markdown("".join(partes), unsafe_allow_html=True)

    if relacionados:
        st.markdown("**Continue a consulta:** assuntos relacionados, ordenados por proximidade no grafo")
        colunas = st.columns(len(relacionados))
        for coluna, rid in zip(colunas, relacionados):
            registro = assistente.base.obter(rid)
            coluna.button(f"{registro.titulo}", key=f"rel-{resposta.registro_id}-{rid}",
                          on_click=ir_para, args=(PAGINAS[0], rid), use_container_width=True)


def mostrar_resultado(resultado: ResultadoConsulta, assistente: Assistente) -> None:
    for errado, certo in resultado.termos_corrigidos:
        st.caption(f"Considerei '{errado}' como '{certo}'.")
    if resultado.status == "entrada_invalida":
        st.error(resultado.mensagem, icon="✖️")
    elif resultado.status == "sem_resultado":
        st.info(resultado.mensagem, icon="ℹ️")
        st.markdown("Você pode explorar os temas disponíveis:")
        colunas = st.columns(len(assistente.categorias()))
        for coluna, (tema, nome) in zip(colunas, assistente.categorias().items()):
            coluna.button(nome, key=f"sug-{tema}", on_click=ir_para, args=(PAGINAS[1],), use_container_width=True)
    elif resultado.status in ("ambiguo", "baixa_confianca"):
        st.warning(resultado.mensagem, icon="⚠️")
        for c in resultado.opcoes:
            registro = assistente.base.obter(c.registro_id)
            st.button(f"{registro.titulo}  ·  relevância {c.confianca:.0%}", key=f"op-{c.registro_id}",
                      on_click=ir_para, args=(PAGINAS[0], c.registro_id), use_container_width=True)
    else:
        st.success(f"Orientação encontrada em {resultado.tempo_ms:.2f} ms.", icon="✅")
        mostrar_resposta(resultado.resposta, assistente)


# ------------------------------------------------------------------ páginas
def pagina_consulta(assistente: Assistente) -> None:
    st.markdown(f'<div class="ca-hero"><h1>🧭 {NOME}</h1><p>{esc(SLOGAN)}</p>'
                f"<small>{esc(AVISO_INSTITUCIONAL)}</small></div>", unsafe_allow_html=True)
    categorias = assistente.categorias()
    with st.form("consulta", clear_on_submit=False):
        pergunta = st.text_input("Qual é a sua dúvida?", placeholder="Ex.: Como tirar o passaporte?", max_chars=300)
        c1, c2 = st.columns([1, 1])
        modelo = c1.radio("Modelo de resposta", ("B", "A"), horizontal=True, key=CHAVE_MODELO,
                          format_func=lambda m: "B — contextualizada" if m == "B" else "A — direta")
        rotulos = {"": "Todas as categorias", **categorias}
        categoria = c2.selectbox("Filtrar por categoria (opcional)", list(rotulos), format_func=rotulos.get)
        enviar = st.form_submit_button("Consultar", type="primary", use_container_width=True)

    if enviar:
        with st.spinner("Procurando na base de conhecimento..."):
            st.session_state[CHAVE_RESULTADO] = assistente.consultar(pergunta, modelo=modelo, categoria=categoria or None)
        st.session_state[CHAVE_REGISTRO] = None

    if st.session_state.get(CHAVE_REGISTRO):
        mostrar_resposta(assistente.responder_registro(st.session_state[CHAVE_REGISTRO], modelo), assistente)
    elif st.session_state.get(CHAVE_RESULTADO) is not None:
        mostrar_resultado(st.session_state[CHAVE_RESULTADO], assistente)
    else:
        st.markdown("#### Temas atendidos")
        colunas = st.columns(len(categorias))
        for coluna, (tema, nome) in zip(colunas, categorias.items()):
            titulos = ", ".join(r.titulo.split(" (")[0] for r in assistente.registros_da_categoria(tema)[:3])
            coluna.markdown(f'<div class="ca-card"><span class="ca-etiqueta">{esc(nome)}</span>'
                            f"<p>{esc(titulos)} e outros.</p></div>", unsafe_allow_html=True)
            coluna.button(f"Explorar {nome}", key=f"exp-{tema}", on_click=ir_para, args=(PAGINAS[1],),
                          use_container_width=True)


def pagina_temas(assistente: Assistente) -> None:
    st.header("Temas disponíveis")
    abas = st.tabs(list(assistente.categorias().values()))
    for aba, tema in zip(abas, assistente.categorias()):
        with aba:
            registros = assistente.registros_da_categoria(tema)
            for i in range(0, len(registros), 2):
                colunas = st.columns(2)
                for coluna, registro in zip(colunas, registros[i:i + 2]):
                    coluna.markdown(f'<div class="ca-card"><span class="ca-etiqueta">{registro.id}</span>'
                                    f"<h4>{esc(registro.titulo)}</h4><p>{esc(registro.resumo)}</p></div>",
                                    unsafe_allow_html=True)
                    coluna.button("Ver orientação", key=f"ver-{registro.id}", on_click=ir_para,
                                  args=(PAGINAS[0], registro.id), use_container_width=True)


def pagina_grafo(assistente: Assistente) -> None:
    st.header("Navegar entre assuntos")
    st.write("Escolha dois assuntos. O algoritmo de Dijkstra calcula a trilha de menor custo no grafo de assuntos.")
    nos = {**{f"CAT:{t}": f"Categoria: {n}" for t, n in assistente.categorias().items()},
           **{r.id: f"{r.id} — {r.titulo}" for r in assistente.fontes()}}
    c1, c2 = st.columns(2)
    origem = c1.selectbox("Assunto de partida", list(nos), format_func=nos.get, index=list(nos).index("DOC002"))
    destino = c2.selectbox("Assunto de destino", list(nos), format_func=nos.get, index=list(nos).index("SER003"))
    try:
        caminho, custo = assistente.trilha(origem, destino)
    except CitizenAssistError as erro:
        st.error(str(erro))
        return
    st.success(f"Trilha de menor custo: {custo:.1f}")
    st.markdown("  →  ".join(f"**{esc(assistente.grafo.rotulo(no))}**" for no in caminho))
    if not origem.startswith("CAT:"):
        st.subheader("Assuntos mais próximos da partida")
        st.table([{"Código": r.id, "Assunto": r.titulo, "Custo": f"{d:.1f}"} for r, d in assistente.relacionados(origem)])
    with st.expander("Como os pesos foram definidos"):
        st.markdown("- Relação explícita entre orientações da mesma categoria: **1,0**\n"
                    "- Relação explícita entre orientações de categorias diferentes: **1,5**\n"
                    "- Ligação de uma orientação com a sua categoria: **2,0**")


def pagina_fontes(assistente: Assistente) -> None:
    st.header("Fontes oficiais")
    st.write("Todas as orientações foram resumidas a partir destas páginas, lidas na data indicada.")
    for r in assistente.fontes():
        st.markdown(f"**{r.id} — {esc(r.titulo)}**  \n{esc(r.fonte.nome)}  \n"
                    f"[{esc(r.fonte.url)}]({r.fonte.url}) · verificado em {r.data_verificacao}")


def pagina_funcionamento() -> None:
    st.header("Como funciona")
    for titulo, texto in COMO_FUNCIONA:
        st.markdown(f"**{titulo}.** {texto}")
    st.subheader("Indicadores da última avaliação automática")
    resultados = carregar_resultados()
    if not resultados:
        st.info("Ainda não há resultados. Execute `python src/avaliar.py`.")
        return
    ind = resultados["indicadores"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Testes executados", ind["total_testes"])
    c2.metric("Taxa de acerto", f"{ind['taxa_acerto']:.1%}")
    c3.metric("Abstenção correta", "—" if ind["taxa_abstencao_correta"] is None else f"{ind['taxa_abstencao_correta']:.1%}")
    c4.metric("Tempo médio", f"{ind['tempo_medio_ms']:.3f} ms")
    st.caption(f"Gerado em {resultados['gerado_em']} pelo script src/avaliar.py (versão {resultados['versao_codigo']}).")
    st.subheader("Facilidade de uso")
    usab = resultados.get("usabilidade") or {"status": "pendente"}
    if usab["status"] == "pendente":
        st.info("Teste com usuário ainda não realizado. O roteiro está em docs/roteiro_usabilidade.md.")
    else:
        u1, u2, u3 = st.columns(3)
        u1.metric("Participantes", usab["participantes"])
        u2.metric("Tarefas concluídas sem ajuda", f"{usab['taxa_conclusao_sem_ajuda']:.0%}")
        u3.metric("Nota média (1 a 5)", "—" if usab["nota_media_facilidade"] is None else usab["nota_media_facilidade"])


def pagina_privacidade() -> None:
    st.header("Privacidade e responsabilidade")
    for item in PRIVACIDADE:
        st.markdown(f"- {item}")
    st.header("Limitações")
    for item in LIMITACOES:
        st.markdown(f"- {item}")
    st.caption(AVISO_INSTITUCIONAL)


# ------------------------------------------------------------------- main
def main() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
    try:
        assistente = obter_assistente()
    except BaseConhecimentoInvalida as erro:
        st.error(f"Não foi possível carregar a base de conhecimento. {erro}")
        st.stop()

    st.session_state.setdefault(CHAVE_PAGINA, PAGINAS[0])
    st.session_state.setdefault(CHAVE_RESULTADO, None)
    st.session_state.setdefault(CHAVE_REGISTRO, None)
    with st.sidebar:
        st.markdown(f"### 🧭 {NOME}")
        st.radio("Navegação", PAGINAS, key=CHAVE_PAGINA)
        st.caption(AVISO_INSTITUCIONAL)

    pagina = st.session_state[CHAVE_PAGINA]
    if pagina == PAGINAS[0]:
        pagina_consulta(assistente)
    elif pagina == PAGINAS[1]:
        pagina_temas(assistente)
    elif pagina == PAGINAS[2]:
        pagina_grafo(assistente)
    elif pagina == PAGINAS[3]:
        pagina_fontes(assistente)
    elif pagina == PAGINAS[4]:
        pagina_funcionamento()
    else:
        pagina_privacidade()


main()
