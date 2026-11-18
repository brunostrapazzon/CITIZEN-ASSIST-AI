# Roteiro do vídeo — gravação em 3 partes separadas

> **Divisão da gravação definida pela equipe:** Parte 1 — Bruno Trevizan Strapazzon · Parte 2 — Lucas Matheus Laitart · Parte 3 — André Luiz Hlatchuk. A divisão vale apenas para a gravação do vídeo e não representa uma divisão de responsabilidades no desenvolvimento do projeto.

**Duração-alvo:** cerca de 8 minutos no total (Parte 1 ≈ 2:30 · Parte 2 ≈ 3:00 · Parte 3 ≈ 2:30). Confirmem o tempo máximo exigido pela FIAP e ajustem.

Todos os números citados vêm de `data/resultados_testes.json` e da execução real do sistema. Se o sistema mudar antes da gravação, confiram os números de novo.

---

## Combinados antes de gravar (todos)

| Item | Padrão |
|---|---|
| Resolução | 1920×1080, 30 fps |
| Formato | MP4 |
| Áudio | Microfone próximo, ambiente silencioso, sem música de fundo (a música, se houver, entra na edição) |
| Tela | Terminal em tela cheia, fonte grande (tamanho 16 ou mais), tema escuro ou claro, mas o mesmo para os três |
| Câmera (opcional) | Se alguém aparecer, todos aparecem, no mesmo canto da tela |
| Nome do arquivo | `parte1.mp4`, `parte2.mp4`, `parte3.mp4` |
| Margem | 2 segundos de silêncio no início e no fim de cada parte (facilita o corte) |
| Pasta | Raiz do projeto, com o ambiente virtual ativado (`.venv\Scripts\activate`) |

Testem antes:

```bash
python src/sistema.py
```

```bash
python -m pytest
```

```bash
streamlit run src/web_app.py
```

Para a gravação, a pessoa só lê a fala em **negrito** e digita o que está em `código`. Os demais textos são instruções.

---

## PARTE 1 — Problema, proposta e base de conhecimento (≈ 2:30)

**Gravado por:** Bruno Trevizan Strapazzon (RM573816)

### Cena 1.1 — Abertura (0:00–0:20) · Tela: slide ou README aberto

> **"Olá! Este é o Citizen Assist AI, projeto da Global Solution do segundo semestre de 2026 da FIAP, no desafio CitizenTech. Somos a equipe formada por Bruno Trevizan Strapazzon, Lucas Matheus Laitart e André Luiz Hlatchuk."**

### Cena 1.2 — O problema (0:20–0:50) · Tela: slide simples ou navegador com o portal gov.br

> **"Informações sobre documentos, serviços públicos e direitos estão espalhadas por dezenas de portais oficiais. Para quem tem pouca familiaridade com o mundo digital, a dificuldade começa antes do serviço: saber por onde começar, quais passos seguir e qual página é realmente a oficial."**

### Cena 1.3 — A proposta (0:50–1:20) · Tela: terminal

Digite `python src/sistema.py` e deixe o cabeçalho e o menu aparecerem.

> **"O Citizen Assist AI organiza essas informações em orientações curtas, sempre com a fonte oficial e a data em que ela foi verificada. Ele não é um canal oficial e tem uma regra absoluta: nunca inventar uma orientação. Se a base não tem a resposta, ele diz que não sabe."**

### Cena 1.4 — A base de conhecimento (1:20–2:10) · Tela: terminal

Digite `5` (Visualizar fontes oficiais) e role a lista devagar.

> **"A base tem 15 orientações em três categorias: documentação, serviços públicos e direitos do cidadão. Cada uma foi escrita a partir de uma página oficial, como gov.br, Polícia Federal, TSE, Planalto e Consumidor.gov.br, todas lidas e conferidas em 17 de novembro de 2026. Aqui aparecem o órgão, o endereço e a data de verificação de cada fonte."**

Pressione Enter para voltar ao menu.

### Cena 1.5 — Arquitetura e passagem (2:10–2:30) · Tela: README, seção 9 (Arquitetura)

