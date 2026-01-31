"""
Guardião Escolar - Sistema de Controle de Acesso Escolar
========================================================

Sistema desktop para controle de entrada e saída de alunos
utilizando reconhecimento facial.

Desenvolvido com:
- Python 3.8+
- PyQt5 (Interface gráfica)
- OpenCV (Captura de câmera)
- face_recognition (Reconhecimento facial)
- SQLite (Banco de dados local)

Uso:
    python main.py

Desenvolvido por: Axio - Sistemas e Automações Inteligentes
                  Vanthuir Maia
"""

import sys
import os

# Adiciona o diretório atual ao path para imports relativos
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Cria diretórios necessários
DIRETORIOS = [
    "data",
    "data/faces",
    "data/fotos"
]

for diretorio in DIRETORIOS:
    os.makedirs(diretorio, exist_ok=True)


def verificar_dependencias():
    """Verifica se todas as dependências estão instaladas"""
    dependencias = {
        'PyQt5': 'PyQt5',
        'cv2': 'opencv-python',
        'numpy': 'numpy',
        'PIL': 'Pillow'
    }

    faltando = []

    for modulo, pacote in dependencias.items():
        try:
            __import__(modulo)
        except ImportError:
            faltando.append(pacote)

    # Verifica face_recognition separadamente (pode falhar por causa do dlib)
    try:
        import face_recognition
    except ImportError:
        print("\n" + "=" * 60)
        print("AVISO: Biblioteca face_recognition não instalada!")
        print("=" * 60)
        print("\nO sistema funcionará em modo limitado (sem reconhecimento).")
        print("\nPara instalar o face_recognition no Windows:")
        print("1. Instale o Visual Studio Build Tools")
        print("2. Instale o cmake: pip install cmake")
        print("3. Instale o dlib: pip install dlib")
        print("4. Instale o face_recognition: pip install face_recognition")
        print("\nAlternativamente, use conda:")
        print("  conda install -c conda-forge dlib")
        print("  pip install face_recognition")
        print("=" * 60 + "\n")

    if faltando:
        print("\n" + "=" * 60)
        print("ERRO: Dependências não instaladas!")
        print("=" * 60)
        print(f"\nPacotes faltando: {', '.join(faltando)}")
        print("\nExecute: pip install -r requirements.txt")
        print("=" * 60 + "\n")
        return False

    return True


def main():
    """Função principal - inicia a aplicação"""

    # Verifica dependências
    if not verificar_dependencias():
        input("\nPressione ENTER para sair...")
        sys.exit(1)

    # Importa PyQt5
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtGui import QFont

    # Cria aplicação
    app = QApplication(sys.argv)
    app.setApplicationName("Guardião Escolar")
    app.setOrganizationName("Axio - Sistemas e Automações Inteligentes")

    # Configura fonte padrão
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    # Tenta iniciar a janela principal
    try:
        from ui.main_window import MainWindow
        from core.config import get_config

        # Carrega configurações
        config = get_config()

        # Cria e exibe janela principal
        window = MainWindow()
        window.show()

        # Mensagem inicial
        print("\n" + "=" * 60)
        print("   GUARDIÃO ESCOLAR - Sistema de Controle de Acesso")
        print("=" * 60)
        print(f"\n Escola: {config.nome_completo_escola}")
        print(f" Versão: {config.config.versao}")
        print("\n Sistema iniciado com sucesso!")
        print(" Câmera ativa e pronta para reconhecimento.")
        print("\n Atalhos:")
        print("   - ESPAÇO: Capturar foto (na tela de cadastro)")
        print("   - ESC: Fechar janelas de diálogo")
        print("\n" + "-" * 60)
        print(f" Desenvolvido por: {config.config.desenvolvedor}")
        print(f"                   {config.config.desenvolvedor_responsavel}")
        print("=" * 60 + "\n")

        # Executa loop da aplicação
        sys.exit(app.exec_())

    except Exception as e:
        # Exibe erro em dialog
        QMessageBox.critical(
            None,
            "Erro ao iniciar",
            f"Ocorreu um erro ao iniciar o sistema:\n\n{str(e)}\n\n"
            "Verifique se todas as dependências estão instaladas."
        )
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
