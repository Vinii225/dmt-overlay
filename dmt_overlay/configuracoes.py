from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QKeySequenceEdit,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSlider,
    QSpinBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from . import __version__
from .atalhos import interpretar
from .bandeja import abrir_pasta
from .config import pasta_config, pasta_voltas
from .icone import icone
from .widgets.base import Opcao, WidgetOverlay

if TYPE_CHECKING:
    from .app import Aplicativo

FONTES = (("lmu", "Le Mans Ultimate"), ("demo", "Demonstração"))
ATALHOS = (("mostrar_ocultar", "Esconder / mostrar overlays"), ("travar", "Travar / destravar posições"))

RECURSOS = (Path(__file__).parent / "recursos").as_posix()

ESTILO = """
QWidget { background: #141416; color: #f0efec; font-family: "Segoe UI", "Inter", "Noto Sans", sans-serif; font-size: 13px; }
QListWidget { background: #1b1b1e; border: none; border-right: 1px solid #2a2a2d; padding: 8px 0; outline: 0; }
QListWidget::item { padding: 7px 16px; border-left: 3px solid transparent; }
QListWidget::item:selected { background: #232327; color: #ffffff; border-left: 3px solid #2fbf71; }
QListWidget::item:hover:!selected { background: #1f1f23; }
QListWidget::item:disabled { color: #898781; font-size: 11px; font-weight: 600; padding-top: 14px; }
QScrollArea { border: none; }
QLabel#titulo { font-size: 20px; font-weight: 600; }
QLabel#descricao, QLabel#ajuda { color: #a9a8a0; }
QLabel#ajuda { font-size: 12px; }
QLabel#secao { color: #898781; font-size: 11px; font-weight: 600; letter-spacing: 1px; padding-top: 12px; }
QLabel#aviso { background: #1f2a22; border: 1px solid #2c4a35; border-radius: 6px; padding: 8px 10px; color: #c9e9d4; }
QLabel#erro { color: #ec835a; font-size: 12px; }
QLabel#ok { color: #2fbf71; font-size: 12px; }
QLabel#rodape { color: #6f6e69; font-size: 11px; }
QFrame#linha { background: #2a2a2d; max-height: 1px; border: none; }
QPushButton { background: #26262a; border: 1px solid #34343a; border-radius: 6px; padding: 6px 14px; }
QPushButton:hover { background: #2e2e33; }
QPushButton:pressed { background: #222226; }
QPushButton#primario { background: #2fbf71; border-color: #2fbf71; color: #0d1f14; font-weight: 600; }
QPushButton#primario:hover { background: #38cf7d; }
QComboBox, QSpinBox, QDoubleSpinBox, QKeySequenceEdit, QLineEdit {
    background: #1e1e22; border: 1px solid #34343a; border-radius: 6px; padding: 5px 8px; min-height: 18px;
}
QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QLineEdit:focus { border-color: #2fbf71; }
QComboBox QAbstractItemView { background: #1e1e22; selection-background-color: #2a3a30; border: 1px solid #34343a; }
QCheckBox { spacing: 8px; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #4a4a50; background: #1e1e22; }
QCheckBox::indicator:checked { background: #2fbf71; border-color: #2fbf71; image: url(@/marcado.svg); }
QCheckBox::indicator:hover { border-color: #2fbf71; }
QSpinBox, QDoubleSpinBox { padding-right: 22px; }
QSpinBox::up-button, QDoubleSpinBox::up-button, QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border; width: 20px; border: none; border-left: 1px solid #34343a; background: #232327;
}
QSpinBox::up-button, QDoubleSpinBox::up-button { subcontrol-position: top right; border-top-right-radius: 6px; }
QSpinBox::down-button, QDoubleSpinBox::down-button { subcontrol-position: bottom right; border-bottom-right-radius: 6px; }
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover, QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background: #2e2e33;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow { image: url(@/seta-cima.svg); width: 10px; height: 6px; }
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow { image: url(@/seta-baixo.svg); width: 10px; height: 6px; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox::down-arrow { image: url(@/seta-baixo.svg); width: 10px; height: 6px; }
QScrollBar:vertical { background: transparent; width: 10px; margin: 2px; }
QScrollBar::handle:vertical { background: #3a3a40; border-radius: 3px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #4a4a50; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical, QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    height: 0; background: none;
}
QSlider::groove:horizontal { height: 4px; background: #2c2c2a; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #2fbf71; border-radius: 2px; }
QSlider::handle:horizontal { background: #f0efec; width: 14px; height: 14px; margin: -5px 0; border-radius: 7px; }
"""


