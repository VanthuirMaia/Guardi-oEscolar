# Guardião Escolar

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15-green.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-orange.svg)

**Sistema de Controle de Acesso Escolar com Reconhecimento Facial**

*Tecnologia acessível para escolas públicas brasileiras*

</div>

---

## Sobre o Projeto

O **Guardião Escolar** nasceu de uma necessidade real: trazer tecnologia de ponta para escolas públicas que, muitas vezes, não têm acesso a soluções modernas de segurança e controle de acesso.

Este projeto foi desenvolvido com **cunho 100% social**, visando democratizar o acesso à tecnologia de reconhecimento facial para instituições de ensino público que enfrentam desafios diários relacionados à segurança e ao controle de entrada e saída de alunos.

### O Problema

Muitas escolas públicas brasileiras ainda dependem de métodos manuais e ultrapassados para controlar o acesso de alunos:
- Listas de chamada em papel
- Carteirinhas físicas facilmente perdidas ou falsificadas
- Porteiros sobrecarregados tentando identificar centenas de alunos
- Falta de registro histórico confiável de presença
- Dificuldade em notificar responsáveis sobre ausências

### A Solução

O Guardião Escolar oferece uma solução **gratuita, offline e de fácil implementação** que utiliza reconhecimento facial para:
- Registrar automaticamente a entrada e saída de alunos
- Manter histórico completo e confiável de acessos
- Funcionar 100% localmente, sem necessidade de internet
- Rodar em hardware comum, sem exigir equipamentos caros

---

## Impacto Social

### Para as Escolas
- **Custo zero de licenciamento** - Software livre e gratuito
- **Independência de internet** - Funciona offline
- **Hardware acessível** - Roda em computadores comuns
- **Fácil manutenção** - Código aberto e documentado

### Para os Alunos
- **Mais segurança** - Controle rigoroso de quem entra e sai
- **Registro automático** - Sem filas ou atrasos na entrada
- **Privacidade garantida** - Dados armazenados apenas localmente

### Para os Responsáveis
- **Tranquilidade** - Saber que há controle de acesso na escola
- **Transparência** - Possibilidade de consultar registros

### Para a Comunidade
- **Modelo replicável** - Pode ser implementado em qualquer escola
- **Código aberto** - Permite adaptações às necessidades locais
- **Documentação completa** - Facilita a implementação por voluntários

---

## Funcionalidades

### Implementadas (MVP)
- [x] Monitoramento em tempo real via webcam
- [x] Reconhecimento facial automático
- [x] Modo entrada/saída (toggle)
- [x] Cadastro de alunos com captura de 5 fotos
- [x] Registro manual (fallback)
- [x] Visualização de registros do dia
- [x] Feedback visual (verde/vermelho)
- [x] Contador de entradas e saídas
- [x] Banco de dados local SQLite
- [x] Exportação de relatórios em PDF
- [x] Exportação para Excel (.xlsx)
- [x] Exportação para CSV
- [x] Tela de configurações personalizáveis
- [x] Personalização com nome da escola e cidade

### Roadmap Futuro
- [ ] Notificação para responsáveis (SMS/WhatsApp)
- [ ] Integração com sistema de frequência escolar
- [ ] Dashboard administrativo
- [ ] Suporte a múltiplas câmeras
- [ ] App mobile para consulta

---

## Requisitos do Sistema

### Hardware Mínimo
- Processador: Intel Core i3 ou equivalente
- Memória RAM: 4GB
- Webcam: 720p (comum em notebooks)
- Armazenamento: 1GB livre

### Hardware Recomendado
- Processador: Intel Core i5 ou superior
- Memória RAM: 8GB
- Webcam: 1080p USB externa
- Armazenamento: SSD com 5GB livres

### Software
- Windows 10/11, Linux ou macOS
- Python 3.8 ou superior

