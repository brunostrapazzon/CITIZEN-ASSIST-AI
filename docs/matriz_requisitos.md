# Matriz de rastreabilidade de requisitos — Citizen Assist AI

Status possíveis: **Atendido** (código, teste executado e evidência), **Implementado (sem teste)**, **Preparado** (estrutura pronta, depende de ação humana) e **Pendente**.

Os testes citados foram executados com `python -m pytest`. A evidência de cada indicador é o arquivo `data/resultados_testes.json`, gerado por `python src/avaliar.py`.

## Requisitos funcionais e técnicos

| # | Requisito FIAP / mega prompt | Funcionalidade | Arquivo responsável | Comprovação | Teste | Status |
|---|---|---|---|---|---|---|
| 1 | Aplicação Python funcional, executada por `python src/sistema.py` | Programa de terminal completo | `src/sistema.py` | Execução manual e automática | `test_sistema.py::test_cli_inicia_e_encerra` | Atendido |
| 2 | Interface de terminal com menu (8 opções) | Menu, temas, consulta, palavras-chave, relacionados, fontes, funcionamento, privacidade, sair | `src/sistema.py` | Saída real no README, seção 22 | `test_cli_menus_no_mesmo_processo` (14 casos) | Atendido |
| 3 | Rich opcional, com alternativa sem a dependência | `Tela` (texto) e `TelaRich` | `src/sistema.py` | `CITIZEN_ASSIST_SEM_RICH=1` | `test_cli_funciona_sem_rich` | Atendido |
| 4 | Interface web (diferencial) | Streamlit com 6 páginas | `src/web_app.py` | Verificação visual (desktop e 375 px) | `test_web.py` (12 testes) | Atendido |
| 5 | Mesmo núcleo e mesmas respostas nas duas interfaces | Classe `Assistente` | `src/core/respostas.py` | As interfaces não leem o JSON nem criam o motor | `test_web_e_cli_usam_o_mesmo_nucleo`, `test_web_e_cli_mostram_a_mesma_fonte`, `test_resposta_estruturada_identica_entre_instancias` | Atendido |
| 6 | Base JSON com ≥ 15 registros em ≥ 3 categorias | 15 registros, 3 categorias | `data/base.json` | — | `test_base_real_e_valida`, `test_base_real_tem_pelo_menos_tres_categorias_com_registros` | Atendido |
| 7 | Campos obrigatórios em todos os registros | Validação completa | `src/core/validacoes.py` | — | `test_campo_obrigatorio_ausente`, `test_campo_com_tipo_errado` | Atendido |
| 8 | Fontes oficiais com URL verificável | URL `https` validada; páginas lidas em 17/11/2026 | `data/base.json` | README seção 17 | `test_todas_as_fontes_tem_url_https_oficial` | Atendido (formato automático; leitura manual registrada) |
| 9 | Normalização (minúsculas, acentos, pontuação, palavras) | `normalizar`, `tokenizar` | `src/core/busca.py` | — | `test_normalizar_*`, `test_tokenizar_*` | Atendido |
| 10 | Busca por identificador | `buscar_por_id`, consulta direta por código | `busca.py`, `respostas.py` | — | `test_busca_por_id`, `test_consulta_por_id` | Atendido |
| 11 | Busca por categoria | `listar_categoria`, filtro de categoria | `busca.py` | — | `test_listar_categoria`, `test_filtro_por_categoria` | Atendido |
| 12 | Busca por palavras-chave | Menu 3 com relevância e cobertura | `respostas.py`, `sistema.py` | — | `test_cli_menus_no_mesmo_processo` (menu 3) | Atendido |
| 13 | Índice invertido | `IndiceInvertido` | `busca.py` | — | `test_indice_invertido_aponta_registros_corretos` | Atendido |
| 14 | Pontuação de relevância | idf × peso do campo | `busca.py` | README seção 12 | `test_peso_do_titulo_maior_que_orientacao`, `test_confianca_entre_zero_e_um` | Atendido |
| 15 | Tratamento de empates e múltiplos resultados | Ordem por pontuação e código; status `ambiguo` com opções | `busca.py` | — | `test_ordem_estavel_em_empate`, `test_consulta_ambigua_apresenta_opcoes` | Atendido |
| 16 | Limite mínimo de relevância e baixa confiança | Cobertura e confiança mínimas | `busca.py` | — | `test_consulta_fora_do_tema_nao_responde`, `test_metade_da_pergunta_desconhecida_nao_gera_resposta` | Atendido |
| 17 | Grafo com dicionários e listas de adjacência | `construir_grafo` | `src/core/grafo.py` | README seção 13 | `test_grafo_tem_registros_e_categorias`, `test_grafo_nao_direcionado_e_sem_vertices_orfaos` | Atendido |
| 18 | Dijkstra com aplicação real | Trilha entre assuntos e relacionados do Modelo B | `grafo.py`, `respostas.py` | CLI menu 4; página Web "Navegar entre assuntos" | `test_dijkstra_igual_ao_oraculo_em_grafos_aleatorios`, `test_caso_calculado_a_mao`, `test_trilha_de_navegacao`, `test_web_trilha_dijkstra` | Atendido |
| 19 | Pesos definidos e documentados | 1,0 / 1,5 / 2,0 | `grafo.py` | README seção 13 | `test_pesos_documentados` | Atendido |
| 20 | Navegação entre assuntos relacionados | Botões (Web) e menu 4 (CLI) | `sistema.py`, `web_app.py` | — | `test_relacionados_por_proximidade` | Atendido |
| 21 | Dois modelos de resposta (A direta, B contextualizada) | `gerar_resposta_modelo_a/b` | `respostas.py` | README seção 14 | `test_consulta_bem_sucedida_modelo_a/b` | Atendido |
| 22 | Comparação dos modelos com perguntas equivalentes | `comparar_modelos` | `metricas.py` | `comparacao_modelos` em `resultados_testes.json` | `test_comparacao_dos_modelos` | Atendido |
| 23 | Nunca inventar orientação | Conteúdo só vem da base; abstenção sem suporte | `respostas.py` | — | `test_resposta_nunca_inventa_conteudo`, `test_sem_correspondencia_informa_claramente` | Atendido |
| 24 | Erros: entrada vazia, espaços, caracteres inválidos | `validar_entrada` | `validacoes.py` | — | `test_entrada_vazia`, `test_entrada_sem_letras_ou_numeros`, `test_entrada_com_caractere_de_controle` | Atendido |
| 25 | Erro: opção de menu inexistente | `validar_opcao_menu` | `validacoes.py`, `sistema.py` | — | `test_opcao_de_menu_inexistente`, `test_cli_trata_opcao_invalida_e_entrada_vazia` | Atendido |
| 26 | Erros: JSON ausente, vazio, malformado, falha de leitura | `carregar_base` | `base_conhecimento.py` | — | `test_arquivo_ausente`, `test_arquivo_vazio`, `test_json_malformado`, `test_cli_informa_base_invalida` | Atendido |
| 27 | Erros: IDs duplicados, referências inexistentes, dados inconsistentes | `validar_dados_base` | `validacoes.py` | — | `test_id_duplicado`, `test_referencia_inexistente`, `test_tema_fora_das_categorias` | Atendido |
| 28 | Falha isolada não encerra a aplicação | `try/except CitizenAssistError` no laço; Ctrl+C e fim da entrada tratados | `sistema.py` | — | `test_cli_encerra_sem_erro_quando_entrada_termina` | Atendido |
| 29 | Não pedir nem armazenar dados pessoais | Nenhum campo pessoal; nenhuma gravação de perguntas | `sistema.py`, `web_app.py` | Revisão do código; texto de privacidade | — | Implementado (verificado por revisão) |
| 30 | ≥ 12 cenários de teste (recomendado ≥ 20) | 30 cenários de 11 tipos | `data/testes.json` | — | `test_avaliacao_completa_tem_pelo_menos_12_cenarios` | Atendido |
| 31 | Métricas calculadas automaticamente (9 indicadores) | `calcular_indicadores` | `metricas.py` | `resultados_testes.json` | `test_indicadores_calculados_corretamente` | Atendido |
| 32 | Tempo com `time.perf_counter()` | Medição em `Assistente.consultar` | `respostas.py` | `tempo_ms` em cada resultado | `test_tempo_medido` | Atendido |
| 33 | Diferenciar correta / incorreta / abstenção correta / abstenção incorreta / falha técnica | `classificar` | `metricas.py` | — | `test_classificacao_dos_resultados` | Atendido |
| 34 | Interpretação dos resultados e ≥ 2 melhorias | README seções 19 e 24; relatório | `README.md`, `docs/relatorio.pdf` | — | — | Atendido |
| 35 | Roteiro de usabilidade (sem inventar participantes) | Roteiro aplicado e formulário preenchido | `docs/roteiro_usabilidade.md` | — | — | Atendido (aplicado em 17/11/2026, 1 participante) |
| 36 | README completo (25 itens) | — | `README.md` | — | — | Atendido (pendentes: link do vídeo, participação na competição e licença) |
| 37 | Relatório PDF de 4 a 8 páginas | Gerado a partir dos resultados reais | `docs/relatorio.pdf`, `scripts/gerar_relatorio_pdf.py` | Contagem de páginas na geração | — | Atendido |
| 38 | Documentação do uso de IA | — | `docs/uso_ia.md` | — | — | Atendido (revisado por toda a equipe) |
| 39 | Estrutura de pastas obrigatória | Caminhos exigidos presentes | raiz do projeto | Auditoria final | — | Atendido |
| 40 | Sem serviços pagos e sem internet na execução | Somente biblioteca padrão (+ opcionais locais) | — | — | Toda a suíte roda offline | Atendido |
| 41 | Preparação para GitHub (`.gitignore`, sem credenciais) | Repositório público | `.gitignore` | https://github.com/brunostrapazzon/CITIZEN-ASSIST-AI | — | Atendido |
| 42 | `docs/link_video.txt` com o link do YouTube (não listado) | — | `docs/link_video.txt` | — | — | Pendente (vídeo ainda não gravado) |
| 43 | Roteiro de apresentação com as duas interfaces | — | `docs/roteiro_apresentacao.md` | — | — | Atendido |
| 44 | Identificação da equipe no README e no PDF | "Equipe não nomeada" + 3 integrantes e RMs | `README.md`, relatório | — | — | Atendido |

