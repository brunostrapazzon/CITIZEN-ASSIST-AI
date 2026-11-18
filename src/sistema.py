"""CITIZEN ASSIST AI — interface de terminal (ponto de entrada principal).

Execute a partir da raiz do projeto:
    python src/sistema.py

Esta camada só lê o teclado, chama o núcleo (src/core) e mostra o resultado.
Toda regra de busca, grafo e montagem de resposta está no núcleo, que também
é usado pela interface web (src/web_app.py).

A biblioteca Rich deixa a apresentação mais bonita, mas é opcional: sem ela
(ou com CITIZEN_ASSIST_SEM_RICH=1), o programa usa texto simples.
"""

from __future__ import annotations

import os
import sys
from typing import Callable

from core.erros import BaseConhecimentoInvalida, CitizenAssistError, EntradaInvalida
from core.metricas import carregar_resultados
from core.respostas import Assistente, Resposta, ResultadoConsulta
from core.textos import AVISO_INSTITUCIONAL, COMO_FUNCIONA, LIMITACOES, NOME, PRIVACIDADE, SLOGAN
from core.validacoes import validar_entrada, validar_opcao_menu

try:  # Rich é opcional
    if os.environ.get("CITIZEN_ASSIST_SEM_RICH"):
        raise ImportError
    from rich.console import Console
    from rich.markup import escape
    from rich.panel import Panel
    from rich.table import Table
    RICH_DISPONIVEL = True
except ImportError:
    RICH_DISPONIVEL = False

MENU = (
    ("1", "Consultar uma orientação"),
    ("2", "Explorar temas disponíveis"),
    ("3", "Pesquisar por palavras-chave"),
    ("4", "Consultar assuntos relacionados"),
    ("5", "Visualizar fontes oficiais"),
    ("6", "Conhecer o funcionamento do assistente"),
    ("7", "Privacidade e limitações"),
    ("8", "Sair"),
)


class EncerrarPrograma(Exception):
    """Fim da entrada (Ctrl+D / Ctrl+Z) ou Ctrl+C: encerra sem erro."""


# =================================================================== saída
class Tela:
    """Saída em texto simples (funciona em qualquer terminal)."""

    def ler(self, rotulo: str) -> str:
        try:
            return input(f"{rotulo} ")
        except (EOFError, KeyboardInterrupt):
            raise EncerrarPrograma from None

    def cabecalho(self) -> None:
        linha = "=" * 64
        print(f"\n{linha}\n  {NOME}\n  {SLOGAN}\n{linha}\n  {AVISO_INSTITUCIONAL}\n")

    def titulo(self, texto: str) -> None:
        print(f"\n--- {texto} ---")

    def texto(self, texto: str) -> None:
        print(texto)

    def lista(self, itens: list[str] | tuple[str, ...], numerada: bool = False) -> None:
        for i, item in enumerate(itens, start=1):
            print(f"  {i}. {item}" if numerada else f"  • {item}")

    def sucesso(self, texto: str) -> None:
        print(f"[OK] {texto}")

    def aviso(self, texto: str) -> None:
        print(f"[ATENÇÃO] {texto}")

    def erro(self, texto: str) -> None:
        print(f"[ERRO] {texto}")

    def tabela(self, colunas: list[str], linhas: list[list[str]]) -> None:
        print("  " + " | ".join(colunas))
        for linha in linhas:
            print("  " + " | ".join(linha))

    def carregando(self, texto: str):
        print(texto)
        return _SemEfeito()


class _SemEfeito:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class TelaRich(Tela):
    """Mesma interface, com cores e painéis da biblioteca Rich."""

    def __init__(self) -> None:
        sem_cor = bool(os.environ.get("CITIZEN_ASSIST_SEM_CORES"))
        # soft_wrap fica desligado no console (painéis e tabelas quebram linha
        # normalmente) e ligado só nos textos corridos, para URLs não serem cortadas.
        self.console = Console(highlight=False, no_color=sem_cor)

    def ler(self, rotulo: str) -> str:
        try:
            return self.console.input(f"[bold #0B5FFF]{escape(rotulo)}[/] ")
        except (EOFError, KeyboardInterrupt):
            raise EncerrarPrograma from None

    def cabecalho(self) -> None:
        corpo = f"[bold]{NOME}[/]\n{SLOGAN}\n\n[dim]{AVISO_INSTITUCIONAL}[/]"
        self.console.print(Panel(corpo, border_style="#0B3D91", padding=(1, 2)))

    def titulo(self, texto: str) -> None:
        self.console.rule(f"[bold #0B3D91]{escape(texto)}[/]", align="left", style="#9DB4D9")

    def texto(self, texto: str) -> None:
        self.console.print(escape(texto), soft_wrap=True)

    def lista(self, itens, numerada: bool = False) -> None:
        for i, item in enumerate(itens, start=1):
            marcador = f"[bold #0B5FFF]{i}.[/]" if numerada else "[#0B5FFF]•[/]"
            self.console.print(f"  {marcador} {escape(item)}", soft_wrap=True)

    def sucesso(self, texto: str) -> None:
        self.console.print(f"[bold green]✔[/] {escape(texto)}", soft_wrap=True)

    def aviso(self, texto: str) -> None:
        self.console.print(f"[bold #B26A00]⚠ {escape(texto)}[/]", soft_wrap=True)

    def erro(self, texto: str) -> None:
        self.console.print(f"[bold red]✖ {escape(texto)}[/]", soft_wrap=True)

    def tabela(self, colunas, linhas) -> None:
        tabela = Table(header_style="bold #0B3D91", border_style="#9DB4D9")
        for coluna in colunas:
            tabela.add_column(coluna, overflow="fold")
        for linha in linhas:
            tabela.add_row(*(escape(c) for c in linha))
        self.console.print(tabela)

    def carregando(self, texto: str):
        return self.console.status(escape(texto))


