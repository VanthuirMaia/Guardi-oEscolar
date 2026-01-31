"""
Módulo de Manipulação da Câmera
Responsável por captura de vídeo e processamento de frames
"""

import cv2
import numpy as np
from typing import Optional, Tuple
import os


class CameraHandler:
    """Classe responsável pela manipulação da câmera/webcam"""

    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480):
        """
        Inicializa o manipulador de câmera

        Args:
            camera_index: Índice da câmera (0 = padrão)
            width: Largura do frame
            height: Altura do frame
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False

    def iniciar(self) -> bool:
        """
        Inicia a captura da câmera

        Returns:
            True se iniciou com sucesso, False caso contrário
        """
        try:
            # Tenta abrir a câmera
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)  # CAP_DSHOW para Windows

            if not self.cap.isOpened():
                # Tenta sem CAP_DSHOW
                self.cap = cv2.VideoCapture(self.camera_index)

            if not self.cap.isOpened():
                print(f"Erro: Não foi possível abrir a câmera {self.camera_index}")
                return False

            # Configura resolução
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            # Configura buffer pequeno para menor latência
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

            self.is_running = True
            print(f"Câmera {self.camera_index} iniciada com sucesso")
            return True

        except Exception as e:
            print(f"Erro ao iniciar câmera: {e}")
            return False

    def parar(self):
        """Para a captura da câmera"""
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        print("Câmera parada")

    def capturar_frame(self) -> Optional[np.ndarray]:
        """
        Captura um frame da câmera

        Returns:
            Frame em formato numpy array (BGR) ou None se falhar
        """
        if not self.is_running or self.cap is None:
            return None

        ret, frame = self.cap.read()

        if ret:
            return frame
        return None

    def capturar_frame_rgb(self) -> Optional[np.ndarray]:
        """
        Captura um frame e converte para RGB

        Returns:
            Frame em formato numpy array (RGB) ou None se falhar
        """
        frame = self.capturar_frame()
        if frame is not None:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return None

    def salvar_foto(self, frame: np.ndarray, diretorio: str, nome_arquivo: str) -> Optional[str]:
        """
        Salva um frame como imagem

        Args:
            frame: Frame a salvar
            diretorio: Diretório de destino
            nome_arquivo: Nome do arquivo (sem extensão)

        Returns:
            Caminho completo do arquivo salvo ou None se falhar
        """
        try:
            os.makedirs(diretorio, exist_ok=True)
            caminho = os.path.join(diretorio, f"{nome_arquivo}.jpg")
            cv2.imwrite(caminho, frame)
            return caminho
        except Exception as e:
            print(f"Erro ao salvar foto: {e}")
            return None

    def desenhar_retangulo_rosto(self, frame: np.ndarray,
                                   face_location: Tuple[int, int, int, int],
                                   cor: Tuple[int, int, int] = (0, 255, 0),
                                   espessura: int = 2) -> np.ndarray:
        """
        Desenha retângulo ao redor do rosto detectado

        Args:
            frame: Frame original
            face_location: Coordenadas do rosto (top, right, bottom, left)
            cor: Cor do retângulo em BGR
            espessura: Espessura da linha

        Returns:
            Frame com retângulo desenhado
        """
        frame_copy = frame.copy()
        top, right, bottom, left = face_location
        cv2.rectangle(frame_copy, (left, top), (right, bottom), cor, espessura)
        return frame_copy

    def adicionar_texto(self, frame: np.ndarray, texto: str,
                        posicao: Tuple[int, int] = (10, 30),
                        cor: Tuple[int, int, int] = (255, 255, 255),
                        tamanho: float = 0.8,
                        espessura: int = 2) -> np.ndarray:
        """
        Adiciona texto ao frame

        Args:
            frame: Frame original
            texto: Texto a adicionar
            posicao: Posição (x, y) do texto
            cor: Cor do texto em BGR
            tamanho: Escala da fonte
            espessura: Espessura da fonte

        Returns:
            Frame com texto adicionado
        """
        frame_copy = frame.copy()
        cv2.putText(frame_copy, texto, posicao, cv2.FONT_HERSHEY_SIMPLEX,
                   tamanho, cor, espessura)
        return frame_copy

    def adicionar_overlay(self, frame: np.ndarray, cor: Tuple[int, int, int],
                          alpha: float = 0.3) -> np.ndarray:
        """
        Adiciona overlay colorido ao frame (feedback visual)

        Args:
            frame: Frame original
            cor: Cor do overlay em BGR
            alpha: Transparência (0-1)

        Returns:
            Frame com overlay
        """
        overlay = np.full(frame.shape, cor, dtype=np.uint8)
        return cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)

    def espelhar_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Espelha o frame horizontalmente (efeito espelho)

        Args:
            frame: Frame original

        Returns:
            Frame espelhado
        """
        return cv2.flip(frame, 1)

    def redimensionar_frame(self, frame: np.ndarray, largura: int, altura: int) -> np.ndarray:
        """
        Redimensiona o frame para as dimensões especificadas

        Args:
            frame: Frame original
            largura: Nova largura
            altura: Nova altura

        Returns:
            Frame redimensionado
        """
        return cv2.resize(frame, (largura, altura))

    @property
    def esta_ativa(self) -> bool:
        """Verifica se a câmera está ativa"""
        return self.is_running and self.cap is not None and self.cap.isOpened()

    def listar_cameras_disponiveis(self, max_cameras: int = 5) -> list:
        """
        Lista câmeras disponíveis no sistema

        Args:
            max_cameras: Número máximo de câmeras a verificar

        Returns:
            Lista de índices de câmeras disponíveis
        """
        cameras = []
        for i in range(max_cameras):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(i)
                cap.release()
        return cameras
