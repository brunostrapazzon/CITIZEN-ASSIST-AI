# Roteiro de apresentação — Citizen Assist AI

Duração sugerida: cerca de 8 minutos. Tudo o que aparece no roteiro existe e foi executado. Os números citados vêm de `data/resultados_testes.json`.

> **Gravação em partes:** o roteiro detalhado, dividido entre os três integrantes conforme definido pela equipe, está em [`roteiro_video.md`](roteiro_video.md).

| # | Momento | O que mostrar / falar | Tempo |
|---|---|---|---|
| 1 | Problema | Informações públicas espalhadas em muitos portais; dificuldade de saber por onde começar e qual página é oficial. | 0:40 |
| 2 | Proposta | Assistente que organiza orientações curtas, sempre com fonte oficial e data de verificação. Não é canal oficial e nunca inventa. | 0:30 |
| 3 | Interface funcionando (CLI) | `python src/sistema.py` → cabeçalho e menu de 8 opções. | 0:20 |
| 4 | Consulta bem-sucedida | Menu 1 → "Como tirar o passaporte?" → Modelo A. Depois a mesma pergunta no Modelo B (necessidade, contexto, limitações, relacionados). | 1:00 |
| 5 | Fonte oficial | Destacar a seção Fonte oficial (Polícia Federal, URL e data). Menu 5: lista das 15 fontes. | 0:30 |
| 6 | Múltiplos resultados | Menu 1 → "reclamação" → o sistema mostra Consumidor.gov.br e Fala.BR para o usuário escolher. | 0:30 |
| 7 | Navegação entre assuntos | Menu 4 → partida DOC002 (CPF) → tabela dos mais próximos → destino SER005 → trilha por Dijkstra (custo 2,5). Explicar os pesos 1,0 / 1,5 / 2,0. | 1:00 |
| 8 | Sem correspondência | Menu 1 → "previsão do tempo amanhã" → o sistema informa que não tem orientação verificada. | 0:20 |
| 9 | Entrada inválida | Menu "99" → opção inexistente; menu 1 com pergunta vazia → mensagem clara. | 0:20 |
| 10 | Execução dos testes | `python -m pytest` (mostrar o resumo de testes aprovados) e `python src/avaliar.py`. | 0:40 |
| 11 | Indicadores | Menu 6: 30 testes, taxa de acerto de 86,7%, abstenção correta de 87,5%, tempo médio abaixo de 0,1 ms. Explicar honestamente os 4 casos não atendidos. | 0:50 |
| 12 | Diferenciais técnicos | Índice invertido + idf + cobertura; Dijkstra comprovado contra Floyd–Warshall; **interface web** (`streamlit run src/web_app.py`) com o mesmo núcleo: repetir a consulta do passaporte e mostrar a mesma fonte; página de trilha; tela de celular. | 1:00 |
| 13 | Limitações | Sinônimos e conjugações (T05, T17), base com 15 assuntos, limiares ajustados nos mesmos cenários, teste de usabilidade ainda não feito. | 0:30 |
| 14 | Conclusão | Orientação confiável é melhor do que resposta rápida: o assistente prefere admitir que não sabe a inventar. | 0:20 |

## Checklist antes de gravar

- [ ] `python -m pytest` passando na máquina da gravação.
- [ ] `python src/avaliar.py` executado e números do roteiro conferidos com `data/resultados_testes.json`.
- [ ] Terminal com fonte legível e janela larga.
- [ ] Streamlit aberto em outra janela.
- [ ] Vídeo publicado no YouTube como **não listado** e link colocado em `docs/link_video.txt` e no README.
