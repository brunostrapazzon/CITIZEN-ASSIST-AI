# Uso de inteligência artificial no desenvolvimento

## Ferramenta utilizada

| Ferramenta | Tipo | Ambiente |
|---|---|---|
| Assistente de programação baseado em IA (modelo de linguagem) | Agente de desenvolvimento com acesso ao terminal e ao navegador | Computador da equipe, Windows 11 |

Recursos do assistente usados:
- instruções de engenharia (desenvolvimento orientado a testes, depuração sistemática, verificação antes de concluir);
- instruções específicas criadas para este projeto (arquitetura, grafos, busca, testes, validação de dados, documentação e interface web);
- leitura automática de páginas oficiais;
- navegador para conferir páginas que dependem de JavaScript e a interface web.

O **sistema entregue não usa IA**: ele não chama nenhum modelo de linguagem e funciona sem internet. A IA foi usada somente como **ferramenta de apoio ao desenvolvimento**.

## Finalidade e etapas apoiadas por IA

| Etapa | Como a IA apoiou |
|---|---|
| Configuração do ambiente | Definição das instruções de trabalho do assistente para o projeto |
| Análise do desafio | Leitura do repositório-modelo da FIAP e montagem da matriz de requisitos |
| Pesquisa de fontes | Leitura das 15 páginas oficiais e síntese do conteúdo (ver "Verificação das fontes") |
| Arquitetura e código | Proposta da arquitetura (núcleo compartilhado), escrita dos módulos e das interfaces |
| Testes | Escrita dos testes antes do código (TDD), criação dos 30 cenários, execução e diagnóstico das falhas |
| Documentação | Redação do README, desta documentação, dos roteiros e do relatório PDF |

## Prompts utilizados

Os prompts abaixo foram escritos pela equipe e enviados ao assistente, nesta ordem:

1. **Configuração do assistente:** pedido de recursos de planejamento, testes, revisão de código, depuração e documentação.
2. **Instruções específicas do projeto:** pedido para criar orientações de trabalho sobre arquitetura Python, grafos, busca, testes e métricas, validação de dados, documentação acadêmica e Streamlit.
3. **Complemento oficial da equipe:** decisões sobre as duas interfaces (CLI principal e Web como diferencial), núcleo compartilhado, identidade visual própria, estrutura de arquivos e identificação da equipe.
4. **Mega prompt da Global Solution:** requisitos completos do produto, como base com ≥ 15 registros verificados, busca com índice invertido, grafo e Dijkstra, Modelos A e B, tratamento de erros, ≥ 12 testes com métricas reais, README, relatório e roteiros.

Em todos os prompts a equipe deu a mesma instrução central: **não inventar informações, URLs, resultados ou participação de pessoas**.

## Sugestões da IA incorporadas

- Núcleo único (`Assistente`) usado pelas duas interfaces, com um teste que impede a duplicação de lógica.
- Medida de **cobertura** da pergunta para evitar respostas baseadas em uma única palavra em comum.
- Uso de **Floyd–Warshall como oráculo** para comprovar a correção do Dijkstra.
- Uso do Dijkstra também para ordenar os assuntos relacionados do Modelo B.
- Classificação dos resultados em cinco categorias (correta, incorreta, abstenção correta, abstenção incorreta, falha técnica).

## Problemas encontrados pela IA durante os testes e corrigidos

1. O plural "-ais" não era reduzido ("federais" ≠ "federal").
2. A correção ortográfica trocava "emito" por "feito". Agora ela exige a mesma letra inicial.
3. "receita de bolo" era respondida com a orientação do CPF. Agora o sistema exige 60% de cobertura para responder.
4. Um exemplo de trilha escrito no README não correspondia à execução real e foi substituído pelo resultado executado.

## Verificação das fontes

- Cada uma das 15 páginas oficiais foi **aberta e lida** em 17/11/2026, por leitura automática (subagentes) ou pelo navegador embutido, no caso de páginas que dependem de JavaScript.
- Seis páginas não puderam ser lidas na primeira tentativa (erro 404, bloqueio 403 ou conteúdo carregado por JavaScript). Elas só entraram na base depois de lidas no navegador.
- Informações que vieram de **resumo automático**, e não do texto da página, foram conferidas no texto original antes de entrar na base (Meu INSS e Cadastro Único).
- Achado relevante: a página oficial da "Carteira Digital de Trânsito" já chama o aplicativo de **"CNH do Brasil"**, e isso foi registrado na base.

## Validação das respostas

- Todo número de desempenho vem da execução de `python src/avaliar.py`. Nenhum foi digitado à mão.
- Todo teste citado na documentação foi executado.
- A IA não tem acesso a usuários reais, por isso o teste de usabilidade **não foi realizado**. Ele ficou preparado para a equipe.

## Limitações identificadas no uso de IA

- A IA pode produzir texto plausível e errado. Exemplo deste projeto: a trilha citada no README estava errada e foi detectada na conferência.
- Resumos automáticos de páginas longas chegaram a contradizer o texto original. Exemplo: os níveis da conta gov.br apareceram com outros nomes no resumo. Por isso, todo dado da base foi conferido no texto lido.
- Os limiares da busca foram ajustados com o mesmo conjunto de cenários usado na avaliação, o que pode tornar os números otimistas.

## Participação humana

A equipe definiu o problema, o escopo, as decisões de arquitetura (duas interfaces e núcleo compartilhado) e as regras de rigor acadêmico, e enviou todos os prompts.

**Revisão da equipe:**
- PREENCHER — quem revisou o quê e quando (código, base de conhecimento, documentação).
- PREENCHER — alterações feitas pela equipe após a revisão.
- PREENCHER — confirmação de que todos os integrantes entendem e conseguem explicar a busca, o grafo/Dijkstra e as métricas.

> A IA foi usada como ferramenta de apoio. A responsabilidade pela compreensão, validação e apresentação da solução é da equipe.
