# Módulo core - Reconhecimento facial e câmera
from .facial_recognition import FacialRecognition
from .camera_handler import CameraHandler
from .config import get_config, GerenciadorConfig, ConfiguracaoSistema

__all__ = ['FacialRecognition', 'CameraHandler', 'get_config', 'GerenciadorConfig', 'ConfiguracaoSistema']
