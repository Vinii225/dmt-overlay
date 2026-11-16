# Changelog

Todas as mudanças relevantes do projeto. O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto usa [versionamento semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

## [0.3.0-beta.2] - 2026-11-16

Versão de teste com tudo da 0.3.0 (a beta.1 não chegou a ser publicada). Roteiro para uma sessão só, uns 40 minutos:

**Sem o jogo (modo demonstração)**
1. Bandeja → **Configurações…** → Geral → Fonte de dados: **Demonstração**. Destrave, arraste uns widgets e trave.
2. Aparência → Tema **Transmissão** (e volte, se quiser).
3. Ligue **Volante e inputs** e **Rivais: pneus e VE** nas páginas deles. No volante, ajuste o **Giro do volante** para o do seu carro.
4. **Transmissão** → Ligar HUD → **Abrir no navegador**. A torre e a caixa de briga devem aparecer. Se for usar, adicione no OBS como Fonte de navegador (1920×1080).

**No LMU (treino livre com IA)**
5. Geral → Fonte de dados: **Le Mans Ultimate**. Na pista, teste `Ctrl+Shift+H` e `Ctrl+Shift+L` com o jogo em foco.
6. Confira se o volante gira para o lado certo e se o gráfico acompanha os pedais. Nos **Rivais**, veja se pneu e VE dos outros carros aparecem (offline com IA deve aparecer; online pode vir "–").
7. Faça 3 voltas, pare no box para abastecer e faça mais 2. Depois, **Abrir voltas gravadas**: o tempo de cada volta deve bater com o do jogo, e depois do abastecimento o `stint` vira 2.
8. Com o HUD aberto, confira torre, nomes das equipes e intervalo para o carro da frente.
9. Ligue **Layout separado por classe**, entre com um carro de outra classe, arrume diferente, e volte ao primeiro carro.

**Modo narrador (assistindo)**
10. Transmissão → **Modo narrador** ligado. Saia do carro e assista a corrida como espectador: widgets e HUD devem seguir a briga mais apertada. Teste também **Líder** e **Carro pelo número**.

Deu problema? Abra uma issue com o `dmt-overlay.log` (Geral → Abrir pasta de configuração).

### Novidades

- Atalhos globais: `Ctrl+Shift+H` esconde/mostra os overlays e `Ctrl+Shift+L` trava/destrava, com o jogo em foco. Configuráveis em **Configurações → Atalhos**.
- Gravação das voltas em CSV (uma linha por volta, um arquivo por sessão) com tempo, stint, consumo, pneus e condições, para análise pós-corrida.
- Janela de configurações: opções gerais, aparência, atalhos e uma página por widget, sem editar o `config.json`.
- Layout separado por classe: posições e widgets ligados de cada classe, trocando sozinho ao mudar de carro (desligado por padrão).
- Tema Transmissão, com visual de TV: azul-marinho, fonte condensada, sobrenomes em caixa alta e faixa da classe.
- Widget **Volante e inputs** (desligado por padrão): volante que gira com a marcha no centro, anel de RPM e gráfico do acelerador e freio nos últimos segundos, com ABS e TC em amarelo.
- Widget **Rivais: pneus e VE** (desligado por padrão): desgaste do pneu e energia virtual do topo da sua classe (5 no Hypercar, 3 no LMP2 e no LMGT3, ajustável) e você junto.
- **Modo narrador** (Transmissão → Modo narrador): assistindo como espectador, widgets e HUD seguem a briga mais apertada, o líder ou um carro pelo número.
- HUD de transmissão para OBS: torre de classificação por classe e caixa de briga com o carro da frente, servida pelo próprio app (Configurações → Transmissão).

### Mudanças

- O menu da bandeja ficou só com o que se usa durante a sessão; o resto foi para **Configurações…**.

## [0.2.0] - 2026-11-09

Versão estável da 0.2.0, testada em pista a partir da beta.

### Novidades

- Widget de track limits com barra até a punição.
- Alerta multiclasse: carro mais rápido chegando e tráfego mais lento à frente.
- Widget de stint e estratégia: janela de box, paradas restantes e quanto abastecer.
- Radar de proximidade com alerta de carro lado a lado.
- Aviso na bandeja quando sai versão nova (pode ser desligado no menu).

## [0.2.0-beta.1] - 2026-10-30

Versão de teste. Confira principalmente o lado do radar (esquerda/direita) e a janela de box em corrida longa.

### Novidades

- Widget de track limits com barra até a punição.
- Alerta multiclasse: carro mais rápido chegando e tráfego mais lento à frente.
- Widget de stint e estratégia: janela de box, paradas restantes e quanto abastecer.
- Radar de proximidade com alerta de carro lado a lado.
- Aviso na bandeja quando sai versão nova (pode ser desligado no menu).

## [0.1.0] - 2026-10-30

### Novidades

- Leitura direta da memória compartilhada nativa do LMU, sem plugin.
- Widgets: relativo, classificação por classe, delta, marcha e RPM, pedais, combustível e energia virtual, pneus e freios, sessão e eletrônica.
- Menu na bandeja: travar/destravar, ligar/desligar widgets, tamanho, opacidade, esconder fora da pista.
- Modo demonstração para posicionar os widgets sem o jogo aberto.
- Configuração salva em `%APPDATA%\DMT Overlay`.

[Não lançado]: https://github.com/Vinii225/dmt-overlay/compare/v0.3.0-beta.2...HEAD
[0.3.0-beta.2]: https://github.com/Vinii225/dmt-overlay/compare/v0.2.0...v0.3.0-beta.2
[0.2.0]: https://github.com/Vinii225/dmt-overlay/compare/v0.1.0...v0.2.0
[0.2.0-beta.1]: https://github.com/Vinii225/dmt-overlay/compare/v0.1.0...v0.2.0-beta.1
[0.1.0]: https://github.com/Vinii225/dmt-overlay/releases/tag/v0.1.0