def _rotulo(texto: str, nome: str = "") -> QLabel:
    rotulo = QLabel(texto)
    rotulo.setWordWrap(True)
    if nome:
        rotulo.setObjectName(nome)
    return rotulo


def _linha() -> QFrame:
    linha = QFrame()
    linha.setObjectName("linha")
    linha.setFrameShape(QFrame.Shape.HLine)
    return linha


class _Pagina(QScrollArea):
    def __init__(self, titulo: str, descricao: str = "") -> None:
        super().__init__()
        self.setWidgetResizable(True)
        conteudo = QWidget()
        self.layout_ = QVBoxLayout(conteudo)
        self.layout_.setContentsMargins(28, 24, 28, 24)
        self.layout_.setSpacing(10)
        self.layout_.addWidget(_rotulo(titulo, "titulo"))
        if descricao:
            self.layout_.addWidget(_rotulo(descricao, "descricao"))
        self.setWidget(conteudo)
        self._grade: QGridLayout | None = None

    def secao(self, nome: str) -> None:
        self.layout_.addWidget(_rotulo(nome.upper(), "secao"))
        self.layout_.addWidget(_linha())
        self._grade = None

    def campo(self, rotulo: str, controle: QWidget, ajuda: str = "") -> QLabel | None:
        """Rótulo à esquerda, controle à direita e a ajuda logo abaixo do rótulo."""
        if self._grade is None:
            self._grade = QGridLayout()
            self._grade.setHorizontalSpacing(24)
            self._grade.setVerticalSpacing(4)
            self._grade.setColumnStretch(0, 1)
            self.layout_.addLayout(self._grade)
        linha = self._grade.rowCount()
        self._grade.addWidget(_rotulo(rotulo), linha, 0)
        self._grade.addWidget(controle, linha, 1, 2 if ajuda else 1, 1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        texto_ajuda = None
        if ajuda:
            texto_ajuda = _rotulo(ajuda, "ajuda")
            self._grade.addWidget(texto_ajuda, linha + 1, 0)
        self._grade.setRowMinimumHeight(self._grade.rowCount(), 8)
        return texto_ajuda

    def adicionar(self, widget: QWidget) -> None:
        self.layout_.addWidget(widget)
        self._grade = None

    def fim(self) -> None:
        self.layout_.addStretch(1)


def _botoes(*botoes: QPushButton) -> QWidget:
    caixa = QWidget()
    linha = QHBoxLayout(caixa)
    linha.setContentsMargins(0, 4, 0, 0)
    for botao in botoes:
        linha.addWidget(botao)
    linha.addStretch(1)
    return caixa


class JanelaConfiguracoes(QWidget):
    def __init__(self, aplicativo: Aplicativo) -> None:
        super().__init__(None, Qt.WindowType.Window)
        self.app = aplicativo
        self._recarregar: list[Callable[[], None]] = []
        self.setWindowTitle("DMT Overlay - Configurações")
        self.setWindowIcon(icone())
        self.setStyleSheet(ESTILO.replace("@/", RECURSOS + "/"))
        self.resize(780, 680)
        self.setMinimumSize(620, 440)

        self.navegacao = QListWidget()
        self.navegacao.setFixedWidth(200)
        self.paginas = QStackedWidget()
        self.navegacao.currentRowChanged.connect(self._trocar_pagina)
        self._indices: list[int] = []

        corpo = QHBoxLayout(self)
        corpo.setContentsMargins(0, 0, 0, 0)
        corpo.setSpacing(0)
        corpo.addWidget(self.navegacao)
        direita = QVBoxLayout()
        direita.setContentsMargins(0, 0, 0, 0)
        direita.addWidget(self.paginas, 1)
        rodape = _rotulo(f"As mudanças valem na hora e são salvas sozinhas.  ·  DMT Overlay {__version__}", "rodape")
        rodape.setContentsMargins(28, 6, 28, 10)
        direita.addWidget(rodape)
        corpo.addLayout(direita, 1)

        self._adicionar("Geral", self._pagina_geral())
        self._adicionar("Aparência", self._pagina_aparencia())
        self._adicionar("Atalhos", self._pagina_atalhos())
        self._cabecalho("Widgets")
        for widget in self.app.widgets.values():
            self._adicionar(widget.titulo, self._pagina_widget(widget))
        self.navegacao.setCurrentRow(0)
        self.app.ao_mudar(self.recarregar)
        self.recarregar()

    # Navegação

    def _adicionar(self, nome: str, pagina: QWidget) -> None:
        self.navegacao.addItem(nome)
        self._indices.append(self.paginas.addWidget(pagina))

    def _cabecalho(self, nome: str) -> None:
        item = QListWidgetItem(nome.upper())
        item.setFlags(Qt.ItemFlag.NoItemFlags)
        self.navegacao.addItem(item)
        self._indices.append(-1)

    def _trocar_pagina(self, linha: int) -> None:
        if 0 <= linha < len(self._indices) and self._indices[linha] >= 0:
            self.paginas.setCurrentIndex(self._indices[linha])

    def mostrar_pagina(self, nome: str) -> None:
        for i in range(self.navegacao.count()):
            if self.navegacao.item(i).text() == nome:
                self.navegacao.setCurrentRow(i)
                return

    def recarregar(self) -> None:
        """Lê de novo a configuração (algo pode ter mudado pela bandeja ou por atalho)."""
        for recarregar in self._recarregar:
            recarregar()

    def _ligar(self, controle: QWidget, ler: Callable[[], Any], escrever: Callable[[QWidget, Any], None]) -> None:
        def recarregar() -> None:
            controle.blockSignals(True)
            escrever(controle, ler())
            controle.blockSignals(False)

        self._recarregar.append(recarregar)

    def _caixa(self, ler: Callable[[], bool], ao_mudar: Callable[[bool], None], texto: str = "") -> QCheckBox:
        caixa = QCheckBox(texto)
        caixa.toggled.connect(ao_mudar)
        self._ligar(caixa, ler, lambda c, v: c.setChecked(bool(v)))
        return caixa

    # Páginas

    def _pagina_geral(self) -> QWidget:
        app, geral = self.app, self.app.config.geral
        pagina = _Pagina("Geral")

        pagina.secao("Posição na tela")
        travar = QPushButton()
        travar.setObjectName("primario")
        travar.setMinimumWidth(200)
        travar.clicked.connect(lambda: app.bandeja.acao_travar.toggle())
        texto_travar = lambda b, v: b.setText("Destravar para posicionar" if v else "Travar posições")  # noqa: E731
        self._ligar(travar, lambda: geral["travado"], texto_travar)
        restaurar = QPushButton("Restaurar posições")
        restaurar.clicked.connect(app.restaurar_posicoes)
        pagina.adicionar(_botoes(travar, restaurar))
        pagina.adicionar(
            _rotulo("Destravado, arraste os widgets (eles encaixam nas bordas). Trave para o clique voltar ao jogo.", "ajuda")
        )
        explicacao = "Guarda posições e widgets ligados de cada classe (Hypercar, LMP2, GT3…) e troca sozinho ao mudar de carro."
        ajuda_classe = pagina.campo(
            "Layout separado por classe",
            self._caixa(lambda: geral["layout_por_classe"], app.definir_layout_por_classe),
            explicacao,
        )
        texto_classe = lambda r, v: r.setText(f"{explicacao}\nClasse atual: {v or 'nenhum carro na pista ainda'}.")  # noqa: E731
        self._ligar(ajuda_classe, lambda: app.nome_classe, texto_classe)
        pagina.campo(
            "Esconder fora da pista",
            self._caixa(lambda: geral["ocultar_fora_da_pista"], app.definir_ocultar),
            "Some com os overlays no menu e na garagem.",
        )

        pagina.secao("Dados")
        fonte = QComboBox()
        for chave, nome in FONTES:
            fonte.addItem(nome, chave)
        fonte.currentIndexChanged.connect(lambda i: app.trocar_fonte(fonte.itemData(i)))
        self._ligar(fonte, lambda: app.provedor.fonte, lambda c, v: c.setCurrentIndex(max(0, c.findData(v))))
        pagina.campo("Fonte de dados", fonte, "Demonstração usa dados simulados para posicionar tudo sem abrir o jogo.")
        taxa = QSpinBox()
        taxa.setRange(10, 60)
        taxa.setSingleStep(5)
        taxa.setSuffix(" Hz")
        taxa.setKeyboardTracking(False)
        taxa.valueChanged.connect(app.definir_taxa)
        self._ligar(taxa, lambda: geral["taxa_atualizacao"], lambda c, v: c.setValue(int(v)))
        pagina.campo("Atualização", taxa, "Mais alto deixa RPM e pedais mais suaves e usa mais CPU.")

        pagina.secao("Voltas gravadas")
        pagina.campo(
            "Gravar voltas em CSV",
            self._caixa(lambda: geral["gravar_voltas"], app.definir_gravar_voltas),
            "Uma linha por volta com tempo, stint, consumo e pneus, para analisar depois da corrida.",
        )
        abrir_voltas = QPushButton("Abrir pasta das voltas")
        abrir_voltas.clicked.connect(lambda: abrir_pasta(pasta_voltas()))
        pagina.adicionar(_botoes(abrir_voltas))

        pagina.secao("Sobre")
        pagina.campo(
            "Avisar sobre atualizações",
            self._caixa(lambda: geral["verificar_atualizacoes"], app.definir_verificar_atualizacoes),
            "Ao abrir, confere se saiu versão nova.",
        )
        abrir_config = QPushButton("Abrir pasta de configuração")
        abrir_config.clicked.connect(lambda: abrir_pasta(pasta_config()))
        pagina.adicionar(_botoes(abrir_config))
        pagina.fim()
        return pagina

    def _pagina_aparencia(self) -> QWidget:
        app, geral = self.app, self.app.config.geral
        pagina = _Pagina("Aparência", "Vale para todos os widgets.")
        pagina.secao("Widgets")
        tamanho = self._slider(80, 150, 5, lambda: geral["escala"], app.definir_escala)
        pagina.campo("Tamanho", tamanho, "Para telas grandes ou triplas.")
        pagina.campo("Opacidade", self._slider(40, 100, 5, lambda: geral["opacidade"], app.definir_opacidade))
        pagina.fim()
        return pagina

    def _slider(
        self, minimo: int, maximo: int, passo: int, ler: Callable[[], float], aplicar: Callable[[float], None]
    ) -> QWidget:
        caixa = QWidget()
        linha = QHBoxLayout(caixa)
        linha.setContentsMargins(0, 0, 0, 0)
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(minimo // passo, maximo // passo)
        slider.setFixedWidth(200)
        # Aplica ao soltar (ou por teclado); arrastando só atualiza o número.
        slider.setTracking(False)
        valor = QLabel()
        valor.setFixedWidth(44)
        valor.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        slider.sliderMoved.connect(lambda v: valor.setText(f"{v * passo}%"))

        def soltar(v: int) -> None:
            valor.setText(f"{v * passo}%")
            aplicar(v * passo / 100)

        slider.valueChanged.connect(soltar)
        linha.addWidget(slider)
        linha.addWidget(valor)

        def escrever(s: QSlider, v: float) -> None:
            s.setValue(round(v * 100 / passo))
            valor.setText(f"{round(v * 100)}%")

        self._ligar(slider, ler, escrever)
        return caixa

    def _pagina_atalhos(self) -> QWidget:
        app = self.app
        pagina = _Pagina("Atalhos", "Funcionam com o jogo em foco. Use Ctrl, Shift, Alt ou Win com uma letra, número ou tecla F.")
        if not app.atalhos.suportado:
            pagina.adicionar(_rotulo("Atalhos globais só funcionam no Windows.", "aviso"))
        pagina.secao("Teclado")
        for nome, rotulo in ATALHOS:
            pagina.campo(rotulo, self._editor_atalho(nome))
        pagina.fim()
        return pagina

    def _editor_atalho(self, nome: str) -> QWidget:
        app = self.app
        caixa = QWidget()
        coluna = QVBoxLayout(caixa)
        coluna.setContentsMargins(0, 0, 0, 0)
        coluna.setSpacing(2)
        linha = QHBoxLayout()
        editor = QKeySequenceEdit()
        editor.setMaximumSequenceLength(1)
        editor.setFixedWidth(170)
        limpar = QPushButton("Limpar")
        linha.addWidget(editor)
        linha.addWidget(limpar)
        estado = _rotulo("", "ajuda")
        estado.setAlignment(Qt.AlignmentFlag.AlignRight)
        estado.hide()
        coluna.addLayout(linha)
        coluna.addWidget(estado)

        def mostrar(texto: str, tipo: str) -> None:
            estado.setObjectName(tipo)
            estado.setText(texto)
            estado.setVisible(bool(texto))
            estado.style().unpolish(estado)
            estado.style().polish(estado)

        def salvar() -> None:
            texto = editor.keySequence().toString(QKeySequence.SequenceFormat.PortableText)
            anterior = app.config.geral["atalhos"].get(nome, "")
            if texto and interpretar(texto) is None:
                mostrar("Combinação inválida: use Ctrl, Shift, Alt ou Win + tecla.", "erro")
                editor.setKeySequence(QKeySequence(anterior))
                return
            normalizado = interpretar(texto)[2] if texto else ""
            if normalizado == anterior:
                return
            if app.definir_atalho(nome, normalizado):
                mostrar("Salvo." if normalizado else "Desligado.", "ok")
            else:
                mostrar("Outro programa já usa essa combinação.", "erro")

        editor.editingFinished.connect(salvar)
        limpar.clicked.connect(lambda: (editor.clear(), salvar()))

        def escrever(e: QKeySequenceEdit, v: str) -> None:
            e.setKeySequence(QKeySequence(v or ""))
            if v and app.atalhos.suportado and nome not in app.atalhos.registrados:
                mostrar("Não registrado: outro programa usa essa combinação.", "erro")

        self._ligar(editor, lambda: app.config.geral["atalhos"].get(nome, ""), escrever)
        return caixa

    def _pagina_widget(self, widget: WidgetOverlay) -> QWidget:
        app, nome = self.app, widget.nome
        pagina = _Pagina(widget.titulo, widget.descricao)
        pagina.secao("Exibição")
        pagina.campo("Mostrar este widget", self._caixa(lambda: widget.config["ativo"], lambda v: app.alternar_widget(nome, v)))
        opcoes = type(widget).opcoes
        if opcoes:
            pagina.secao("Opções")
            for chave, opcao in opcoes.items():
                pagina.campo(opcao.rotulo, self._controle_opcao(widget, chave, opcao), opcao.ajuda)
            restaurar = QPushButton("Restaurar padrão")
            restaurar.clicked.connect(lambda: app.restaurar_opcoes(nome))
            pagina.adicionar(_botoes(restaurar))
        dica = _rotulo("Para ver as mudanças sem o jogo, use Geral → Fonte de dados → Demonstração e destrave.", "ajuda")
        dica.setContentsMargins(0, 16, 0, 0)
        pagina.adicionar(dica)
        pagina.fim()
        return pagina

    def _controle_opcao(self, widget: WidgetOverlay, chave: str, opcao: Opcao) -> QWidget:
        app, nome = self.app, widget.nome
        padrao = type(widget).opcoes_padrao[chave]
        ler = lambda: widget.config[chave]  # noqa: E731

        if isinstance(padrao, bool):
            return self._caixa(ler, lambda v: app.definir_opcao(nome, chave, v))

        if opcao.escolhas:
            combo = QComboBox()
            for valor, texto in opcao.escolhas:
                combo.addItem(texto, valor)
            combo.currentIndexChanged.connect(lambda i: app.definir_opcao(nome, chave, combo.itemData(i)))
            self._ligar(combo, ler, lambda c, v: c.setCurrentIndex(max(0, c.findData(v))))
            return combo

        inteiro = isinstance(padrao, int) and float(opcao.passo).is_integer() and opcao.fator == 1
        spin: QAbstractSpinBox = QSpinBox() if inteiro else QDoubleSpinBox()
        if not inteiro:
            casas = 0 if float(opcao.passo).is_integer() else 1
            spin.setDecimals(casas)
        if inteiro:
            spin.setRange(int(opcao.minimo), int(opcao.maximo))
            spin.setSingleStep(int(opcao.passo))
        else:
            spin.setRange(opcao.minimo, opcao.maximo)
            spin.setSingleStep(opcao.passo)
        spin.setSuffix(opcao.sufixo)
        spin.setKeyboardTracking(False)
        spin.setFixedWidth(130)

        def aplicar(valor: float) -> None:
            salvo = valor / opcao.fator
            app.definir_opcao(nome, chave, int(salvo) if isinstance(padrao, int) else round(salvo, 4))

        spin.valueChanged.connect(aplicar)
        self._ligar(spin, ler, lambda s, v: s.setValue(v * opcao.fator))
        return spin

    def closeEvent(self, evento) -> None:
        # Só esconde: a janela é reaproveitada na próxima vez.
        evento.ignore()
        self.hide()