> **"O sistema é feito em Python e funciona sem internet. Um único núcleo de processamento atende duas interfaces: o terminal, que é a principal, e uma interface web. A seguir, vamos ver o assistente funcionando."**

> **"Agora o Lucas vai mostrar o assistente funcionando."**

*(Fim da Parte 1.)*

---

## PARTE 2 — O assistente funcionando no terminal (≈ 3:00)

**Gravado por:** Lucas Matheus Laitart (RM573137)

Comece com o terminal já aberto em `python src/sistema.py`, no menu principal.

### Cena 2.1 — Consulta bem-sucedida, Modelo A (0:00–0:40)

Digite `1`, depois `Como tirar o passaporte?`, depois `A`.

> **"Vou perguntar como tirar o passaporte, escolhendo o Modelo A, a resposta direta. Ela traz a orientação curta, o passo a passo numerado, a fonte oficial da Polícia Federal com o endereço e um aviso para confirmar valores e prazos. No final, o assistente sugere assuntos relacionados para continuar a consulta."**

Aponte com o mouse para a seção FONTE OFICIAL. Pressione Enter.

### Cena 2.2 — A mesma pergunta, Modelo B (0:40–1:15)

Digite `1`, depois `Como tirar o passaporte?`, depois `B` (ou só Enter).

> **"Agora a mesma pergunta no Modelo B, a resposta contextualizada. Além dos passos e da fonte, ele explica o contexto, mostra as limitações, como taxas e prazos, e sugere assuntos relacionados. Nos testes, os dois modelos mostraram fonte e aviso em todas as respostas. O B é o padrão porque não esconde as ressalvas."**

Role até LIMITAÇÕES E RESSALVAS e ASSUNTOS RELACIONADOS. Pressione Enter.

### Cena 2.3 — Consulta ambígua (1:15–1:40)

Digite `1`, depois `reclamação`, depois `B`.

> **"Se eu digito só 'reclamação', existem dois caminhos possíveis: reclamar de uma empresa ou de um serviço público. Em vez de escolher sozinho, o assistente mostra as duas opções."**

Digite `2` para abrir o Fala.BR. Pressione Enter.

### Cena 2.4 — Sem correspondência e entrada inválida (1:40–2:10)

Digite `1`, depois `previsão do tempo amanhã`, depois `B`.

> **"Quando a pergunta está fora dos temas, ele não inventa: avisa que a base não tem uma orientação verificada e mostra as alternativas de consulta que existem."**

Pressione Enter. Digite `99`.

> **"Opções que não existem e perguntas vazias também são tratadas, sem travar o programa."**

Digite `1` e pressione Enter com a pergunta vazia. Pressione Enter de novo.

### Cena 2.5 — Grafo e Dijkstra (2:10–3:00)

Digite `4`, depois `7` (CPF) como partida.

> **"Os assuntos formam um grafo com pesos. Ligações entre assuntos da mesma categoria custam 1, entre categorias diferentes custam 1,5, e a ligação de um assunto com sua categoria custa 2. Esta tabela mostra os assuntos mais próximos do CPF, calculados pelo algoritmo de Dijkstra."**

Digite `15` (Encontrar serviços públicos no portal gov.br) como destino.

> **"E aqui o Dijkstra encontra a trilha de menor custo: do CPF para a Conta gov.br e dela para os serviços públicos, com custo 2,5. A mesma lógica ordena os assuntos relacionados do Modelo B."**

Pressione Enter e digite `8` para sair.

> **"Para fechar, o André vai mostrar os testes, os resultados e a interface web."**

---

## PARTE 3 — Testes, resultados, interface web e conclusão (≈ 2:30)

**Gravado por:** André Luiz Hlatchuk (RM571789)

### Cena 3.1 — Testes automatizados (0:00–0:30) · Tela: terminal

Digite `python -m pytest` e espere o resumo final.

> **"O projeto tem testes automatizados para a base, a busca, o grafo, os modelos de resposta, o terminal e a interface web. O Dijkstra, por exemplo, é comparado com outro algoritmo, o Floyd–Warshall, em 100 grafos aleatórios. Todos os testes passaram."**

