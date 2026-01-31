"""
Janela de Configurações do Sistema
Interface para personalizar o Guardião Escolar
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QMessageBox,
    QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from core.config import get_config


class ConfigWindow(QDialog):
    """Janela de configurações do sistema"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self._setup_ui()
        self._carregar_valores()

    def _setup_ui(self):
        """Configura a interface gráfica"""
        self.setWindowTitle("Configurações do Sistema")
        self.setMinimumSize(550, 500)
        self.setStyleSheet(self._get_stylesheet())

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        titulo = QLabel("CONFIGURAÇÕES")
        titulo.setObjectName("titulo")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)

        # Abas
        tabs = QTabWidget()
        tabs.setObjectName("tabs")

        # ==================== ABA ESCOLA ====================
        tab_escola = QWidget()
        escola_layout = QVBoxLayout(tab_escola)

        escola_group = QGroupBox("Dados da Instituição")
        escola_form = QGridLayout(escola_group)
        escola_form.setSpacing(15)

        # Nome da escola
        escola_form.addWidget(QLabel("Nome da Escola:"), 0, 0)
        self.input_nome_escola = QLineEdit()
        self.input_nome_escola.setPlaceholderText("Ex: Escola Municipal João da Silva")
        escola_form.addWidget(self.input_nome_escola, 0, 1)

        # Cidade
        escola_form.addWidget(QLabel("Cidade:"), 1, 0)
        self.input_cidade = QLineEdit()
        self.input_cidade.setPlaceholderText("Ex: São Paulo")
        escola_form.addWidget(self.input_cidade, 1, 1)

        # Estado
        escola_form.addWidget(QLabel("Estado (UF):"), 2, 0)
        self.input_estado = QComboBox()
        self.input_estado.addItems([
            "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO",
            "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI",
            "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"
        ])
        escola_form.addWidget(self.input_estado, 2, 1)

        escola_layout.addWidget(escola_group)
        escola_layout.addStretch()

        tabs.addTab(tab_escola, "Escola")

        # ==================== ABA RECONHECIMENTO ====================
        tab_reconhecimento = QWidget()
        rec_layout = QVBoxLayout(tab_reconhecimento)

        rec_group = QGroupBox("Configurações de Reconhecimento Facial")
        rec_form = QGridLayout(rec_group)
        rec_form.setSpacing(15)

        # Tolerância
        rec_form.addWidget(QLabel("Tolerância (0.1 - 1.0):"), 0, 0)
        self.input_tolerancia = QDoubleSpinBox()
        self.input_tolerancia.setRange(0.1, 1.0)
        self.input_tolerancia.setSingleStep(0.05)
        self.input_tolerancia.setDecimals(2)
        self.input_tolerancia.setToolTip(
            "Menor valor = mais rigoroso (menos falsos positivos)\n"
            "Maior valor = mais permissivo (mais reconhecimentos)"
        )
        rec_form.addWidget(self.input_tolerancia, 0, 1)

        # Ajuda sobre tolerância
        tolerancia_help = QLabel("Valor recomendado: 0.6")
        tolerancia_help.setObjectName("helpText")
        rec_form.addWidget(tolerancia_help, 1, 1)

        # Tempo entre registros
        rec_form.addWidget(QLabel("Intervalo mínimo (segundos):"), 2, 0)
        self.input_tempo_registros = QSpinBox()
        self.input_tempo_registros.setRange(10, 300)
        self.input_tempo_registros.setSingleStep(10)
        self.input_tempo_registros.setToolTip(
            "Tempo mínimo entre registros do mesmo aluno\n"
            "para evitar registros duplicados"
        )
        rec_form.addWidget(self.input_tempo_registros, 2, 1)

        rec_layout.addWidget(rec_group)
        rec_layout.addStretch()

        tabs.addTab(tab_reconhecimento, "Reconhecimento")

        # ==================== ABA SOBRE ====================
        tab_sobre = QWidget()
        sobre_layout = QVBoxLayout(tab_sobre)

        # Logo/Nome do sistema
        sistema_frame = QFrame()
        sistema_frame.setObjectName("sobreFrame")
        sistema_vlayout = QVBoxLayout(sistema_frame)

        nome_sistema = QLabel("GUARDIÃO ESCOLAR")
        nome_sistema.setObjectName("sistemaNome")
        nome_sistema.setAlignment(Qt.AlignCenter)
        sistema_vlayout.addWidget(nome_sistema)

        desc_sistema = QLabel("Sistema de Controle de Acesso Escolar\ncom Reconhecimento Facial")
        desc_sistema.setObjectName("sistemaDesc")
        desc_sistema.setAlignment(Qt.AlignCenter)
        sistema_vlayout.addWidget(desc_sistema)

        versao = QLabel(f"Versão {self.config.config.versao}")
        versao.setObjectName("versaoLabel")
        versao.setAlignment(Qt.AlignCenter)
        sistema_vlayout.addWidget(versao)

        sobre_layout.addWidget(sistema_frame)

        # Desenvolvedor
        dev_frame = QFrame()
        dev_frame.setObjectName("devFrame")
        dev_vlayout = QVBoxLayout(dev_frame)

        dev_titulo = QLabel("DESENVOLVIDO POR")
        dev_titulo.setObjectName("devTitulo")
        dev_titulo.setAlignment(Qt.AlignCenter)
        dev_vlayout.addWidget(dev_titulo)

        dev_empresa = QLabel(self.config.config.desenvolvedor)
        dev_empresa.setObjectName("devEmpresa")
        dev_empresa.setAlignment(Qt.AlignCenter)
        dev_vlayout.addWidget(dev_empresa)

        dev_responsavel = QLabel(self.config.config.desenvolvedor_responsavel)
        dev_responsavel.setObjectName("devResponsavel")
        dev_responsavel.setAlignment(Qt.AlignCenter)
        dev_vlayout.addWidget(dev_responsavel)

        sobre_layout.addWidget(dev_frame)
        sobre_layout.addStretch()

        # Nota de rodapé
        rodape = QLabel("Software de cunho social para segurança escolar")
        rodape.setObjectName("rodape")
        rodape.setAlignment(Qt.AlignCenter)
        sobre_layout.addWidget(rodape)

        tabs.addTab(tab_sobre, "Sobre")

        main_layout.addWidget(tabs)

        # ==================== BOTÕES ====================
        botoes_layout = QHBoxLayout()

        btn_cancelar = QPushButton("CANCELAR")
        btn_cancelar.setObjectName("btnCancelar")
        btn_cancelar.clicked.connect(self.reject)
        botoes_layout.addWidget(btn_cancelar)

        botoes_layout.addStretch()

        btn_salvar = QPushButton("SALVAR CONFIGURAÇÕES")
        btn_salvar.setObjectName("btnSalvar")
        btn_salvar.clicked.connect(self._salvar)
        botoes_layout.addWidget(btn_salvar)

        main_layout.addLayout(botoes_layout)

    def _carregar_valores(self):
        """Carrega os valores atuais das configurações"""
        cfg = self.config.config

        self.input_nome_escola.setText(cfg.nome_escola)
        self.input_cidade.setText(cfg.cidade)

        # Seleciona o estado correto
        index = self.input_estado.findText(cfg.estado)
        if index >= 0:
            self.input_estado.setCurrentIndex(index)

        self.input_tolerancia.setValue(cfg.tolerancia_reconhecimento)
        self.input_tempo_registros.setValue(cfg.tempo_entre_registros)

    def _salvar(self):
        """Salva as configurações"""
        # Valida campos obrigatórios
        nome_escola = self.input_nome_escola.text().strip()
        cidade = self.input_cidade.text().strip()

        if not nome_escola:
            QMessageBox.warning(self, "Aviso", "Digite o nome da escola")
            self.input_nome_escola.setFocus()
            return

        if not cidade:
            QMessageBox.warning(self, "Aviso", "Digite a cidade")
            self.input_cidade.setFocus()
            return

        # Atualiza configurações
        self.config.set("nome_escola", nome_escola)
        self.config.set("cidade", cidade)
        self.config.set("estado", self.input_estado.currentText())
        self.config.set("tolerancia_reconhecimento", self.input_tolerancia.value())
        self.config.set("tempo_entre_registros", self.input_tempo_registros.value())

        # Salva no arquivo
        if self.config.salvar():
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", "Erro ao salvar configurações")

    def _get_stylesheet(self):
        """Retorna o stylesheet da janela"""
        return """
            QDialog {
                background-color: #1a1a2e;
            }

            QLabel#titulo {
                color: #e94560;
                font-size: 22px;
                font-weight: bold;
                padding: 10px;
            }

            QTabWidget::pane {
                border: 1px solid #3a3a5c;
                border-radius: 8px;
                background-color: #16213e;
            }

            QTabBar::tab {
                background-color: #0f0f1a;
                color: #a0a0a0;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }

            QTabBar::tab:selected {
                background-color: #16213e;
                color: #e94560;
                font-weight: bold;
            }

            QTabBar::tab:hover {
                background-color: #1a1a2e;
            }

            QGroupBox {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #3a3a5c;
                border-radius: 8px;
                margin-top: 15px;
                padding: 20px;
                padding-top: 25px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }

            QLabel {
                color: #ffffff;
                font-size: 14px;
            }

            QLabel#helpText {
                color: #a0a0a0;
                font-size: 12px;
                font-style: italic;
            }

            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                background-color: #0f0f1a;
                color: white;
                border: 1px solid #3a3a5c;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-width: 250px;
            }

            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                border-color: #e94560;
            }

            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }

            QComboBox QAbstractItemView {
                background-color: #16213e;
                color: white;
                selection-background-color: #e94560;
            }

            QFrame#sobreFrame {
                background-color: #0f0f1a;
                border: 2px solid #e94560;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }

            QLabel#sistemaNome {
                color: #e94560;
                font-size: 26px;
                font-weight: bold;
            }

            QLabel#sistemaDesc {
                color: #a0a0a0;
                font-size: 14px;
                padding: 10px;
            }

            QLabel#versaoLabel {
                color: #27ae60;
                font-size: 12px;
            }

            QFrame#devFrame {
                background-color: #16213e;
                border: 1px solid #3a3a5c;
                border-radius: 10px;
                padding: 20px;
                margin: 10px;
            }

            QLabel#devTitulo {
                color: #a0a0a0;
                font-size: 12px;
                padding-bottom: 5px;
            }

            QLabel#devEmpresa {
                color: #3498db;
                font-size: 18px;
                font-weight: bold;
            }

            QLabel#devResponsavel {
                color: #f39c12;
                font-size: 16px;
            }

            QLabel#rodape {
                color: #666666;
                font-size: 11px;
                font-style: italic;
                padding: 10px;
            }

            QPushButton#btnSalvar {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }

            QPushButton#btnSalvar:hover {
                background-color: #2ecc71;
            }

            QPushButton#btnCancelar {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }

            QPushButton#btnCancelar:hover {
                background-color: #ec7063;
            }
        """
