"""
Janela Principal do Sistema Guardião Escolar
Interface principal com preview da câmera e controles de acesso
"""

import cv2
import os
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QMessageBox,
    QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

from database.models import Database, Registro
from core.facial_recognition import FacialRecognition, ResultadoReconhecimento
from core.camera_handler import CameraHandler
from core.config import get_config
from .cadastro_window import CadastroWindow
from .registros_window import RegistrosWindow
from .config_window import ConfigWindow


class MainWindow(QMainWindow):
    """Janela principal do sistema de controle de acesso"""

    # Sinal emitido quando um aluno é reconhecido
    aluno_reconhecido = pyqtSignal(int, str, float)

    def __init__(self):
        super().__init__()

        # Carrega configurações
        self.config = get_config()

        # Inicializa componentes do sistema
        self.db = Database()
        self.facial_recognition = FacialRecognition(
            tolerance=self.config.config.tolerancia_reconhecimento
        )
        self.camera = CameraHandler()

        # Estado do sistema
        self.modo_atual = "entrada"  # entrada ou saida
        self.ultimo_reconhecimento = None
        self.tempo_feedback = 0  # Contador para exibir feedback
        self.reconhecimento_ativo = True
        self.frame_contador = 0  # Para processar a cada N frames

        # Configura interface
        self._setup_ui()
        self._setup_timers()
        self._iniciar_camera()

        # Atualiza contadores
        self._atualizar_contadores()

    def _setup_ui(self):
        """Configura a interface gráfica"""
        self.setWindowTitle(f"Guardião Escolar - {self.config.config.nome_escola}")
        self.setMinimumSize(1200, 700)
        self.setStyleSheet(self._get_stylesheet())

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal horizontal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ==================== PAINEL ESQUERDO (Câmera) ====================
        left_panel = QFrame()
        left_panel.setObjectName("cameraPanel")
        left_layout = QVBoxLayout(left_panel)

        # Título
        titulo_camera = QLabel("MONITORAMENTO")
        titulo_camera.setObjectName("sectionTitle")
        titulo_camera.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(titulo_camera)

        # Preview da câmera
        self.camera_label = QLabel()
        self.camera_label.setObjectName("cameraPreview")
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setText("Iniciando câmera...")
        left_layout.addWidget(self.camera_label)

        # Status da câmera
        self.status_camera = QLabel("Status: Aguardando...")
        self.status_camera.setObjectName("statusLabel")
        self.status_camera.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.status_camera)

        main_layout.addWidget(left_panel, stretch=2)

        # ==================== PAINEL DIREITO (Controles) ====================
        right_panel = QFrame()
        right_panel.setObjectName("controlPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(15)

        # Logo/Título
        titulo = QLabel("GUARDIÃO ESCOLAR")
        titulo.setObjectName("mainTitle")
        titulo.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(titulo)

        subtitulo = QLabel("Sistema de Controle de Acesso")
        subtitulo.setObjectName("subtitle")
        subtitulo.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(subtitulo)

        # Nome da escola
        self.escola_label = QLabel(self.config.nome_completo_escola)
        self.escola_label.setObjectName("escolaLabel")
        self.escola_label.setAlignment(Qt.AlignCenter)
        self.escola_label.setWordWrap(True)
        right_layout.addWidget(self.escola_label)

        right_layout.addSpacing(10)

        # ==================== MODO ENTRADA/SAÍDA ====================
        modo_group = QGroupBox("MODO DE OPERAÇÃO")
        modo_group.setObjectName("groupBox")
        modo_layout = QVBoxLayout(modo_group)

        # Botões de modo
        modo_buttons_layout = QHBoxLayout()

        self.btn_entrada = QPushButton("ENTRADA")
        self.btn_entrada.setObjectName("modoEntrada")
        self.btn_entrada.setCheckable(True)
        self.btn_entrada.setChecked(True)
        self.btn_entrada.clicked.connect(lambda: self._set_modo("entrada"))
        modo_buttons_layout.addWidget(self.btn_entrada)

        self.btn_saida = QPushButton("SAÍDA")
        self.btn_saida.setObjectName("modoSaida")
        self.btn_saida.setCheckable(True)
        self.btn_saida.clicked.connect(lambda: self._set_modo("saida"))
        modo_buttons_layout.addWidget(self.btn_saida)

        modo_layout.addLayout(modo_buttons_layout)

        # Indicador de modo atual
        self.modo_label = QLabel("Registrando: ENTRADA")
        self.modo_label.setObjectName("modoIndicator")
        self.modo_label.setAlignment(Qt.AlignCenter)
        modo_layout.addWidget(self.modo_label)

        right_layout.addWidget(modo_group)

        # ==================== ÚLTIMO RECONHECIMENTO ====================
        reconhecimento_group = QGroupBox("ÚLTIMO RECONHECIMENTO")
        reconhecimento_group.setObjectName("groupBox")
        reconhecimento_layout = QVBoxLayout(reconhecimento_group)

        # Foto do aluno reconhecido
        self.foto_aluno = QLabel()
        self.foto_aluno.setObjectName("fotoAluno")
        self.foto_aluno.setFixedSize(150, 150)
        self.foto_aluno.setAlignment(Qt.AlignCenter)
        self.foto_aluno.setText("Aguardando...")
        reconhecimento_layout.addWidget(self.foto_aluno, alignment=Qt.AlignCenter)

        # Nome do aluno
        self.nome_aluno = QLabel("---")
        self.nome_aluno.setObjectName("nomeAluno")
        self.nome_aluno.setAlignment(Qt.AlignCenter)
        self.nome_aluno.setWordWrap(True)
        reconhecimento_layout.addWidget(self.nome_aluno)

        # Horário
        self.horario_label = QLabel("--:--:--")
        self.horario_label.setObjectName("horarioLabel")
        self.horario_label.setAlignment(Qt.AlignCenter)
        reconhecimento_layout.addWidget(self.horario_label)

        # Confiança
        self.confianca_label = QLabel("Confiança: ---%")
        self.confianca_label.setObjectName("confiancaLabel")
        self.confianca_label.setAlignment(Qt.AlignCenter)
        reconhecimento_layout.addWidget(self.confianca_label)

        right_layout.addWidget(reconhecimento_group)

        # ==================== CONTADORES ====================
        contadores_group = QGroupBox("REGISTROS DO DIA")
        contadores_group.setObjectName("groupBox")
        contadores_layout = QHBoxLayout(contadores_group)

        # Contador de entradas
        entrada_frame = QFrame()
        entrada_frame.setObjectName("contadorEntrada")
        entrada_layout = QVBoxLayout(entrada_frame)
        self.contador_entradas = QLabel("0")
        self.contador_entradas.setObjectName("contadorNumero")
        self.contador_entradas.setAlignment(Qt.AlignCenter)
        entrada_layout.addWidget(self.contador_entradas)
        entrada_layout.addWidget(QLabel("Entradas"), alignment=Qt.AlignCenter)
        contadores_layout.addWidget(entrada_frame)

        # Contador de saídas
        saida_frame = QFrame()
        saida_frame.setObjectName("contadorSaida")
        saida_layout = QVBoxLayout(saida_frame)
        self.contador_saidas = QLabel("0")
        self.contador_saidas.setObjectName("contadorNumero")
        self.contador_saidas.setAlignment(Qt.AlignCenter)
        saida_layout.addWidget(self.contador_saidas)
        saida_layout.addWidget(QLabel("Saídas"), alignment=Qt.AlignCenter)
        contadores_layout.addWidget(saida_frame)

        right_layout.addWidget(contadores_group)

        # ==================== BOTÕES DE AÇÃO ====================
        right_layout.addStretch()

        # Registro manual
        self.btn_manual = QPushButton("REGISTRO MANUAL")
        self.btn_manual.setObjectName("btnManual")
        self.btn_manual.clicked.connect(self._abrir_registro_manual)
        right_layout.addWidget(self.btn_manual)

        # Cadastrar aluno
        self.btn_cadastro = QPushButton("CADASTRAR ALUNO")
        self.btn_cadastro.setObjectName("btnCadastro")
        self.btn_cadastro.clicked.connect(self._abrir_cadastro)
        right_layout.addWidget(self.btn_cadastro)

        # Ver registros
        self.btn_registros = QPushButton("VER REGISTROS")
        self.btn_registros.setObjectName("btnRegistros")
        self.btn_registros.clicked.connect(self._abrir_registros)
        right_layout.addWidget(self.btn_registros)

        # Configurações
        self.btn_config = QPushButton("CONFIGURAÇÕES")
        self.btn_config.setObjectName("btnConfig")
        self.btn_config.clicked.connect(self._abrir_configuracoes)
        right_layout.addWidget(self.btn_config)

        right_layout.addSpacing(10)

        # Créditos do desenvolvedor
        creditos_frame = QFrame()
        creditos_frame.setObjectName("creditosFrame")
        creditos_layout = QVBoxLayout(creditos_frame)
        creditos_layout.setSpacing(2)
        creditos_layout.setContentsMargins(5, 8, 5, 8)

        dev_label = QLabel(self.config.config.desenvolvedor)
        dev_label.setObjectName("devLabel")
        dev_label.setAlignment(Qt.AlignCenter)
        creditos_layout.addWidget(dev_label)

        dev_nome = QLabel(self.config.config.desenvolvedor_responsavel)
        dev_nome.setObjectName("devNome")
        dev_nome.setAlignment(Qt.AlignCenter)
        creditos_layout.addWidget(dev_nome)

        right_layout.addWidget(creditos_frame)

        main_layout.addWidget(right_panel, stretch=1)

    def _setup_timers(self):
        """Configura os timers do sistema"""
        # Timer para atualizar frame da câmera (30ms = ~33fps)
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self._atualizar_frame)
        self.camera_timer.start(30)

        # Timer para limpar feedback (1 segundo)
        self.feedback_timer = QTimer()
        self.feedback_timer.timeout.connect(self._decrementar_feedback)
        self.feedback_timer.start(1000)

    def _iniciar_camera(self):
        """Inicia a câmera"""
        if self.camera.iniciar():
            self.status_camera.setText("Status: Câmera ativa")
            self.status_camera.setStyleSheet("color: #27ae60;")
        else:
            self.status_camera.setText("Status: Câmera não disponível")
            self.status_camera.setStyleSheet("color: #e74c3c;")
            self.camera_label.setText("Câmera não disponível\nVerifique a conexão")

    def _atualizar_frame(self):
        """Atualiza o frame da câmera e processa reconhecimento"""
        frame = self.camera.capturar_frame()

        if frame is None:
            return

        # Espelha o frame para efeito espelho
        frame = self.camera.espelhar_frame(frame)

        # Processa reconhecimento a cada 5 frames (para performance)
        self.frame_contador += 1
        if self.frame_contador >= 5 and self.reconhecimento_ativo and self.tempo_feedback == 0:
            self.frame_contador = 0
            self._processar_reconhecimento(frame)

        # Aplica overlay se houver feedback ativo
        if self.tempo_feedback > 0:
            if self.ultimo_reconhecimento and self.ultimo_reconhecimento.reconhecido:
                # Verde para reconhecido
                frame = self.camera.adicionar_overlay(frame, (0, 255, 0), 0.2)
            else:
                # Vermelho para não reconhecido
                frame = self.camera.adicionar_overlay(frame, (0, 0, 255), 0.2)

        # Converte para QImage e exibe
        self._exibir_frame(frame)

    def _processar_reconhecimento(self, frame):
        """Processa reconhecimento facial no frame"""
        # Detecta rostos
        face_locations = self.facial_recognition.detectar_rostos(frame)

        if not face_locations:
            return

        # Tenta reconhecer o primeiro rosto detectado
        resultado = self.facial_recognition.reconhecer_rosto(frame, face_locations[0])

        if resultado.reconhecido:
            self._registrar_reconhecimento(resultado)

    def _registrar_reconhecimento(self, resultado: ResultadoReconhecimento):
        """Registra um reconhecimento bem-sucedido"""
        # Busca dados completos do aluno
        aluno = self.db.buscar_aluno_por_id(resultado.aluno_id)

        if not aluno:
            return

        # Verifica se já não registrou recentemente (evita duplicatas)
        ultimo = self.db.ultimo_registro_aluno(aluno.id)
        if ultimo and ultimo.tipo == self.modo_atual:
            diferenca = (datetime.now() - ultimo.data_hora).total_seconds()
            tempo_minimo = self.config.config.tempo_entre_registros
            if diferenca < tempo_minimo:
                return

        # Cria registro
        registro = Registro(
            aluno_id=aluno.id,
            tipo=self.modo_atual,
            data_hora=datetime.now(),
            confianca=resultado.confianca,
            manual=False
        )

        self.db.inserir_registro(registro)

        # Atualiza interface
        self._exibir_feedback_reconhecimento(aluno, resultado.confianca)
        self._atualizar_contadores()

        # Ativa feedback visual
        self.ultimo_reconhecimento = resultado
        self.tempo_feedback = 3  # 3 segundos

    def _exibir_feedback_reconhecimento(self, aluno, confianca):
        """Exibe feedback visual do reconhecimento"""
        # Atualiza nome
        self.nome_aluno.setText(aluno.nome)

        # Atualiza horário
        self.horario_label.setText(datetime.now().strftime("%H:%M:%S"))

        # Atualiza confiança
        self.confianca_label.setText(f"Confiança: {confianca:.1f}%")

        # Carrega foto do aluno
        if aluno.foto_path and os.path.exists(aluno.foto_path):
            pixmap = QPixmap(aluno.foto_path)
            pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.foto_aluno.setPixmap(pixmap)
        else:
            self.foto_aluno.setText(aluno.nome[:2].upper())

    def _decrementar_feedback(self):
        """Decrementa o contador de feedback"""
        if self.tempo_feedback > 0:
            self.tempo_feedback -= 1

    def _exibir_frame(self, frame):
        """Converte e exibe o frame na interface"""
        # Converte BGR para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Cria QImage
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        # Converte para QPixmap e redimensiona
        pixmap = QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(self.camera_label.width(), self.camera_label.height(),
                               Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.camera_label.setPixmap(pixmap)

    def _set_modo(self, modo: str):
        """Define o modo de operação (entrada/saída)"""
        self.modo_atual = modo

        if modo == "entrada":
            self.btn_entrada.setChecked(True)
            self.btn_saida.setChecked(False)
            self.modo_label.setText("Registrando: ENTRADA")
            self.modo_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.btn_entrada.setChecked(False)
            self.btn_saida.setChecked(True)
            self.modo_label.setText("Registrando: SAÍDA")
            self.modo_label.setStyleSheet("color: #e74c3c; font-weight: bold;")

    def _atualizar_contadores(self):
        """Atualiza os contadores de entrada/saída"""
        contagens = self.db.contar_registros_hoje()
        self.contador_entradas.setText(str(contagens['entrada']))
        self.contador_saidas.setText(str(contagens['saida']))

    def _abrir_cadastro(self):
        """Abre a janela de cadastro de alunos"""
        self.reconhecimento_ativo = False
        cadastro = CadastroWindow(self.db, self.facial_recognition, self.camera, self)
        cadastro.exec_()
        self.reconhecimento_ativo = True

    def _abrir_registros(self):
        """Abre a janela de visualização de registros"""
        registros = RegistrosWindow(self.db, self)
        registros.exec_()

    def _abrir_configuracoes(self):
        """Abre a janela de configurações"""
        config_window = ConfigWindow(self)
        if config_window.exec_():
            # Atualiza a interface com as novas configurações
            self.config = get_config()
            self.escola_label.setText(self.config.nome_completo_escola)
            self.setWindowTitle(f"Guardião Escolar - {self.config.config.nome_escola}")
            # Atualiza tolerância do reconhecimento facial
            self.facial_recognition.tolerance = self.config.config.tolerancia_reconhecimento

    def _abrir_registro_manual(self):
        """Abre diálogo para registro manual"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Registro Manual")
        dialog.setMinimumWidth(300)

        layout = QVBoxLayout(dialog)

        layout.addWidget(QLabel("Digite a matrícula do aluno:"))

        matricula_input = QLineEdit()
        matricula_input.setPlaceholderText("Matrícula")
        layout.addWidget(matricula_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            matricula = matricula_input.text().strip()
            if matricula:
                aluno = self.db.buscar_aluno_por_matricula(matricula)
                if aluno:
                    registro = Registro(
                        aluno_id=aluno.id,
                        tipo=self.modo_atual,
                        data_hora=datetime.now(),
                        confianca=100.0,
                        manual=True
                    )
                    self.db.inserir_registro(registro)
                    self._exibir_feedback_reconhecimento(aluno, 100.0)
                    self._atualizar_contadores()
                    self.tempo_feedback = 3
                    QMessageBox.information(self, "Sucesso",
                                            f"Registro de {self.modo_atual} realizado para {aluno.nome}")
                else:
                    QMessageBox.warning(self, "Erro",
                                        f"Aluno com matrícula {matricula} não encontrado")

    def _get_stylesheet(self):
        """Retorna o stylesheet da aplicação"""
        return """
            QMainWindow {
                background-color: #1a1a2e;
            }

            QFrame#cameraPanel {
                background-color: #16213e;
                border-radius: 10px;
                padding: 15px;
            }

            QFrame#controlPanel {
                background-color: #16213e;
                border-radius: 10px;
                padding: 15px;
            }

            QLabel#sectionTitle {
                color: #e94560;
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }

            QLabel#mainTitle {
                color: #e94560;
                font-size: 28px;
                font-weight: bold;
            }

            QLabel#subtitle {
                color: #a0a0a0;
                font-size: 14px;
            }

            QLabel#escolaLabel {
                color: #3498db;
                font-size: 13px;
                font-weight: bold;
                padding: 5px;
            }

            QLabel#cameraPreview {
                background-color: #0f0f1a;
                border: 2px solid #e94560;
                border-radius: 10px;
            }

            QLabel#statusLabel {
                color: #a0a0a0;
                font-size: 14px;
                padding: 5px;
            }

            QGroupBox {
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #3a3a5c;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }

            QPushButton#modoEntrada {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 100px;
            }

            QPushButton#modoEntrada:checked {
                background-color: #1e8449;
                border: 3px solid #ffffff;
            }

            QPushButton#modoEntrada:hover {
                background-color: #2ecc71;
            }

            QPushButton#modoSaida {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 100px;
            }

            QPushButton#modoSaida:checked {
                background-color: #c0392b;
                border: 3px solid #ffffff;
            }

            QPushButton#modoSaida:hover {
                background-color: #ec7063;
            }

            QLabel#modoIndicator {
                color: #27ae60;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }

            QLabel#fotoAluno {
                background-color: #0f0f1a;
                border: 2px solid #3a3a5c;
                border-radius: 75px;
                color: #ffffff;
                font-size: 36px;
                font-weight: bold;
            }

            QLabel#nomeAluno {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }

            QLabel#horarioLabel {
                color: #e94560;
                font-size: 24px;
                font-weight: bold;
            }

            QLabel#confiancaLabel {
                color: #27ae60;
                font-size: 14px;
            }

            QFrame#contadorEntrada {
                background-color: rgba(39, 174, 96, 0.2);
                border: 1px solid #27ae60;
                border-radius: 8px;
                padding: 10px;
            }

            QFrame#contadorSaida {
                background-color: rgba(231, 76, 60, 0.2);
                border: 1px solid #e74c3c;
                border-radius: 8px;
                padding: 10px;
            }

            QLabel#contadorNumero {
                color: #ffffff;
                font-size: 36px;
                font-weight: bold;
            }

            QPushButton#btnManual {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }

            QPushButton#btnManual:hover {
                background-color: #f7b731;
            }

            QPushButton#btnCadastro {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }

            QPushButton#btnCadastro:hover {
                background-color: #5dade2;
            }

            QPushButton#btnRegistros {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }

            QPushButton#btnRegistros:hover {
                background-color: #a569bd;
            }

            QPushButton#btnConfig {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 8px;
            }

            QPushButton#btnConfig:hover {
                background-color: #4a6a8a;
            }

            QFrame#creditosFrame {
                background-color: #0f0f1a;
                border: 1px solid #3a3a5c;
                border-radius: 6px;
            }

            QLabel#devLabel {
                color: #3498db;
                font-size: 10px;
                font-weight: bold;
            }

            QLabel#devNome {
                color: #f39c12;
                font-size: 10px;
            }

            QLineEdit {
                background-color: #0f0f1a;
                color: white;
                border: 1px solid #3a3a5c;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border-color: #e94560;
            }
        """

    def closeEvent(self, event):
        """Evento de fechamento da janela"""
        # Para a câmera
        self.camera.parar()

        # Fecha conexão com banco
        self.db.close()

        event.accept()
