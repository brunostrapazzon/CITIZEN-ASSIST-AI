# Roteiro de teste de usabilidade — Citizen Assist AI

> **Situação: NÃO REALIZADO.** Este roteiro está pronto para ser aplicado. Nenhum resultado abaixo foi preenchido, e nenhuma participação foi simulada.

## Objetivo

Verificar se uma pessoa que **não participou do desenvolvimento** consegue usar o assistente sem ajuda e encontrar orientações com a fonte oficial.

## Perfil do participante

- Não pode ter participado do projeto.
- Preferencialmente, alguém com pouca familiaridade com serviços digitais do governo.
- Não é preciso coletar nome, CPF ou contato. Use apenas um código (P1, P2…).

## Preparação

1. Abrir a interface escolhida:
   - terminal: `python src/sistema.py`;
   - Web: `streamlit run src/web_app.py`.
2. Explicar apenas: "Este é um assistente de orientação cidadã. Vou pedir algumas tarefas. Pense em voz alta."
3. Não ajudar durante as tarefas. Anotar onde a pessoa hesita.
4. Medir o tempo de cada tarefa com um cronômetro, do enunciado até a conclusão ou desistência.

## Tarefas

| # | Tarefa lida ao participante | Critério de sucesso |
|---|---|---|
| 1 | "Descubra como tirar o passaporte." | Chega à orientação DOC004 e lê os passos |
| 2 | "Descubra como se inscrever no Cadastro Único." | Chega à orientação SER002 |
| 3 | "Encontre o endereço do site oficial que confirma a orientação do passaporte." | Aponta a URL da Polícia Federal na seção Fonte oficial |
| 4 | "Pergunte qual será a previsão do tempo amanhã." | Entende que o assistente não tem essa informação |
| 5 | "A partir do passaporte, vá para um assunto relacionado." | Usa "Continue a consulta" ou o menu 4 (CLI), ou um botão de assunto relacionado (Web) |

> **Depois do teste:** copie os resultados de cada participante para `data/usabilidade.json` (lista `sessoes`, seguindo o exemplo do arquivo) e rode `python src/avaliar.py`. A taxa de conclusão, o tempo médio por tarefa, a nota média e as dificuldades são calculados automaticamente e aparecem no menu 6 e na página "Como funciona". Depois, peça a atualização do README e do relatório.

## Formulário de registro (preencher durante o teste)

**Participante:** PREENCHER (código) · **Interface:** PREENCHER (CLI/Web) · **Data:** PREENCHER

| Tarefa | Resultado (concluiu / com dificuldade / não concluiu) | Tempo | Dificuldade encontrada | Comentários do participante | Sugestão de melhoria |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

## Perguntas finais

1. De 1 (muito difícil) a 5 (muito fácil), quão fácil foi usar o assistente? ____
2. Você confiaria na orientação? Por quê? ____
3. O que mais atrapalhou? ____
4. O que você mudaria? ____

## Consolidação (após aplicar)

- Número de participantes: PREENCHER
- Tarefas concluídas sem ajuda: PREENCHER
- Principais dificuldades: PREENCHER
- Melhorias priorizadas: PREENCHER