# ============================================================== aplicação
class AplicativoTerminal:
    def __init__(self, assistente: Assistente, tela: Tela) -> None:
        self.assistente = assistente
        self.tela = tela
        self.acoes: dict[str, Callable[[], None]] = {
            "1": self.consultar,
            "2": self.explorar_temas,
            "3": self.pesquisar_palavras_chave,
            "4": self.assuntos_relacionados,
            "5": self.fontes_oficiais,
            "6": self.funcionamento,
            "7": self.privacidade_limitacoes,
        }

    # ---------------------------------------------------------- utilidades
    def pausar(self) -> None:
        self.tela.ler("\nPressione Enter para voltar ao menu...")

    def escolher_modelo(self) -> str:
        while True:
            opcao = self.tela.ler("Modelo de resposta — [A] direta ou [B] contextualizada (Enter = B):").strip().upper()
            if opcao in ("", "A", "B"):
                return opcao or "B"
            self.tela.erro("Digite A, B ou apenas Enter.")

    def escolher_numero(self, quantidade: int, rotulo: str) -> int | None:
        """Número de 1 a `quantidade`, ou None se o usuário apertar Enter."""
        while True:
            texto = self.tela.ler(f"{rotulo} (1-{quantidade}, Enter para voltar):").strip()
            if not texto:
                return None
            try:
                validar_opcao_menu(texto, {str(i) for i in range(1, quantidade + 1)})
                return int(texto)
            except EntradaInvalida as erro:
                self.tela.erro(str(erro))

    def mostrar_resposta(self, resposta: Resposta) -> None:
        nome_modelo = "Resposta direta" if resposta.modelo == "A" else "Resposta contextualizada"
        self.tela.titulo(resposta.titulo)
        self.tela.texto(f"{resposta.categoria} · Modelo {resposta.modelo} ({nome_modelo})")
        for secao in resposta.secoes:
            self.tela.texto(f"\n{secao.titulo.upper()}")
            if isinstance(secao.conteudo, tuple):
                self.tela.lista(secao.conteudo, numerada=secao.titulo == "Passo a passo")
            elif secao.titulo == "Aviso":
                self.tela.aviso(secao.conteudo)
            else:
                self.tela.texto(secao.conteudo)

    def exibir_e_continuar(self, registro_id: str, modelo: str) -> None:
        """Mostra a orientação e oferece até 3 assuntos relacionados para continuar a consulta.

        O próprio pedido "Enter para voltar" funciona como pausa antes do menu.
        """
        while True:
            self.mostrar_resposta(self.assistente.responder_registro(registro_id, modelo))
            proximos = self.assistente.relacionados(registro_id)[:3]
            if not proximos:
                self.pausar()
                return
            self.tela.titulo("Continue a consulta")
            self.tela.lista([f"{r.titulo} ({r.id})" for r, _ in proximos], numerada=True)
            escolha = self.escolher_numero(len(proximos), "Abrir um assunto relacionado")
            if escolha is None:
                return
            registro_id = proximos[escolha - 1][0].id

    def mostrar_alternativas(self) -> None:
        """Quando não há resposta adequada, mostra o que a base cobre."""
        self.tela.titulo("Alternativas de consulta")
        for tema, nome in self.assistente.categorias().items():
            self.tela.texto(f"\n{nome}:")
            self.tela.lista([f"{r.titulo} ({r.id})" for r in self.assistente.registros_da_categoria(tema)])
        self.tela.texto("\nDica: use o menu 2 para escolher um tema ou digite o código da orientação (ex.: DOC004).")

    def mostrar_resultado(self, resultado: ResultadoConsulta, modelo: str) -> bool:
        """Mostra o resultado de uma consulta. Devolve True se ainda é preciso pausar."""
        for errado, certo in resultado.termos_corrigidos:
            self.tela.aviso(f"Considerei '{errado}' como '{certo}'.")
        if resultado.status == "encontrado":
            self.exibir_e_continuar(resultado.resposta.registro_id, modelo)
            return False
        if resultado.status == "entrada_invalida":
            self.tela.erro(resultado.mensagem)
            return True
        if resultado.status == "sem_resultado":
            self.tela.aviso(resultado.mensagem)
            self.mostrar_alternativas()
            return True
        self.tela.aviso(resultado.mensagem)
        linhas = []
        for c in resultado.opcoes:
            registro = self.assistente.base.obter(c.registro_id)
            linhas.append(f"{registro.titulo} ({c.registro_id}) — relevância {c.confianca:.0%}")
        self.tela.lista(linhas, numerada=True)
        escolha = self.escolher_numero(len(resultado.opcoes), "Escolha uma opção")
        if escolha is None:
            return True
        self.exibir_e_continuar(resultado.opcoes[escolha - 1].registro_id, modelo)
        return False

    # ---------------------------------------------------------- menu 1
    def consultar(self) -> None:
        self.tela.titulo("Consultar uma orientação")
        self.tela.texto("Escreva sua dúvida com suas palavras. Exemplo: 'Como tirar o passaporte?'")
        pergunta = self.tela.ler("Sua pergunta:")
        try:
            validar_entrada(pergunta)
        except EntradaInvalida as erro:
            self.tela.erro(str(erro))
            self.pausar()
            return
        modelo = self.escolher_modelo()
        with self.tela.carregando("Procurando na base de conhecimento..."):
            resultado = self.assistente.consultar(pergunta, modelo=modelo)
        if self.mostrar_resultado(resultado, modelo):
            self.pausar()

    # ---------------------------------------------------------- menu 2
    def explorar_temas(self) -> None:
        self.tela.titulo("Temas disponíveis")
        categorias = list(self.assistente.categorias().items())
        self.tela.lista([f"{nome} ({len(self.assistente.registros_da_categoria(tema))} orientações)"
                         for tema, nome in categorias], numerada=True)
        escolha = self.escolher_numero(len(categorias), "Escolha um tema")
        if escolha is None:
            return
        tema, nome = categorias[escolha - 1]
        registros = self.assistente.registros_da_categoria(tema)
        self.tela.titulo(nome)
        self.tela.lista([f"{r.titulo} ({r.id})" for r in registros], numerada=True)
        numeros = {str(i) for i in range(1, len(registros) + 1)}
        while True:
            texto = self.tela.ler(f"Escolha uma orientação (1-{len(registros)}), digite uma pergunta "
                                  f"sobre {nome} ou Enter para voltar:").strip()
            if not texto:
                return
            if texto in numeros:
                self.exibir_e_continuar(registros[int(texto) - 1].id, self.escolher_modelo())
                return
            if texto.isdigit():
                self.tela.erro(f"A opção '{texto}' não existe. Escolha de 1 a {len(registros)}.")
                continue
            break
        # Pergunta em texto dentro do tema escolhido (ex.: tema = documentos + pergunta)
        modelo = self.escolher_modelo()
        resultado = self.assistente.consultar(texto, modelo=modelo, categoria=tema)
        if self.mostrar_resultado(resultado, modelo):
            self.pausar()

    # ---------------------------------------------------------- menu 3
    def pesquisar_palavras_chave(self) -> None:
        self.tela.titulo("Pesquisar por palavras-chave")
        termos = self.tela.ler("Palavras-chave (ex.: CPF suspenso):")
        try:
            correspondencias = self.assistente.pesquisar_palavras_chave(termos)
        except EntradaInvalida as erro:
            self.tela.erro(str(erro))
            self.pausar()
            return
        if not correspondencias:
            self.tela.aviso("Nenhuma orientação com relevância suficiente para essas palavras-chave.")
            self.pausar()
            return
        linhas = []
        for i, c in enumerate(correspondencias, start=1):
            registro = self.assistente.base.obter(c.registro_id)
            linhas.append([str(i), c.registro_id, registro.titulo, f"{c.confianca:.0%}", f"{c.cobertura:.0%}"])
        self.tela.tabela(["#", "Código", "Orientação", "Relevância", "Cobertura"], linhas)
        escolha = self.escolher_numero(len(correspondencias), "Abrir qual orientação")
        if escolha is None:
            self.pausar()
            return
        self.exibir_e_continuar(correspondencias[escolha - 1].registro_id, self.escolher_modelo())

    # ---------------------------------------------------------- menu 4
    def assuntos_relacionados(self) -> None:
        self.tela.titulo("Assuntos relacionados (grafo + Dijkstra)")
        registros = self.assistente.fontes()
        self.tela.lista([f"{r.id} — {r.titulo}" for r in registros], numerada=True)
        escolha = self.escolher_numero(len(registros), "Escolha o assunto de partida")
        if escolha is None:
            return
        origem = registros[escolha - 1]
        self.tela.titulo(f"Mais próximos de: {origem.titulo}")
        self.tela.tabela(
            ["Código", "Assunto", "Custo da trilha"],
            [[r.id, r.titulo, f"{d:.1f}"] for r, d in self.assistente.relacionados(origem.id)],
        )
        self.tela.texto("\nQuer ver a trilha de navegação até outro assunto?")
        destino_num = self.escolher_numero(len(registros), "Escolha o assunto de destino")
        if destino_num is not None:
            destino = registros[destino_num - 1]
            try:
                caminho, custo = self.assistente.trilha(origem.id, destino.id)
            except CitizenAssistError as erro:
                self.tela.erro(str(erro))
            else:
                trilha = " → ".join(self.assistente.grafo.rotulo(no) for no in caminho)
                self.tela.sucesso(f"Trilha de menor custo ({custo:.1f}): {trilha}")
        self.pausar()

    # ---------------------------------------------------------- menu 5
    def fontes_oficiais(self) -> None:
        self.tela.titulo("Fontes oficiais consultadas")
        for r in self.assistente.fontes():
            self.tela.texto(f"\n{r.id} — {r.titulo}")
            self.tela.texto(f"  Órgão/fonte: {r.fonte.nome}")
            self.tela.texto(f"  Endereço: {r.fonte.url}")
            self.tela.texto(f"  Verificado em: {r.data_verificacao}")
        self.pausar()

    # ---------------------------------------------------------- menu 6
    def funcionamento(self) -> None:
        self.tela.titulo("Como o Citizen Assist AI funciona")
        for titulo, texto in COMO_FUNCIONA:
            self.tela.texto(f"\n{titulo.upper()}\n{texto}")
        resultados = carregar_resultados()
        self.tela.titulo("Indicadores da última avaliação automática")
        if not resultados:
            self.tela.aviso("Ainda não há resultados. Execute: python src/avaliar.py")
        else:
            ind = resultados["indicadores"]
            self.tela.tabela(["Indicador", "Valor"], [
                ["Gerado em", resultados["gerado_em"]],
                ["Testes executados", str(ind["total_testes"])],
                ["Corretas / incorretas", f"{ind['total_corretas']} / {ind['total_incorretas']}"],
                ["Taxa de acerto", _pct(ind["taxa_acerto"])],
                ["Cobertura (respondíveis atendidas)", _pct(ind["taxa_cobertura"])],
                ["Abstenção correta", _pct(ind["taxa_abstencao_correta"])],
                ["Tempo médio / mín. / máx. (ms)",
                 f"{ind['tempo_medio_ms']:.3f} / {ind['tempo_min_ms']:.3f} / {ind['tempo_max_ms']:.3f}"],
            ])
        self.pausar()

    # ---------------------------------------------------------- menu 7
    def privacidade_limitacoes(self) -> None:
        self.tela.titulo("Privacidade")
        self.tela.lista(PRIVACIDADE)
        self.tela.titulo("Limitações")
        self.tela.lista(LIMITACOES)
        self.pausar()

    # ---------------------------------------------------------- laço
    def executar(self) -> None:
        self.tela.cabecalho()
        opcoes = {codigo for codigo, _ in MENU}
        while True:
            self.tela.titulo("Menu principal")
            self.tela.lista([f"[{codigo}] {texto}" for codigo, texto in MENU])
            try:
                opcao = validar_opcao_menu(self.tela.ler("Escolha uma opção:"), opcoes)
            except EntradaInvalida as erro:
                self.tela.erro(str(erro))
                continue
            if opcao == "8":
                return
            try:
                self.acoes[opcao]()
            except CitizenAssistError as erro:  # falha isolada não derruba o programa
                self.tela.erro(str(erro))


def _pct(valor: float | None) -> str:
    return "—" if valor is None else f"{valor:.1%}"


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tela: Tela = TelaRich() if RICH_DISPONIVEL else Tela()
    try:
        with tela.carregando("Carregando a base de conhecimento..."):
            assistente = Assistente()
    except BaseConhecimentoInvalida as erro:
        tela.erro(f"Não foi possível iniciar o Citizen Assist AI. {erro}")
        return 1
    try:
        AplicativoTerminal(assistente, tela).executar()
    except EncerrarPrograma:
        pass
    tela.texto("\nAté logo! Lembre-se de confirmar as orientações nos canais oficiais.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
