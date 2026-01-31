"""
Módulo de Reconhecimento Facial
Responsável por detectar e reconhecer rostos usando a biblioteca face_recognition
"""

import os
import pickle
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("AVISO: Biblioteca face_recognition não instalada. Usando modo simulado.")


@dataclass
class ResultadoReconhecimento:
    """Resultado de uma tentativa de reconhecimento"""
    reconhecido: bool = False
    aluno_id: Optional[int] = None
    nome: Optional[str] = None
    confianca: float = 0.0
    face_location: Optional[Tuple[int, int, int, int]] = None


class FacialRecognition:
    """Classe responsável pelo reconhecimento facial"""

    def __init__(self, encodings_path: str = "data/faces/encodings.pkl", tolerance: float = 0.6):
        """
        Inicializa o sistema de reconhecimento facial

        Args:
            encodings_path: Caminho para o arquivo de encodings salvos
            tolerance: Tolerância para matching (menor = mais rigoroso)
        """
        self.encodings_path = encodings_path
        self.tolerance = tolerance

        # Dicionários para armazenar encodings conhecidos
        self.known_encodings: List[np.ndarray] = []
        self.known_ids: List[int] = []
        self.known_names: List[str] = []

        # Garante que o diretório existe
        os.makedirs(os.path.dirname(encodings_path), exist_ok=True)

        # Carrega encodings salvos
        self._load_encodings()

    def _load_encodings(self):
        """Carrega encodings do arquivo pickle"""
        if os.path.exists(self.encodings_path):
            try:
                with open(self.encodings_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_encodings = data.get('encodings', [])
                    self.known_ids = data.get('ids', [])
                    self.known_names = data.get('names', [])
                print(f"Carregados {len(self.known_encodings)} encodings faciais")
            except Exception as e:
                print(f"Erro ao carregar encodings: {e}")
                self.known_encodings = []
                self.known_ids = []
                self.known_names = []

    def _save_encodings(self):
        """Salva encodings no arquivo pickle"""
        try:
            data = {
                'encodings': self.known_encodings,
                'ids': self.known_ids,
                'names': self.known_names
            }
            with open(self.encodings_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"Salvos {len(self.known_encodings)} encodings faciais")
        except Exception as e:
            print(f"Erro ao salvar encodings: {e}")

    def detectar_rostos(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detecta rostos em um frame

        Args:
            frame: Imagem em formato numpy array (BGR do OpenCV)

        Returns:
            Lista de localizações de rostos (top, right, bottom, left)
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return []

        # Converte de BGR (OpenCV) para RGB e garante array contíguo
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])

        # Reduz a imagem para processamento mais rápido
        small_frame = self._resize_frame(rgb_frame, 0.25)

        # Detecta rostos
        face_locations = face_recognition.face_locations(small_frame, model="hog")

        # Ajusta coordenadas para o tamanho original
        face_locations = [(int(top * 4), int(right * 4), int(bottom * 4), int(left * 4))
                         for (top, right, bottom, left) in face_locations]

        return face_locations

    def _resize_frame(self, frame: np.ndarray, scale: float) -> np.ndarray:
        """Redimensiona o frame mantendo proporções"""
        import cv2
        width = int(frame.shape[1] * scale)
        height = int(frame.shape[0] * scale)
        return cv2.resize(frame, (width, height))

    def reconhecer_rosto(self, frame: np.ndarray, face_location: Tuple[int, int, int, int] = None) -> ResultadoReconhecimento:
        """
        Tenta reconhecer um rosto no frame

        Args:
            frame: Imagem em formato numpy array (BGR do OpenCV)
            face_location: Localização específica do rosto (opcional)

        Returns:
            ResultadoReconhecimento com informações do reconhecimento
        """
        resultado = ResultadoReconhecimento()

        if not FACE_RECOGNITION_AVAILABLE:
            return resultado

        if len(self.known_encodings) == 0:
            return resultado

        # Converte para RGB e garante array contíguo
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])

        # Se não foi passada localização, detecta rostos
        if face_location is None:
            face_locations = face_recognition.face_locations(rgb_frame, model="hog")
            if not face_locations:
                return resultado
            face_location = face_locations[0]
        else:
            face_locations = [face_location]

        resultado.face_location = face_location

        # Gera encoding do rosto detectado
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if not face_encodings:
            return resultado

        face_encoding = face_encodings[0]

        # Compara com rostos conhecidos
        distances = face_recognition.face_distance(self.known_encodings, face_encoding)

        if len(distances) > 0:
            best_match_index = np.argmin(distances)
            best_distance = distances[best_match_index]

            # Verifica se está dentro da tolerância
            if best_distance <= self.tolerance:
                # Calcula confiança (quanto menor a distância, maior a confiança)
                confianca = (1 - best_distance) * 100

                resultado.reconhecido = True
                resultado.aluno_id = self.known_ids[best_match_index]
                resultado.nome = self.known_names[best_match_index]
                resultado.confianca = round(confianca, 1)

        return resultado

    def gerar_encoding(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Gera encoding facial de um frame

        Args:
            frame: Imagem em formato numpy array (BGR do OpenCV)

        Returns:
            Encoding facial ou None se não detectar rosto
        """
        if not FACE_RECOGNITION_AVAILABLE:
            return None

        # Converte para RGB e garante array contíguo (necessário para dlib)
        rgb_frame = np.ascontiguousarray(frame[:, :, ::-1])

        # Detecta rostos
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")

        if not face_locations:
            return None

        # Gera encoding do primeiro rosto detectado
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if face_encodings:
            return face_encodings[0]

        return None

    def cadastrar_rosto(self, aluno_id: int, nome: str, encodings: List[np.ndarray]) -> bool:
        """
        Cadastra um novo rosto no sistema

        Args:
            aluno_id: ID do aluno no banco de dados
            nome: Nome do aluno
            encodings: Lista de encodings faciais (múltiplas fotos)

        Returns:
            True se cadastrado com sucesso
        """
        if not encodings:
            return False

        # Remove encodings anteriores deste aluno (se existirem)
        self.remover_rosto(aluno_id)

        # Calcula encoding médio para maior robustez
        encoding_medio = np.mean(encodings, axis=0)

        # Adiciona aos conhecidos
        self.known_encodings.append(encoding_medio)
        self.known_ids.append(aluno_id)
        self.known_names.append(nome)

        # Salva no arquivo
        self._save_encodings()

        return True

    def remover_rosto(self, aluno_id: int) -> bool:
        """
        Remove um rosto cadastrado

        Args:
            aluno_id: ID do aluno a remover

        Returns:
            True se removido com sucesso
        """
        if aluno_id in self.known_ids:
            index = self.known_ids.index(aluno_id)
            del self.known_encodings[index]
            del self.known_ids[index]
            del self.known_names[index]
            self._save_encodings()
            return True
        return False

    def atualizar_nome(self, aluno_id: int, novo_nome: str) -> bool:
        """
        Atualiza o nome associado a um encoding

        Args:
            aluno_id: ID do aluno
            novo_nome: Novo nome

        Returns:
            True se atualizado com sucesso
        """
        if aluno_id in self.known_ids:
            index = self.known_ids.index(aluno_id)
            self.known_names[index] = novo_nome
            self._save_encodings()
            return True
        return False

    def total_cadastrados(self) -> int:
        """Retorna o total de rostos cadastrados"""
        return len(self.known_encodings)

    def encoding_to_bytes(self, encoding: np.ndarray) -> bytes:
        """Converte encoding numpy para bytes (para salvar no banco)"""
        return pickle.dumps(encoding)

    def bytes_to_encoding(self, data: bytes) -> np.ndarray:
        """Converte bytes para encoding numpy"""
        return pickle.loads(data)
