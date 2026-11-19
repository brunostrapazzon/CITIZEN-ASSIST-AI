# FIAP - Faculdade de Informática e Administração Paulista

# 🧭 CITIZEN ASSIST AI

> Orientação cidadã simples, organizada e com fonte oficial.

**Graduação em Ciência da Computação · Global Solution — 2º semestre de 2026 · Desafio CitizenTech · Case Citizen Assist AI**

> Projeto acadêmico. Não é um canal oficial e não tem vínculo com órgãos públicos.

## 1. Identificação da equipe

### Equipe Rota Cidadã

### 👨‍🎓 Integrantes:

| Integrante | RM |
|---|---|
| Bruno Trevizan Strapazzon | RM573816 |
| Lucas Matheus Laitart | RM573137 |
| André Luiz Hlatchuk | RM571789 |

### 👩‍🏫 Professores:

**Tutor(a):** Lucas Gomes Jorge Gonçalez

**Coordenador(a):** <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a> (conforme o modelo de portfólio da coordenação)

**Participação na Competição:** [x] Sim, aceitamos participar / [ ] Não vamos participar.

## 📑 Sumário

| Tema | Seções |
|---|---|
| Problema e proposta | [3. Problema](#3-descrição-do-problema) · [4. Objetivo](#4-objetivo-da-solução) · [5. Público](#5-público-beneficiado) · [6. Temas](#6-temas-contemplados) |
| Solução | [7. Funcionalidades](#7-funcionalidades) · [8. Tecnologias](#8-tecnologias-utilizadas) · [9. Arquitetura](#9-arquitetura) · [10. Base de conhecimento](#10-estrutura-da-base-de-conhecimento) |
| Algoritmos | [11. Estruturas de dados](#11-estruturas-de-dados-utilizadas) · [12. Busca](#12-algoritmo-de-busca) · [13. Grafo e Dijkstra](#13-grafo-e-dijkstra) · [14. Modelos de prompt A e B](#14-estratégias-de-prompts-modelos-a-e-b) |
| Confiabilidade | [15. Tratamento de erros](#15-tratamento-de-erros) · [16. Privacidade, clareza e acessibilidade](#16-privacidade-e-responsabilidade) · [17. Fontes consultadas](#17-fontes-consultadas) |
| Avaliação | [18. Plano de testes](#18-plano-de-testes) · [19. Resultados](#19-resultados-reais) · [20. Indicadores](#20-indicadores-de-desempenho) |
| Uso | [21. Como executar](#21-como-executar) · [22. Exemplos](#22-exemplos-de-perguntas-e-respostas) · [25. Vídeo](#25-vídeo-de-apresentação) |
| Conclusão | [23. Limitações](#23-limitações) · [24. Evolução](#24-possibilidades-de-evolução) · [Licença](#-licença) |

## 2. Links do projeto

| Item | Endereço |
|---|---|
| Repositório GitHub | https://github.com/brunostrapazzon/CITIZEN-ASSIST-AI |
| Vídeo de apresentação (YouTube, não listado) | https://youtu.be/QpQYXNN09l8 |
| Relatório acadêmico | [`docs/relatorio.pdf`](docs/relatorio.pdf) |

---

## 3. Descrição do problema

Informações sobre documentos, serviços públicos e direitos estão espalhadas por dezenas de portais oficiais, cada um com sua organização. Quem tem pouca familiaridade com plataformas digitais tem dificuldade para descobrir **por onde começar**, **quais passos seguir** e **qual página é a oficial**. Isso favorece desinformação e intermediários desnecessários.

## 4. Objetivo da solução

Transformar informações públicas dispersas em **orientações curtas, organizadas e acessíveis**, sempre acompanhadas da **fonte oficial verificada** e da data da verificação. O assistente organiza o acesso à informação. Ele não substitui o atendimento oficial e nunca inventa uma orientação.

## 5. Público beneficiado

- Cidadãos com dificuldade para encontrar informações sobre serviços.
- Pessoas com pouca familiaridade com plataformas digitais.
- Quem precisa entender um procedimento burocrático passo a passo.
- Quem busca a fonte oficial para confirmar uma orientação.

## 6. Temas contemplados

15 orientações em 3 categorias. Todas as fontes foram lidas em **17/11/2026**.

| Documentação | Serviços públicos | Direitos e orientações cidadãs |
|---|---|---|
| DOC001 Carteira de Identidade Nacional (CIN) | SER001 Conta gov.br e seus níveis | DIR001 Direitos básicos do consumidor (CDC) |
| DOC002 CPF: consultar, atualizar e regularizar | SER002 Cadastro Único (CadÚnico) | DIR002 Reclamar de uma empresa no Consumidor.gov.br |
| DOC003 Carteira de Trabalho Digital | SER003 Meu INSS | DIR003 Acesso à informação pública |
| DOC004 Passaporte comum | SER004 Carteira Digital de Trânsito (app CNH do Brasil) | DIR004 Assistência social no CRAS |
| DOC005 Título de eleitor (primeiro título) | SER005 Encontrar serviços no portal gov.br | DIR005 Ouvidoria pública (Fala.BR) |

## 7. Funcionalidades

| Funcionalidade | Onde está |
|---|---|
| Consulta em linguagem natural, com resposta pelo Modelo A ou B | `src/core/respostas.py` → `Assistente.consultar` |
| Busca direta por código (ex.: `DOC004`) | `src/core/busca.py` → `MotorBusca.buscar_por_id` |
| Exploração por categoria | `MotorBusca.listar_categoria` |
| Pesquisa por palavras-chave com relevância e cobertura | `Assistente.pesquisar_palavras_chave` |
| Correção de erros de digitação simples | `IndiceInvertido.resolver` |
| Opções em consultas ambíguas e aviso de baixa confiança | `MotorBusca.buscar` |
| Alternativas de consulta quando não há resposta (lista dos temas e orientações) | `AplicativoTerminal.mostrar_alternativas` |
| "Continue a consulta": após cada resposta, até 3 assuntos relacionados para abrir | `AplicativoTerminal.exibir_e_continuar`; botões na Web |
| Pergunta dentro de um tema escolhido (ex.: tema = Documentação + pergunta) | menu 2 da CLI; filtro de categoria na Web |
| Assuntos relacionados por proximidade no grafo | `src/core/grafo.py` → `relacionados_por_proximidade` |
| Trilha de navegação entre dois assuntos (Dijkstra) | `grafo.caminho_minimo` / `Assistente.trilha` |
| Lista de fontes oficiais com data de verificação | `Assistente.fontes` |
| Avaliação automática com indicadores | `src/core/metricas.py`, `src/avaliar.py` |
| Interface de terminal com 8 opções de menu (Rich opcional) | `src/sistema.py` |
| Interface web responsiva | `src/web_app.py` |

## 8. Tecnologias utilizadas

- **Python 3.11+** (desenvolvido e testado com Python 3.14.8).
- **Biblioteca padrão:** `json`, `dataclasses`, `heapq`, `difflib`, `unicodedata`, `math`, `time.perf_counter`.
- **Rich** (opcional): visual do terminal. Sem ela, o programa usa texto simples.
- **Streamlit** (opcional): interface web.
- **pytest / pytest-cov:** testes e cobertura.
- **ReportLab:** geração do relatório PDF.

O projeto não usa API externa, serviço pago, banco de dados nem nuvem, e funciona sem internet.

## 9. Arquitetura

```
 python src/sistema.py ──┐                ┌── data/base.json
   (CLI — principal)     │                │
                         ├──> src/core/ ──┤
 streamlit run           │  Assistente    └── data/testes.json → data/resultados_testes.json
   src/web_app.py ───────┘  (porta única)
   (Web — diferencial)
```

| Módulo (`src/core/`) | Responsabilidade |
|---|---|
| `base_conhecimento.py` | Lê e converte a base JSON em objetos imutáveis |
| `validacoes.py` | Valida a base (campos, tipos, IDs, referências, URLs) e as entradas do usuário |
| `busca.py` | Normalização, índice invertido, relevância e classificação da consulta |
| `grafo.py` | Grafo de assuntos, Dijkstra, assuntos próximos e matriz de adjacência |
| `respostas.py` | Modelos A e B e a classe `Assistente`, usada pelas duas interfaces |
| `metricas.py` | Execução dos cenários, classificação e indicadores |
| `textos.py` | Textos de funcionamento, privacidade e limitações, comuns às interfaces |
| `erros.py` | Exceções próprias |

As duas interfaces são **camadas finas**: chamam as mesmas funções do núcleo e não contêm regras de busca. Um teste automatizado (`test_web_e_cli_usam_o_mesmo_nucleo`) impede que alguém duplique a lógica numa interface.

## 10. Estrutura da base de conhecimento

Cada registro de `data/base.json` segue o formato abaixo. Ele amplia o modelo sugerido com `resumo`, usado pelo Modelo A, e `limitacoes`, usado pelo Modelo B.

```json
{
  "id": "DOC004",
  "tema": "documentacao",
  "titulo": "Passaporte comum",
  "pergunta": "Como tirar o passaporte comum?",
  "palavras_chave": ["passaporte", "emitir passaporte", "Polícia Federal", "..."],
  "resumo": "Síntese de 1 a 2 frases (Modelo A).",
  "orientacao": "Explicação com contexto (Modelo B).",
  "passos": ["Passo 1", "Passo 2", "..."],
  "limitacoes": ["Custos, prazos e variações locais informados pela fonte"],
  "fonte": {"nome": "Polícia Federal (gov.br) — Obter passaporte", "url": "https://www.gov.br/..."},
  "data_verificacao": "2026-11-17",
  "aviso": "Orientação sujeita à confirmação nos canais oficiais.",
  "relacionados": ["DOC001", "DOC002"]
}
```

A base é validada a cada inicialização. Uma base inválida impede o programa de iniciar e mostra **todos** os problemas encontrados de uma vez.

## 11. Estruturas de dados utilizadas

| Estrutura | Uso |
|---|---|
| Dicionário `id → Registro` | Acesso direto O(1) por código |
| `dataclass(frozen=True)` | Registros e respostas imutáveis entre camadas |
| Índice invertido `dict[termo, dict[id, peso]]` | Localiza registros pelo termo sem varrer a base |
| Lista de adjacência `dict[nó, list[(vizinho, peso)]]` | Grafo de assuntos |
| Fila de prioridade (`heapq`) | Dijkstra |
| Matriz de adjacência | Exibição e documentação do grafo |
| Tuplas e listas | Passos, limitações, opções e resultados ordenados |

## 12. Algoritmo de busca

1. **Normalização:** minúsculas, remoção de acentos (`unicodedata`) e de pontuação.
2. **Tokenização:** remove palavras vazias ("como", "o", "meu"…) e reduz plurais simples ("direitos" → "direito", "federais" → "federal").
3. **Índice invertido:** cada termo aponta para os registros onde aparece, com o peso do campo. Título e palavras-chave valem 3, pergunta vale 2, resumo e orientação valem 1.
4. **Relevância:** `pontuação(d) = Σ fator(t) · idf(t) · peso(t, d)`, com `idf(t) = ln(1 + N/df(t))`. Termos raros, como "passaporte", valem mais que termos comuns, como "gov".
5. **Correção de digitação:** um termo desconhecido é comparado ao vocabulário (`difflib`, semelhança ≥ 0,8 e mesma letra inicial) e vale 0,7 do termo exato.
6. **Cobertura:** mede quanto da informação da pergunta (soma dos idf) o registro contém. Palavras desconhecidas reduzem a cobertura.
7. **Decisão:**
   - **sem resultado:** cobertura < 0,5 ou confiança < 0,35;
   - **ambíguo:** o 2º colocado tem ≥ 80% da pontuação do 1º, e as opções são mostradas;
   - **baixa confiança:** confiança < 0,6 ou cobertura < 0,6, e as opções aparecem com aviso;
   - **encontrado:** nos demais casos;
   - **empates:** decididos pelo código do registro, o que garante resultado determinístico.

**Por que essa estratégia?** Ela é explicável linha a linha, roda sem internet e sem dependências, e é rápida: o tempo médio medido por consulta fica abaixo de 1 ms. Além disso, a cobertura impede que **uma palavra em comum** gere uma resposta "confiável".

## 13. Grafo e Dijkstra

- **Vértices:** as 15 orientações e as 3 categorias (`CAT:documentacao`, `CAT:servicos_publicos`, `CAT:direitos_cidadania`).
- **Arestas:** o grafo não é direcionado, e cada aresta tem um custo de navegação:

| Ligação | Peso | Justificativa |
|---|---|---|
| Relação explícita entre orientações da mesma categoria | 1,0 | Assuntos diretamente ligados |
| Relação explícita entre categorias diferentes | 1,5 | Ligados, mas exigem mudar de contexto |
| Orientação ↔ sua categoria | 2,0 | Navegação genérica ("voltar ao tema") |

- **Dijkstra** (`src/core/grafo.py`) usa `heapq` com remoção preguiçosa e roda em O((V + E) log V). Ele tem dois usos reais:
  1. **Trilha de navegação** (CLI, menu 4, e página "Navegar entre assuntos" na Web). Exemplo real, saído da execução: `Documentação → Carteira de Identidade Nacional (CIN) → Conta gov.br e seus níveis → Serviços públicos` (custo 5,5). Quando há caminhos com o mesmo custo, o algoritmo devolve um deles.
  2. **Assuntos relacionados do Modelo B**, ordenados pelo custo da trilha.
- **Validação:** os testes comparam Dijkstra com **Floyd–Warshall** (oráculo independente) em 100 grafos aleatórios e no grafo real, além de um caso calculado à mão.

## 14. Estratégias de prompts (Modelos A e B)

O sistema **não usa IA externa**. Os "prompts" são **modelos de instrução aplicados à composição da resposta** (`INSTRUCAO_MODELO_A` e `INSTRUCAO_MODELO_B` em `src/core/respostas.py`). Cada modelo define quais seções existem, em que ordem e de qual campo da base o conteúdo vem.

| | Modelo A — Resposta direta | Modelo B — Resposta contextualizada |
|---|---|---|
| Seções | Orientação · Passo a passo · Fonte oficial · Aviso | Sua necessidade · Contexto · Passo a passo · Fonte oficial · Limitações e ressalvas · Assuntos relacionados · Aviso |
| Média de seções* | 4,0 | 7,0 |
| Média de palavras* | 127,1 | 251,8 |
| Respostas com fonte e aviso* | 17/17 | 17/17 |
| Mesma fonte nos dois modelos* | sim | sim |

\* Medido automaticamente nas 17 perguntas de teste que tiveram resposta (`comparacao_modelos` em `data/resultados_testes.json`).

**Conclusão:** os dois modelos foram **igualmente consistentes**: 100% das respostas têm fonte e aviso, e a fonte é a mesma nos dois.
- O **Modelo B** é o padrão porque é o único que mostra limitações, como custos, variações por estado e exceções, e assuntos relacionados. Isso reduz o risco de o cidadão agir com informação incompleta.
- O **Modelo A** é mais claro para quem só quer os passos, com metade do texto.

**Regra absoluta:** todo o texto exibido vem da base. Se a base não tem a informação, o sistema diz isso.

## 15. Tratamento de erros

| Situação | Comportamento |
|---|---|
| Entrada vazia ou só com espaços | Mensagem "A consulta está vazia" |
| Sem letras ou números / caracteres de controle / mais de 300 caracteres | Mensagem específica, sem processar |
| Opção de menu inexistente | Mostra as opções válidas e continua |
| Arquivo JSON ausente, vazio ou malformado | Mensagem clara (com linha e coluna, se malformado); o programa encerra com código 1, sem traceback |
| Registro sem campo obrigatório, tipo errado, ID duplicado, referência inexistente, URL inválida | Validação lista todos os problemas |
| Consulta ambígua | Mostra as opções para o usuário escolher |
| Nenhuma correspondência / baixa confiança | Informa que a base não tem orientação verificada / mostra as opções com aviso |
| Ctrl+C ou fim da entrada | Encerra com mensagem de despedida |
| Qualquer erro do núcleo durante o uso | Mostra a mensagem e volta ao menu, sem derrubar o programa |

## 16. Privacidade e responsabilidade

- O sistema **não pede** CPF, endereço, telefone ou qualquer dado pessoal.
- As perguntas **não são gravadas** nem associadas a quem perguntou.
- Toda resposta traz um aviso para confirmar a orientação no canal oficial.
- A identidade visual é própria, sem brasões ou elementos que sugiram vínculo com o governo.

### Clareza e acessibilidade

- **Linguagem simples:** frases curtas, passos numerados e um exemplo de pergunta em cada tela.
- **Pouca informação por vez:** o Modelo A tem só 4 seções; o Modelo B organiza o restante em seções com título.
- **Sem depender de cor:** na CLI, os avisos têm marcação em texto (`[ATENÇÃO]`, `[ERRO]`) e funcionam sem cores e sem a biblioteca Rich.
- **Web:** campos com rótulo visível, links com o nome da fonte (não "clique aqui"), contraste alto (texto `#0F1E3D` sobre fundo claro) e layout que funciona em telas de celular (testado em 375 px).
- **Tolerância a erros:** acentos, maiúsculas e erros simples de digitação são aceitos; a resposta informa quando uma palavra foi corrigida.

### Como acrescentar ou corrigir uma orientação

As regras do programa não precisam ser alteradas: basta editar `data/base.json`.
1. Copie um registro existente e troque o `id` (formato `AAA000`, ex.: `SER006`), mantendo todos os campos.
2. Preencha `fonte` com uma página oficial **lida por você** e `data_verificacao` com a data da leitura.
3. Ligue o novo registro a assuntos próximos em `relacionados` (ele entra automaticamente no grafo).
4. Rode `python -m pytest`: se faltar campo, houver ID repetido, referência inexistente ou URL inválida, o validador lista o problema.
5. Acrescente perguntas de teste em `data/testes.json` e rode `python src/avaliar.py`.

## 17. Fontes consultadas

As páginas abaixo foram abertas e lidas em 17/11/2026. Os textos da base são sínteses próprias delas.

| Código | Fonte |
|---|---|
| DOC001 | Governo Digital — Dúvidas Frequentes sobre a CIN: https://www.gov.br/governodigital/pt-br/identidade/cin/perguntas-frequentes-sobre-a-cin |
| DOC002 | Receita Federal — Atualizar CPF: https://www.gov.br/pt-br/servicos/atualizar-cadastro-de-pessoas-fisicas |
| DOC003 | Ministério do Trabalho e Emprego — Obter a Carteira de Trabalho: https://www.gov.br/pt-br/servicos/obter-a-carteira-de-trabalho |
| DOC004 | Polícia Federal — Obter passaporte: https://www.gov.br/pt-br/servicos/obter-passaporte-comum-para-brasileiro |
| DOC005 | TSE — Título Eleitoral (FAQ): https://www.tse.jus.br/servicos-eleitorais/titulo-eleitoral/titulo-eleitoral-faq |
| SER001 | Governo Digital — Níveis da conta gov.br: https://www.gov.br/governodigital/pt-br/identidade/conta-gov-br/niveis-da-conta-govbr |
| SER002 | MDS — Cadastro Único: https://www.gov.br/mds/pt-br/acoes-e-programas/cadastro-unico |
| SER003 | INSS — Saiba tudo sobre o Meu INSS: https://www.gov.br/inss/pt-br/canais_atendimento/meu-inss/meu-inss |
| SER004 | Ministério dos Transportes — Instalar aplicativo CDT: https://www.gov.br/pt-br/servicos/obter-carteira-digital-de-transito |
| SER005 | Portal gov.br — Serviços: https://www.gov.br/pt-br/servicos |
| DIR001 | Planalto — Lei nº 8.078/1990 (CDC): https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm |
| DIR002 | Consumidor.gov.br — Conheça o Consumidor.gov.br: https://www.consumidor.gov.br/pages/conteudo/publico/1 |
| DIR003 | Portal gov.br — Acesso à Informação: https://www.gov.br/acessoainformacao/pt-br |
| DIR004 | MDS — Acessar o CRAS: https://www.gov.br/pt-br/servicos/acessar-o-cras-centro-de-referencia-da-assistencia-social |
| DIR005 | Fala.BR — Plataforma Integrada de Ouvidoria e Acesso à Informação: https://falabr.cgu.gov.br/v2/ |

## 18. Plano de testes

**Testes automatizados** (`tests/`, pytest):

| Arquivo | O que cobre |
|---|---|
| `test_base.py` | Base real e todos os casos de erro de carregamento e validação |
| `test_busca.py` | Normalização, índice invertido, relevância, ambiguidade, erros de digitação e regressões |
| `test_grafo.py` | Dijkstra contra Floyd–Warshall, caso manual, casos-limite e grafo real |
| `test_sistema.py` | Modelos A/B, métricas, CLI real por subprocesso e todos os menus da CLI |
| `test_web.py` | Interface web pelo executor oficial do Streamlit (`AppTest`) |

**Avaliação de desempenho:** `data/testes.json` tem **30 cenários** de vários tipos: perguntas diretas, reformulações, palavras diferentes, palavras-chave, erros de digitação, ambíguas, fora do tema, sem correspondência, entrada vazia ou inválida e regressão. Cada cenário registra a orientação esperada e o comportamento esperado.

A classificação compara o resultado com o esperado. Retornar um texto qualquer não conta como acerto. As categorias são:
- **correta**
- **incorreta**
- **abstenção correta**
- **abstenção incorreta**
- **falha técnica**

**Usabilidade (facilidade de uso):** o roteiro de 5 tarefas está em [`docs/roteiro_usabilidade.md`](docs/roteiro_usabilidade.md). As sessões reais são registradas em `data/usabilidade.json`, e `python src/avaliar.py` calcula automaticamente a taxa de conclusão sem ajuda, o tempo médio por tarefa, a nota média (1 a 5) e a lista de dificuldades. **Resultado:** 1 participante (P1), sessão em 17/11/2026 usando a CLI e a Web: **5 de 5 tarefas concluídas sem ajuda (100%)**, nenhuma dificuldade registrada e **nota de facilidade 5 de 5**. Comentário do participante: "tudo muito prático e fácil de se usar". **Limites desta avaliação:** só uma pessoa participou, o tempo das tarefas não foi cronometrado e a mesma sessão usou as duas interfaces, então o resultado mostra que o fluxo funciona para um usuário, mas não permite generalizar. O próximo passo é repetir o roteiro com mais participantes, cronometrando cada tarefa.

## 19. Resultados reais

Valores gerados por `python src/avaliar.py` em **2026-11-18T21:23:54** (arquivo `data/resultados_testes.json`, Modelo B).

| Resultado | Quantidade |
|---|---|
| Corretas | 19 |
| Abstenções corretas | 7 |
| Incorretas | 1 |
| Abstenções incorretas | 3 |
| Falhas técnicas | 0 |

Cenários não atendidos:
- **T05** "documento de identidade novo, onde emito?" — o sistema se absteve. Ele não reconhece flexões de verbo ("emito" ≠ "emitir").
- **T14** "Onde fica o CRAS e o que ele oferece?" — mostrou a orientação certa só como opção, com baixa confiança, porque "fica" não está no índice.
- **T17** "como achar um serviço do governo federal" — o sistema se absteve. "achar" e "governo" não aparecem no registro SER005.
- **T30** "receita de bolo" — mostrou a orientação do CPF como opção, com aviso de baixa confiança. O correto seria se abster.

**Evolução:** a primeira execução (v1, guardada em `data/historico/`) acertou 27 de 29.
- Os testes revelaram três problemas: o plural "-ais" não era reduzido, a correção ortográfica trocava "emito" por "feito" e "receita de bolo" era **respondida** com a orientação do CPF.
- A v2 corrige os três. Para isso, a v2 é mais conservadora: prefere mostrar opções a responder com pouca certeza, o que custou o acerto direto do T14.

## 20. Indicadores de desempenho

| Indicador | Valor |
|---|---|
| Total de testes executados | 30 |
| Respostas corretas (corretas + abstenções corretas) | 26 |
| Respostas incorretas | 4 |
| **Taxa de acerto** | **86,7%** |
| Taxa de cobertura (respondíveis que receberam resposta ou opções) | 90,9% |
| Taxa de abstenção correta (sem suporte na base) | 87,5% |
| Tempo médio de consulta | 0,077 ms |
| Menor tempo | 0,0013 ms |
| Maior tempo | 0,1777 ms |
| Facilidade de uso: tarefas concluídas sem ajuda | 5 de 5 (100%), 1 participante |
| Facilidade de uso: nota média (1 a 5) | 5,0 |
| Facilidade de uso: tempo por tarefa | não medido |

Os tempos foram medidos com `time.perf_counter()` dentro de `Assistente.consultar`, em um computador com Windows 11 e Python 3.14.8.

Para os testes automatizados, os números atualizados aparecem ao rodar os comandos da seção 21.

## 21. Como executar

Execute os comandos a partir da raiz do projeto.

```bash
# 1. (Opcional) ambiente virtual
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux/macOS

# 2. Dependências (a CLI funciona até sem elas)
python -m pip install -r requirements.txt

# 3. Interface de terminal (principal)
python src/sistema.py

# 4. Interface web
streamlit run src/web_app.py

# 5. Testes automatizados e cobertura
python -m pytest
python -m pytest --cov=src --cov-report=term-missing

# 6. Avaliação de desempenho (regera data/resultados_testes.json)
python src/avaliar.py

# 7. Relatório PDF (regera docs/relatorio.pdf a partir dos resultados)
python scripts/gerar_relatorio_pdf.py
```

## 22. Exemplos de perguntas e respostas

As saídas abaixo foram copiadas da execução real de `python src/sistema.py`.

**Consulta com sucesso (Modelo A):**

```
--- Passaporte comum ---
Documentação · Modelo A (Resposta direta)

ORIENTAÇÃO
O passaporte comum é solicitado à Polícia Federal: formulário e pagamento on-line,
depois atendimento presencial agendado e retirada no mesmo posto.

PASSO A PASSO
  1. Preencha o formulário on-line de solicitação; o envio gera um protocolo e a taxa.
  2. Pague a taxa (PagTesouro por PIX ou cartão, boleto ou DDA).
  ...
FONTE OFICIAL
Polícia Federal (gov.br) — Obter passaporte — https://www.gov.br/pt-br/servicos/obter-passaporte-comum-para-brasileiro (verificado em 2026-11-17)

AVISO
[ATENÇÃO] Valores e prazos mudam. Confirme sempre na página oficial da Polícia Federal antes de pagar ou agendar.
```

**Consulta ambígua ("reclamação"):**

```
[ATENÇÃO] Encontrei mais de uma orientação parecida. Escolha a que corresponde à sua dúvida:
  1. Reclamar de uma empresa no Consumidor.gov.br (DIR002) — relevância 100%
  2. Ouvidoria pública: reclamações, denúncias e sugestões (Fala.BR) (DIR005) — relevância 100%
```

**Sem correspondência ("previsão do tempo amanhã"):**

```
[ATENÇÃO] A base do Citizen Assist AI não possui uma orientação verificada para essa pergunta.
Tente outras palavras, explore os temas disponíveis ou consulte o portal oficial gov.br.

--- Alternativas de consulta ---

Documentação:
  • Carteira de Identidade Nacional (CIN) (DOC001)
  • CPF: consultar, atualizar e regularizar (DOC002)
  ...
Dica: use o menu 2 para escolher um tema ou digite o código da orientação (ex.: DOC004).
```

**Trilha no grafo (menu 4, de CPF até Portal gov.br de serviços):**

```
✔ Trilha de menor custo (2.5): CPF: consultar, atualizar e regularizar → Conta gov.br e seus níveis → Encontrar serviços públicos no portal gov.br
```

## 23. Limitações

- A base cobre **15 assuntos**. Perguntas fora deles não são respondidas, e isso é intencional.
- As orientações são resumos com data de verificação e podem ficar desatualizadas. Valores e prazos, como as taxas do passaporte, mudam.
- A busca não entende todos os **sinônimos** ("achar" ≈ "encontrar") nem **conjugações** ("emito" ≈ "emitir"), como mostram os cenários T05 e T17.
- Os limiares de relevância foram ajustados com o mesmo conjunto de cenários usado na avaliação. Os números podem ser otimistas para perguntas novas, e um conjunto de validação separado seria o próximo passo.
- Regras que variam por estado ou município são sinalizadas, mas não detalhadas.
- O teste de usabilidade teve só 1 participante e não cronometrou as tarefas; o resultado não pode ser generalizado.

## 24. Possibilidades de evolução

1. **Lematização e sinônimos:** um dicionário de sinônimos revisado ("achar" → "encontrar") e a redução de verbos ("emito" → "emitir") resolveriam T05 e T17.
2. **Palavras vazias contextuais:** tratar verbos genéricos como "fica" e "achar" para não penalizar a cobertura (T14).
3. **Conjunto de validação separado** para calibrar os limiares sem viés.
4. Verificação automática periódica das URLs da base, com alerta de link quebrado.
5. Ampliação da base com orientações estaduais, separadas por estado.
6. Leitura em voz alta e modo de alto contraste na interface web.

## 25. Vídeo de apresentação

https://youtu.be/QpQYXNN09l8 (vídeo **não listado** no YouTube, também em `docs/link_video.txt`). Os roteiros estão em [`docs/roteiro_apresentacao.md`](docs/roteiro_apresentacao.md) e [`docs/roteiro_video.md`](docs/roteiro_video.md) (gravação em 3 partes).

---

## 📁 Estrutura de pastas

```
CITIZEN-ASSIST-AI/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   ├── sistema.py            # CLI (ponto de entrada obrigatório)
│   ├── web_app.py            # Interface web (Streamlit)
│   ├── avaliar.py            # Avaliação automática
│   └── core/                 # Núcleo compartilhado
├── data/
│   ├── base.json             # 15 orientações verificadas
│   ├── testes.json           # 30 cenários de avaliação
│   ├── usabilidade.json      # Registro das sessões reais de teste com usuário
│   ├── resultados_testes.json# Gerado automaticamente
│   └── historico/            # Resultados de versões anteriores
├── docs/
│   ├── relatorio.pdf
│   ├── link_video.txt
│   ├── uso_ia.md
│   ├── roteiro_usabilidade.md
│   ├── roteiro_apresentacao.md
│   ├── roteiro_video.md      # Gravação do vídeo em 3 partes
│   └── matriz_requisitos.md
├── scripts/
│   └── gerar_relatorio_pdf.py
├── tests/
│   ├── test_sistema.py  test_busca.py  test_grafo.py  test_base.py  test_web.py
└── .streamlit/config.toml    # Tema visual da interface web
```

## 🧠 Decisões Técnicas

- **CLI como interface principal e Web como diferencial**, ambas sobre o mesmo núcleo, para cumprir o comando obrigatório `python src/sistema.py` sem duplicar lógica.
- **Busca explicável** (índice invertido + idf + cobertura) em vez de modelo de linguagem, para garantir que nada seja inventado e que a equipe consiga justificar cada resultado.
- **Navegação com continuidade:** toda resposta termina com até 3 assuntos relacionados (vindos do grafo) para o usuário seguir a consulta, como pede o enunciado.
- **Abster-se é melhor do que errar:** quando a confiança é baixa, o sistema mostra opções ou admite que não sabe.

## 📋 Licença

Este projeto está licenciado sob a [Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.pt-br), a mesma licença do modelo de portfólio da FIAP. Ele pode ser usado, copiado, adaptado e compartilhado, desde que seja dado o crédito à Equipe Rota Cidadã (Bruno Trevizan Strapazzon, Lucas Matheus Laitart e André Luiz Hlatchuk) com o link para este repositório. Veja o arquivo [LICENSE](LICENSE).
