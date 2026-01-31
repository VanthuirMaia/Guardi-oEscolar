"""
Módulo de Configurações do Sistema
Gerencia configurações personalizáveis do Guardião Escolar
"""

import os
import json
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class ConfiguracaoSistema:
    """Configurações personalizáveis do sistema"""
    # Dados da escola
    nome_escola: str = "Escola Municipal"
    cidade: str = "Cidade"
    estado: str = "UF"

    # Configurações de reconhecimento
    tolerancia_reconhecimento: float = 0.6
    tempo_entre_registros: int = 60  # segundos

    # Aparência
    tema: str = "escuro"

    # Informações do desenvolvedor (fixo)
    desenvolvedor: str = "Axio - Sistemas e Automações Inteligentes"
    desenvolvedor_responsavel: str = "Vanthuir Maia"
    versao: str = "1.0.0"


class GerenciadorConfig:
    """Gerenciador de configurações do sistema"""

    def __init__(self, config_path: str = "data/config.json"):
        self.config_path = config_path
        self.config = ConfiguracaoSistema()
        self._carregar()

    def _carregar(self):
        """Carrega configurações do arquivo"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Atualiza apenas os campos que existem no arquivo
                    for key, value in data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
                print("Configurações carregadas com sucesso")
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")

    def salvar(self):
        """Salva configurações no arquivo"""
        try:
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.config), f, indent=4, ensure_ascii=False)
            print("Configurações salvas com sucesso")
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False

    def get(self, chave: str, padrao=None):
        """Obtém um valor de configuração"""
        return getattr(self.config, chave, padrao)

    def set(self, chave: str, valor):
        """Define um valor de configuração"""
        if hasattr(self.config, chave):
            setattr(self.config, chave, valor)
            return True
        return False

    @property
    def nome_completo_escola(self) -> str:
        """Retorna nome completo da escola com cidade"""
        return f"{self.config.nome_escola} - {self.config.cidade}/{self.config.estado}"

    @property
    def creditos_desenvolvedor(self) -> str:
        """Retorna créditos do desenvolvedor"""
        return f"{self.config.desenvolvedor} - {self.config.desenvolvedor_responsavel}"

    @property
    def versao_sistema(self) -> str:
        """Retorna versão do sistema"""
        return f"Guardião Escolar v{self.config.versao}"


# Instância global de configurações
_config_instance: Optional[GerenciadorConfig] = None


def get_config() -> GerenciadorConfig:
    """Retorna a instância global de configurações"""
    global _config_instance
    if _config_instance is None:
        _config_instance = GerenciadorConfig()
    return _config_instance