## Enunciado oficial da FIAP (Global Solution 2026.2 — Citizen Assist AI)

| Exigência do enunciado | Onde é atendida | Teste / evidência | Status |
|---|---|---|---|
| ≥ 15 registros, ≥ 3 temas, campos id/tema/pergunta ou palavras-chave/orientação resumida/referência/data | `data/base.json` | `test_base_real_e_valida` | Atendido |
| ≥ 12 perguntas de teste (diretas, reformulações, fora do tema) | `data/testes.json` (30) | `test_avaliacao_completa_tem_pelo_menos_12_cenarios` | Atendido |
| ≥ 3 situações de limitação (vazia, ambígua, sem resposta confiável) | T18, T19, T20–T26, T30 | `data/resultados_testes.json` | Atendido |
| Registro de resultados (esperada, obtida, acerto, tempo) | `data/resultados_testes.json` | `src/avaliar.py` | Atendido |
| Ler a base em Python e apresentar os temas | menu 2; página Temas | `test_cli_menus_no_mesmo_processo` | Atendido |
| Acrescentar ou corrigir registros sem reescrever as regras | edição de `base.json` | README, "Como acrescentar ou corrigir uma orientação" | Atendido |
| Arquivo ausente, vazio ou inconsistente | `carregar_base` | `test_arquivo_ausente`, `test_arquivo_vazio`, `test_json_malformado` | Atendido |
| Recuperar por identificador, tema ou palavras-chave | `busca.py` | `test_busca_por_id`, `test_listar_categoria`, `test_busca_encontra_orientacao_esperada` | Atendido |
| Busca por pergunta ou por seleção de assunto | menus 1, 2 e 3 | `test_cli_pergunta_dentro_de_um_tema` | Atendido |
| Temas e subtemas em hierarquia ou grafo, com as relações explicadas | `grafo.py` (categoria → orientação + relações) | README seção 13 | Atendido |
| Navegação entre ≥ 3 assuntos com opções de continuidade | "Continue a consulta" (CLI), botões (Web), menu 4 | `test_cli_oferece_continuidade_apos_resposta`, `test_web_modelo_a_tambem_oferece_continuidade` | Atendido |
| Comportamento com várias correspondências | status `ambiguo` com opções | `test_consulta_ambigua_apresenta_opcoes` | Atendido |
| ≥ 2 modelos de prompt (papel, formato, obrigação de citar a fonte) | `INSTRUCAO_MODELO_A/B` | `test_modelos_documentam_papel_formato_e_fonte` | Atendido |
| Comparar os modelos e justificar | `comparar_modelos`; README seção 14 | `test_comparacao_dos_modelos` | Atendido |
| Aviso de limitação, sem inventar e sem alegar atendimento oficial | mensagens e avisos; `textos.py` | `test_sem_correspondencia_informa_claramente` | Atendido |
| Alternativas ou assuntos relacionados quando não há resposta adequada | `mostrar_alternativas` (CLI), botões de temas (Web) | `test_cli_sem_resultado_mostra_alternativas` | Atendido |
| Taxa de acerto e tempo médio de consulta | `calcular_indicadores` | `test_indicadores_calculados_corretamente` | Atendido |
| Teste de facilidade de uso com usuário ou roteiro de tarefas | roteiro + `data/usabilidade.json` + `calcular_usabilidade` | `test_usabilidade_calcula_indicadores` | Atendido (1 participante; tempo não medido) |
| Interpretar indicadores, ≥ 2 melhorias e limitações da avaliação | README seções 19, 23 e 24; relatório | — | Atendido |
| Uso de IA em `docs/uso_ia.md` | `docs/uso_ia.md` | — | Atendido (revisado por toda a equipe) |
| .TXT com os 2 links; GitHub público; vídeo não listado | `entrega_fiap.txt`, `docs/link_video.txt` | — | **Pendente**: depende da equipe |

## Ajustes de estrutura em relação ao modelo

- Arquivos auxiliares adicionados sem alterar os caminhos obrigatórios: `src/core/`, `src/web_app.py`, `src/avaliar.py`, `scripts/gerar_relatorio_pdf.py`, `tests/conftest.py`, `tests/test_web.py`, `docs/roteiro_apresentacao.md`, `data/historico/` e `.streamlit/config.toml`.
- O documento complementar da equipe listava `_init_.py`; o nome correto em Python é `__init__.py`, que foi o usado.
