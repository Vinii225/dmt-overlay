# Changelog

Todas as mudanças relevantes do projeto. O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/) e o projeto usa [versionamento semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Novidades

- Atalhos globais: `Ctrl+Shift+H` esconde/mostra os overlays e `Ctrl+Shift+L` trava/destrava, com o jogo em foco. Configuráveis em **Configurações → Atalhos**.
- Gravação das voltas em CSV (uma linha por volta, um arquivo por sessão) com tempo, stint, consumo, pneus e condições, para análise pós-corrida.
- Janela de configurações: opções gerais, aparência, atalhos e uma página por widget, sem editar o `config.json`.
- Layout separado por classe: posições e widgets ligados de cada classe, trocando sozinho ao mudar de carro (desligado por padrão).

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

[Não lançado]: https://github.com/Vinii225/dmt-overlay/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/Vinii225/dmt-overlay/compare/v0.1.0...v0.2.0
[0.2.0-beta.1]: https://github.com/Vinii225/dmt-overlay/compare/v0.1.0...v0.2.0-beta.1
[0.1.0]: https://github.com/Vinii225/dmt-overlay/releases/tag/v0.1.0