---

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/guardiao-escolar.git
cd guardiao-escolar
```

### 2. Crie um ambiente virtual (recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

#### Nota sobre o face_recognition no Windows

A biblioteca `face_recognition` requer o `dlib`, que pode ser trabalhoso de instalar no Windows. Opções:

**Opção 1 - Via Conda (mais fácil):**
```bash
conda install -c conda-forge dlib
pip install face_recognition
```

**Opção 2 - Via pip (requer Visual Studio Build Tools):**
```bash
pip install cmake
pip install dlib
pip install face_recognition
```

### 4. Execute o sistema
```bash
python main.py
```

---

## Como Usar

### Primeira Execução
1. Execute `python main.py`
2. O sistema abrirá a interface principal
3. A câmera será iniciada automaticamente

### Cadastrando Alunos
1. Clique em **"CADASTRAR ALUNO"**
2. Posicione o aluno em frente à câmera
3. Capture 5 fotos em diferentes ângulos
4. Preencha os dados (matrícula, nome, turma)
5. Clique em **"SALVAR CADASTRO"**

### Registrando Entradas/Saídas
1. Selecione o modo: **ENTRADA** ou **SAÍDA**
2. O aluno deve se posicionar em frente à câmera
3. O reconhecimento é automático
4. Feedback verde = reconhecido | Vermelho = não reconhecido

### Registro Manual
Caso o reconhecimento falhe:
1. Clique em **"REGISTRO MANUAL"**
2. Digite a matrícula do aluno
3. Confirme o registro

### Consultando Registros
1. Clique em **"VER REGISTROS"**
2. Selecione a data desejada
3. Filtre por tipo (entrada/saída) se necessário

---

## Estrutura do Projeto

```
guardiao-escolar/
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências do projeto
├── README.md              # Este arquivo
├── .gitignore             # Arquivos ignorados pelo Git
│
├── database/              # Módulo de banco de dados
│   ├── __init__.py
│   └── models.py          # Modelos e operações SQLite
│
├── core/                  # Módulo principal
│   ├── __init__.py
│   ├── facial_recognition.py  # Reconhecimento facial
│   ├── camera_handler.py      # Manipulação da câmera
│   └── config.py              # Gerenciador de configurações
│
├── ui/                    # Interface gráfica
│   ├── __init__.py
│   ├── main_window.py     # Janela principal
│   ├── cadastro_window.py # Tela de cadastro
│   ├── registros_window.py # Tela de registros
│   └── config_window.py   # Tela de configurações
│
└── data/                  # Dados locais (criado automaticamente)
    ├── guardiao_escolar.db    # Banco de dados SQLite
    ├── config.json            # Configurações personalizadas
    ├── faces/
    │   └── encodings.pkl      # Encodings faciais
    └── fotos/                 # Fotos dos alunos
        └── {matricula}/
            └── *.jpg
```

---

## Privacidade e Segurança

O Guardião Escolar foi desenvolvido com **privacidade em primeiro lugar**:

- **100% Offline**: Nenhum dado é enviado para a internet
- **Armazenamento Local**: Todos os dados ficam no computador da escola
- **Sem Nuvem**: Não há dependência de serviços externos
- **Código Aberto**: Qualquer pessoa pode auditar o código
- **LGPD**: Preparado para conformidade com a Lei Geral de Proteção de Dados

### Recomendações de Segurança
- Mantenha o computador com senha de acesso
- Faça backup regular do banco de dados
- Restrinja o acesso físico ao equipamento
- Obtenha consentimento dos responsáveis para uso de biometria facial

---

## Replicando em Outras Escolas

Este projeto foi criado para ser **facilmente replicável**. Se você quer implementar o Guardião Escolar em sua escola:

### Passo a Passo
1. **Avalie os requisitos** - Verifique se a escola tem um computador compatível
2. **Obtenha uma webcam** - Pode ser a do notebook ou uma USB externa
3. **Instale o sistema** - Siga o guia de instalação acima
4. **Treine a equipe** - O sistema é intuitivo, mas um breve treinamento ajuda
5. **Cadastre os alunos** - Pode ser feito gradualmente
6. **Comunique os responsáveis** - Explique o sistema e obtenha consentimento

### Suporte à Implementação
Se você é de uma escola pública e precisa de ajuda para implementar:
- Abra uma **Issue** no GitHub descrevendo sua necessidade
- Entre em contato pelos canais oficiais do projeto
- Busque apoio de voluntários na comunidade de tecnologia local

---

## Contribuindo

Contribuições são muito bem-vindas! Este é um projeto social e toda ajuda é valiosa.

### Como Contribuir
1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### Áreas que Precisam de Ajuda
- **Desenvolvimento**: Novas funcionalidades, correção de bugs
- **Documentação**: Melhorar guias, traduzir para outros idiomas
- **Testes**: Testar em diferentes ambientes e configurações
- **Design**: Melhorar a interface e experiência do usuário
- **Divulgação**: Ajudar a levar o projeto para mais escolas

---

## Tecnologias Utilizadas

| Tecnologia | Versão | Finalidade |
|------------|--------|------------|
| Python | 3.8+ | Linguagem principal |
| PyQt5 | 5.15 | Interface gráfica desktop |
| OpenCV | 4.8 | Captura e processamento de vídeo |
| face_recognition | 1.3 | Reconhecimento facial |
| dlib | 19.24 | Machine learning para detecção facial |
| SQLite | 3 | Banco de dados local |
| NumPy | 1.24 | Processamento numérico |
| Pillow | 10.1 | Manipulação de imagens |

---

## Licença

Este projeto é distribuído sob a licença **MIT**. Isso significa que você pode:
- Usar comercialmente
- Modificar
- Distribuir
- Usar privativamente

Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## Desenvolvedor

<div align="center">

**Axio - Sistemas e Automações Inteligentes**

Desenvolvido por **Vanthuir Maia**

*Projeto de cunho social para segurança escolar*

</div>

---

## Agradecimentos

- À comunidade open source por todas as bibliotecas utilizadas
- Aos educadores que dedicam suas vidas às escolas públicas
- A todos que acreditam que tecnologia pode transformar a educação

---

<div align="center">

**Feito com amor para a educação pública brasileira**

*"A educação é a arma mais poderosa para mudar o mundo"* - Nelson Mandela

**Axio - Sistemas e Automações Inteligentes | Vanthuir Maia**

</div>
