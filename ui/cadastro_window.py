"""
Janela de Cadastro de Alunos
Interface para capturar fotos e cadastrar novos alunos no sistema
"""

import cv2
import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QFrame, QMessageBox,
    QProgressBar, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap

from database.models import Database, Aluno
from core.facial_recognition import FacialRecognition
from core.camera_handler import CameraHandler


class CadastroWindow(QDialog):
    """Janela para cadastro de novos alunos"""

    def __init__(self, db: Database, facial_recognition: FacialRecognition,
                 camera: CameraHandler, parent=None):
        super().__init__(parent)

        self.db = db
        self.facial_recognition = facial_recognition
        self.camera = camera

        # Estado do cadastro
        self.fotos_capturadas = []
        self.encodings_capturados = []
        self.max_fotos = 5
        self.captura_ativa = True

        # Configura interface
        self._setup_ui()
        self._setup_timer()

    def _setup_ui(self):
        """Configura a interface gráfica"""
        self.setWindowTitle("Cadastrar Novo Aluno")
        self.setMinimumSize(900, 600)
        self.setStyleSheet(self._get_stylesheet())

        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # ==================== PAINEL ESQUERDO (Câmera) ====================
        left_panel = QFrame()
        left_panel.setObjectName("panel")
        left_layout = QVBoxLayout(left_panel)

        # Título
        titulo = QLabel("CAPTURA DE FOTOS")
        titulo.setObjectName("sectionTitle")
        titulo.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(titulo)

        # Preview da câmera
        self.camera_label = QLabel()
        self.camera_label.setObjectName("cameraPreview")
        self.camera_label.setFixedSize(480, 360)
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setText("Câmera...")
        left_layout.addWidget(self.camera_label, alignment=Qt.AlignCenter)

        # Instrução
        self.instrucao_label = QLabel("Posicione o rosto no centro da câmera")
        self.instrucao_label.setObjectName("instrucao")
        self.instrucao_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.instrucao_label)

        # Progresso de fotos
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.max_fotos)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v de %m fotos capturadas")
        left_layout.addWidget(self.progress_bar)

        # Botão de captura
        self.btn_capturar = QPushButton("CAPTURAR FOTO (ESPAÇO)")
        self.btn_capturar.setObjectName("btnCapturar")
        self.btn_capturar.clicked.connect(self._capturar_foto)
        left_layout.addWidget(self.btn_capturar)

        # Preview das fotos capturadas
        fotos_group = QGroupBox("Fotos Capturadas")
        fotos_layout = QHBoxLayout(fotos_group)

        self.foto_labels = []
        for i in range(self.max_fotos):
            foto_label = QLabel()
            foto_label.setObjectName("fotoMiniatura")
            foto_label.setFixedSize(80, 80)
            foto_label.setAlignment(Qt.AlignCenter)
            foto_label.setText(str(i + 1))
            fotos_layout.addWidget(foto_label)
            self.foto_labels.append(foto_label)

        left_layout.addWidget(fotos_group)

        # Botão recomeçar
        self.btn_recomecar = QPushButton("RECOMEÇAR CAPTURAS")
        self.btn_recomecar.setObjectName("btnSecundario")
        self.btn_recomecar.clicked.connect(self._recomecar_capturas)
        left_layout.addWidget(self.btn_recomecar)

        main_layout.addWidget(left_panel)

        # ==================== PAINEL DIREITO (Dados) ====================
        right_panel = QFrame()
        right_panel.setObjectName("panel")
        right_layout = QVBoxLayout(right_panel)

        # Título
        titulo_dados = QLabel("DADOS DO ALUNO")
        titulo_dados.setObjectName("sectionTitle")
        titulo_dados.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(titulo_dados)

        # Formulário
        form_layout = QGridLayout()
        form_layout.setSpacing(15)

        # Matrícula
        form_layout.addWidget(QLabel("Matrícula:"), 0, 0)
        self.input_matricula = QLineEdit()
        self.input_matricula.setPlaceholderText("Digite a matrícula")
        form_layout.addWidget(self.input_matricula, 0, 1)

        # Nome
        form_layout.addWidget(QLabel("Nome Completo:"), 1, 0)
        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Digite o nome completo")
        form_layout.addWidget(self.input_nome, 1, 1)

        # Turma
        form_layout.addWidget(QLabel("Turma:"), 2, 0)
        self.input_turma = QLineEdit()
        self.input_turma.setPlaceholderText("Ex: 9º A, 1º B")
        form_layout.addWidget(self.input_turma, 2, 1)

        right_layout.addLayout(form_layout)
        right_layout.addStretch()

        # Status
        self.status_label = QLabel("Capture 5 fotos e preencha os dados")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        right_layout.addWidget(self.status_label)

        # Botões
        botoes_layout = QHBoxLayout()

        self.btn_cancelar = QPushButton("CANCELAR")
        self.btn_cancelar.setObjectName("btnCancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        botoes_layout.addWidget(self.btn_cancelar)

        self.btn_salvar = QPushButton("SALVAR CADASTRO")
        self.btn_salvar.setObjectName("btnSalvar")
        self.btn_salvar.clicked.connect(self._salvar_cadastro)
        self.btn_salvar.setEnabled(False)
        botoes_layout.addWidget(self.btn_salvar)

        right_layout.addLayout(botoes_layout)

        main_layout.addWidget(right_panel)

    def _setup_timer(self):
        """Configura timer para atualização da câmera"""
        self.camera_timer = QTimer()
        self.camera_timer.timeout.connect(self._atualizar_frame)
        self.camera_timer.start(30)

    def _atualizar_frame(self):
        """Atualiza o frame da câmera"""
        if not self.captura_ativa:
            return

        frame = self.camera.capturar_frame()
        if frame is None:
            return

        # Espelha
        frame = self.camera.espelhar_frame(frame)

        # Detecta rostos para feedback visual
        face_locations = self.facial_recognition.detectar_rostos(frame)

        if face_locations:
            # Desenha retângulo verde ao redor do rosto
            for face_loc in face_locations:
                frame = self.camera.desenhar_retangulo_rosto(frame, face_loc, (0, 255, 0), 3)

            self.instrucao_label.setText("Rosto detectado! Pressione ESPAÇO ou clique em CAPTURAR")
            self.instrucao_label.setStyleSheet("color: #27ae60;")
        else:
            self.instrucao_label.setText("Posicione o rosto no centro da câmera")
            self.instrucao_label.setStyleSheet("color: #f39c12;")

        # Exibe frame
        self._exibir_frame(frame)

    def _exibir_frame(self, frame):
        """Exibe o frame na interface"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(480, 360, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.camera_label.setPixmap(pixmap)

    def _capturar_foto(self):
        """Captura uma foto para o cadastro"""
        if len(self.fotos_capturadas) >= self.max_fotos:
            QMessageBox.information(self, "Aviso", "Já foram capturadas 5 fotos")
            return

        frame = self.camera.capturar_frame()
        if frame is None:
            QMessageBox.warning(self, "Erro", "Não foi possível capturar a foto")
            return

        # Espelha
        frame = self.camera.espelhar_frame(frame)

        # Gera encoding
        encoding = self.facial_recognition.gerar_encoding(frame)

        if encoding is None:
            QMessageBox.warning(self, "Erro",
                                "Nenhum rosto detectado. Posicione-se melhor e tente novamente.")
            return

        # Armazena foto e encoding
        self.fotos_capturadas.append(frame.copy())
        self.encodings_capturados.append(encoding)

        # Atualiza miniatura
        index = len(self.fotos_capturadas) - 1
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        qt_image = QImage(rgb_frame.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.foto_labels[index].setPixmap(pixmap)

        # Atualiza progresso
        self.progress_bar.setValue(len(self.fotos_capturadas))

        # Atualiza status
        self.status_label.setText(f"Foto {len(self.fotos_capturadas)} de {self.max_fotos} capturada!")
        self.status_label.setStyleSheet("color: #27ae60;")

        # Habilita salvar se tiver todas as fotos
        if len(self.fotos_capturadas) >= self.max_fotos:
            self.btn_salvar.setEnabled(True)
            self.instrucao_label.setText("Todas as fotos capturadas! Preencha os dados e salve.")
            self.instrucao_label.setStyleSheet("color: #27ae60;")
            self.btn_capturar.setEnabled(False)

    def _recomecar_capturas(self):
        """Recomeça o processo de captura de fotos"""
        self.fotos_capturadas = []
        self.encodings_capturados = []
        self.progress_bar.setValue(0)
        self.btn_salvar.setEnabled(False)
        self.btn_capturar.setEnabled(True)

        # Limpa miniaturas
        for label in self.foto_labels:
            label.clear()
            label.setText(str(self.foto_labels.index(label) + 1))

        self.status_label.setText("Capturas reiniciadas. Capture 5 fotos.")
        self.status_label.setStyleSheet("color: #ffffff;")

    def _salvar_cadastro(self):
        """Salva o cadastro do aluno"""
        # Valida dados
        matricula = self.input_matricula.text().strip()
        nome = self.input_nome.text().strip()
        turma = self.input_turma.text().strip()

        if not matricula:
            QMessageBox.warning(self, "Erro", "Digite a matrícula do aluno")
            self.input_matricula.setFocus()
            return

        if not nome:
            QMessageBox.warning(self, "Erro", "Digite o nome do aluno")
            self.input_nome.setFocus()
            return

        if not turma:
            QMessageBox.warning(self, "Erro", "Digite a turma do aluno")
            self.input_turma.setFocus()
            return

        if len(self.encodings_capturados) < self.max_fotos:
            QMessageBox.warning(self, "Erro", f"Capture todas as {self.max_fotos} fotos antes de salvar")
            return

        # Verifica se matrícula já existe
        aluno_existente = self.db.buscar_aluno_por_matricula(matricula)
        if aluno_existente:
            QMessageBox.warning(self, "Erro", f"Já existe um aluno com a matrícula {matricula}")
            self.input_matricula.setFocus()
            return

        try:
            # Cria diretório para fotos do aluno
            fotos_dir = os.path.join("data", "fotos", matricula)
            os.makedirs(fotos_dir, exist_ok=True)

            # Salva primeira foto como foto principal
            foto_path = self.camera.salvar_foto(
                self.fotos_capturadas[0],
                fotos_dir,
                "principal"
            )

            # Salva todas as fotos
            for i, foto in enumerate(self.fotos_capturadas):
                self.camera.salvar_foto(foto, fotos_dir, f"foto_{i+1}")

            # Cria aluno no banco
            aluno = Aluno(
                matricula=matricula,
                nome=nome,
                turma=turma,
                ativo=True,
                foto_path=foto_path
            )

            aluno_id = self.db.inserir_aluno(aluno)

            # Cadastra reconhecimento facial
            sucesso = self.facial_recognition.cadastrar_rosto(
                aluno_id,
                nome,
                self.encodings_capturados
            )

            if sucesso:
                QMessageBox.information(self, "Sucesso",
                                        f"Aluno {nome} cadastrado com sucesso!\n"
                                        f"Matrícula: {matricula}\n"
                                        f"Turma: {turma}")
                self.accept()
            else:
                QMessageBox.warning(self, "Aviso",
                                    "Aluno cadastrado, mas houve problema ao salvar o reconhecimento facial")
                self.accept()

        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar cadastro: {str(e)}")

    def keyPressEvent(self, event):
        """Captura tecla ESPAÇO para capturar foto"""
        if event.key() == Qt.Key_Space:
            self._capturar_foto()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Evento de fechamento"""
        self.camera_timer.stop()
        self.captura_ativa = False
        event.accept()

    def _get_stylesheet(self):
        """Retorna o stylesheet da janela"""
        return """
            QDialog {
                background-color: #1a1a2e;
            }

            QFrame#panel {
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

            QLabel#cameraPreview {
                background-color: #0f0f1a;
                border: 2px solid #e94560;
                border-radius: 10px;
            }

            QLabel#instrucao {
                color: #f39c12;
                font-size: 14px;
                padding: 10px;
            }

            QLabel#fotoMiniatura {
                background-color: #0f0f1a;
                border: 2px solid #3a3a5c;
                border-radius: 5px;
                color: #666666;
                font-size: 24px;
            }

            QLabel#statusLabel {
                color: #ffffff;
                font-size: 14px;
                padding: 15px;
            }

            QProgressBar {
                background-color: #0f0f1a;
                border: 1px solid #3a3a5c;
                border-radius: 5px;
                text-align: center;
                color: white;
                height: 25px;
            }

            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 4px;
            }

            QGroupBox {
                color: #ffffff;
                font-size: 14px;
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

            QLineEdit {
                background-color: #0f0f1a;
                color: white;
                border: 1px solid #3a3a5c;
                border-radius: 5px;
                padding: 12px;
                font-size: 14px;
            }

            QLineEdit:focus {
                border-color: #e94560;
            }

            QLabel {
                color: #ffffff;
                font-size: 14px;
            }

            QPushButton#btnCapturar {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }

            QPushButton#btnCapturar:hover {
                background-color: #2ecc71;
            }

            QPushButton#btnCapturar:disabled {
                background-color: #1e5f3b;
            }

            QPushButton#btnSecundario {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 10px;
                font-size: 12px;
                border-radius: 5px;
            }

            QPushButton#btnSecundario:hover {
                background-color: #4a6a8a;
            }

            QPushButton#btnSalvar {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }

            QPushButton#btnSalvar:hover {
                background-color: #5dade2;
            }

            QPushButton#btnSalvar:disabled {
                background-color: #1a4a6e;
            }

            QPushButton#btnCancelar {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
            }

            QPushButton#btnCancelar:hover {
                background-color: #ec7063;
            }
        """