*(Confira na tela o número de testes aprovados antes de falar. Na última execução foram 133.)*

### Cena 3.2 — Indicadores de desempenho (0:30–1:20) · Tela: terminal

Digite `python src/sistema.py`, depois `6` (Conhecer o funcionamento) e role até a tabela de indicadores.

> **"Também criamos 30 cenários de avaliação: perguntas diretas, reformulações, erros de digitação, perguntas ambíguas e perguntas fora do tema. O sistema acertou 26 dos 30, uma taxa de 86,7%, e se absteve corretamente em 87,5% das perguntas sem resposta na base. Cada consulta leva menos de um milissegundo."**

> **"O teste de facilidade de uso segue um roteiro de cinco tarefas com uma pessoa de fora da equipe, e os indicadores são calculados pelo próprio sistema."** *(Só diga esta frase se o teste já tiver sido feito e registrado. Se não foi, diga: "O teste de facilidade de uso está preparado e será aplicado com uma pessoa de fora da equipe.")*

> **"Os testes também mostraram falhas, e preferimos mostrá-las: o assistente ainda não entende alguns sinônimos e verbos conjugados, como 'achar' no lugar de 'encontrar'. Essa é a principal melhoria planejada."**

Pressione Enter e digite `8`.

### Cena 3.3 — Interface web (1:20–2:05) · Tela: navegador

Digite `streamlit run src/web_app.py` e espere o navegador abrir.

> **"Como diferencial, criamos uma interface web que usa exatamente o mesmo núcleo do terminal."**

Digite `Como tirar o passaporte?` no campo e clique em **Consultar**. Role até a fonte.

> **"A mesma pergunta traz a mesma resposta e a mesma fonte oficial, agora com links clicáveis."**

Clique em um botão de **Assuntos relacionados**. Depois, na barra lateral, clique em **Navegar entre assuntos**.

> **"Aqui dá para navegar entre assuntos e ver a trilha calculada pelo Dijkstra."**

### Cena 3.4 — Limitações e conclusão (2:05–2:30) · Tela: README, seção 23, ou a página "Privacidade e limitações" da web

> **"O assistente não pede nenhum dado pessoal e não guarda as perguntas. Ele cobre 15 assuntos e não substitui o atendimento oficial. Nossa conclusão: em orientação ao cidadão, uma resposta confiável vale mais do que uma resposta rápida, e o Citizen Assist AI prefere admitir que não sabe a inventar. Obrigado!"**

---

## Montagem (quem editar)

1. Ordem: `parte1.mp4` → `parte2.mp4` → `parte3.mp4`.
2. Cortar os 2 segundos de silêncio do começo e do fim de cada parte.
3. Entre as partes, usar uma transição simples (corte seco ou fade de 0,5 s) e, se quiserem, uma tela de 2 s com o título da próxima parte:
   - "O assistente funcionando"
   - "Testes, resultados e interface web"
4. Normalizar o volume das três partes (o mesmo nível para todas as vozes).
5. Legenda com o nome de quem fala no canto inferior, nos primeiros segundos de cada parte: "Bruno Trevizan Strapazzon — RM573816", "Lucas Matheus Laitart — RM573137" e "André Luiz Hlatchuk — RM571789".
6. Exportar em MP4, 1080p.
7. Publicar no YouTube como **NÃO LISTADO**.
8. Colocar o link em `docs/link_video.txt`, no `README.md` (seções 2 e 25) e em `entrega_fiap.txt`.

## Checklist final do vídeo

- [ ] Os três integrantes e os RMs aparecem ou são citados.
- [ ] O nome da equipe aparece como "Equipe não nomeada" (ou o nome decidido).
- [ ] Os números falados conferem com a tela.
- [ ] As duas interfaces aparecem.
- [ ] Nenhuma funcionalidade mostrada ou citada deixa de existir no código.
- [ ] O vídeo está como não listado e o link funciona numa janela anônima.
