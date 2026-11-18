"""Exceções próprias do Citizen Assist AI.

As interfaces capturam CitizenAssistError para mostrar mensagens amigáveis,
sem expor detalhes técnicos ao cidadão.
"""


class CitizenAssistError(Exception):
    """Erro base de todo o sistema."""


class BaseConhecimentoInvalida(CitizenAssistError):
    """A base JSON não pôde ser lida ou não passou na validação."""

    def __init__(self, mensagem: str, problemas: list[str] | None = None) -> None:
        self.problemas = problemas or []
        detalhes = "".join(f"\n  - {p}" for p in self.problemas)
        super().__init__(mensagem + detalhes)


class EntradaInvalida(CitizenAssistError):
    """Texto digitado pelo usuário não pode ser processado."""


class RegistroNaoEncontrado(CitizenAssistError):
    """Identificador de orientação (ou nó do grafo) inexistente."""


class CaminhoInexistente(CitizenAssistError):
    """Não há caminho no grafo entre os dois assuntos pedidos."""
