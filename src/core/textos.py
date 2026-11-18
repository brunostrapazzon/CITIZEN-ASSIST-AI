"""Textos institucionais compartilhados pela CLI e pela Web.

Ficam no núcleo para que as duas interfaces mostrem exatamente o mesmo
conteúdo sobre funcionamento, privacidade e limitações.
"""

NOME = "CITIZEN ASSIST AI"
SLOGAN = "Orientação cidadã simples, organizada e com fonte oficial."
AVISO_INSTITUCIONAL = (
    "Projeto acadêmico da FIAP (Global Solution 2026.2 — CitizenTech). "
    "Não é um canal oficial e não tem vínculo com órgãos públicos."
)

COMO_FUNCIONA = (
    ("Base de conhecimento",
     "As orientações ficam em data/base.json. Cada uma é uma síntese própria de uma página oficial, "
     "com o órgão responsável, o endereço e a data em que foi verificada."),
    ("Busca",
     "A pergunta é normalizada (sem acentos, pontuação e palavras vazias) e procurada em um índice "
     "invertido. Cada orientação recebe uma pontuação de relevância que valoriza termos raros e "
     "campos importantes, como título e palavras-chave."),
    ("Confiança",
     "Se a orientação cobre pouco da pergunta, o assistente não responde. Se duas orientações ficam "
     "muito próximas, ele mostra as opções em vez de escolher sozinho."),
    ("Grafo e Dijkstra",
     "As orientações e as categorias formam um grafo com pesos. O algoritmo de Dijkstra calcula a "
     "trilha mais curta entre dois assuntos e ordena os assuntos relacionados por proximidade."),
    ("Dois modelos de resposta",
     "Modelo A (direta): orientação curta, passos, fonte e aviso. Modelo B (contextualizada): "
     "necessidade, contexto, passos, fonte, limitações, assuntos relacionados e aviso."),
    ("Sem inteligência artificial externa",
     "Não há chamada a serviços de IA. Os 'prompts' são modelos de instrução aplicados à montagem "
     "da resposta, sempre com o conteúdo da base. O sistema funciona sem internet."),
)

PRIVACIDADE = (
    "O Citizen Assist AI não pede CPF, endereço, telefone ou qualquer dado pessoal.",
    "As perguntas não são gravadas nem associadas a quem perguntou.",
    "Não digite dados pessoais nas perguntas: eles não são necessários para receber uma orientação.",
    "Para usar um serviço público de verdade, acesse o canal oficial indicado na fonte.",
)

LIMITACOES = (
    "As orientações são resumos e podem ficar desatualizadas; confira sempre a fonte oficial e a data de verificação.",
    "A base cobre 15 assuntos em 3 categorias. Perguntas fora desses assuntos não são respondidas.",
    "Regras que variam por estado ou município são sinalizadas, mas não detalhadas.",
    "A busca entende variações simples de escrita, mas não entende todos os sinônimos e conjugações.",
    "O assistente não substitui atendimento oficial, advogado, Defensoria Pública ou outro profissional.",
)
