"""
Módulo de modelos e gerenciamento do banco de dados SQLite
"""

import sqlite3
import os
from datetime import datetime, date
from dataclasses import dataclass
from typing import Optional, List
import pickle


@dataclass
class Aluno:
    """Representa um aluno cadastrado no sistema"""
    id: Optional[int] = None
    matricula: str = ""
    nome: str = ""
    turma: str = ""
    face_encoding: Optional[bytes] = None
    ativo: bool = True
    data_cadastro: Optional[datetime] = None
    foto_path: Optional[str] = None


@dataclass
class Registro:
    """Representa um registro de entrada/saída"""
    id: Optional[int] = None
    aluno_id: int = 0
    tipo: str = "entrada"  # entrada ou saida
    data_hora: Optional[datetime] = None
    confianca: float = 0.0
    manual: bool = False
    aluno_nome: Optional[str] = None  # Para exibição
    aluno_matricula: Optional[str] = None  # Para exibição
    aluno_turma: Optional[str] = None  # Para exibição


class Database:
    """Gerenciador do banco de dados SQLite"""

    def __init__(self, db_path: str = "data/guardiao_escolar.db"):
        """Inicializa conexão com o banco de dados"""
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else "data", exist_ok=True)

        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """Estabelece conexão com o banco"""
        try:
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            raise

    def _create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        cursor = self.conn.cursor()

        # Tabela de alunos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                matricula TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                turma TEXT NOT NULL,
                face_encoding BLOB,
                ativo INTEGER DEFAULT 1,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                foto_path TEXT
            )
        ''')

        # Tabela de registros de entrada/saída
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
                data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confianca REAL DEFAULT 0.0,
                manual INTEGER DEFAULT 0,
                FOREIGN KEY (aluno_id) REFERENCES alunos(id)
            )
        ''')

        # Índices para melhor performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registros_data ON registros(data_hora)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_registros_aluno ON registros(aluno_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alunos_matricula ON alunos(matricula)')

        self.conn.commit()

    # ==================== OPERAÇÕES COM ALUNOS ====================

    def inserir_aluno(self, aluno: Aluno) -> int:
        """Insere um novo aluno no banco de dados"""
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO alunos (matricula, nome, turma, face_encoding, ativo, foto_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                aluno.matricula,
                aluno.nome,
                aluno.turma,
                aluno.face_encoding,
                1 if aluno.ativo else 0,
                aluno.foto_path
            ))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise ValueError(f"Matrícula {aluno.matricula} já existe no sistema")

    def atualizar_aluno(self, aluno: Aluno) -> bool:
        """Atualiza dados de um aluno existente"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE alunos
            SET nome = ?, turma = ?, face_encoding = ?, ativo = ?, foto_path = ?
            WHERE id = ?
        ''', (
            aluno.nome,
            aluno.turma,
            aluno.face_encoding,
            1 if aluno.ativo else 0,
            aluno.foto_path,
            aluno.id
        ))
        self.conn.commit()
        return cursor.rowcount > 0

    def buscar_aluno_por_id(self, aluno_id: int) -> Optional[Aluno]:
        """Busca um aluno pelo ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,))
        row = cursor.fetchone()

        if row:
            return self._row_to_aluno(row)
        return None

    def buscar_aluno_por_matricula(self, matricula: str) -> Optional[Aluno]:
        """Busca um aluno pela matrícula"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM alunos WHERE matricula = ?', (matricula,))
        row = cursor.fetchone()

        if row:
            return self._row_to_aluno(row)
        return None

    def listar_alunos_ativos(self) -> List[Aluno]:
        """Lista todos os alunos ativos"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM alunos WHERE ativo = 1 ORDER BY nome')

        return [self._row_to_aluno(row) for row in cursor.fetchall()]

    def listar_todos_alunos(self) -> List[Aluno]:
        """Lista todos os alunos (ativos e inativos)"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM alunos ORDER BY nome')

        return [self._row_to_aluno(row) for row in cursor.fetchall()]

    def desativar_aluno(self, aluno_id: int) -> bool:
        """Desativa um aluno (soft delete)"""
        cursor = self.conn.cursor()
        cursor.execute('UPDATE alunos SET ativo = 0 WHERE id = ?', (aluno_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def _row_to_aluno(self, row) -> Aluno:
        """Converte uma linha do banco para objeto Aluno"""
        return Aluno(
            id=row['id'],
            matricula=row['matricula'],
            nome=row['nome'],
            turma=row['turma'],
            face_encoding=row['face_encoding'],
            ativo=bool(row['ativo']),
            data_cadastro=datetime.fromisoformat(row['data_cadastro']) if row['data_cadastro'] else None,
            foto_path=row['foto_path']
        )

    # ==================== OPERAÇÕES COM REGISTROS ====================

    def inserir_registro(self, registro: Registro) -> int:
        """Insere um novo registro de entrada/saída"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO registros (aluno_id, tipo, data_hora, confianca, manual)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            registro.aluno_id,
            registro.tipo,
            registro.data_hora or datetime.now(),
            registro.confianca,
            1 if registro.manual else 0
        ))
        self.conn.commit()
        return cursor.lastrowid

    def listar_registros_do_dia(self, data: date = None) -> List[Registro]:
        """Lista todos os registros de um dia específico"""
        if data is None:
            data = date.today()

        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT r.*, a.nome as aluno_nome, a.matricula as aluno_matricula, a.turma as aluno_turma
            FROM registros r
            JOIN alunos a ON r.aluno_id = a.id
            WHERE DATE(r.data_hora) = ?
            ORDER BY r.data_hora DESC
        ''', (data.isoformat(),))

        registros = []
        for row in cursor.fetchall():
            reg = Registro(
                id=row['id'],
                aluno_id=row['aluno_id'],
                tipo=row['tipo'],
                data_hora=datetime.fromisoformat(row['data_hora']) if row['data_hora'] else None,
                confianca=row['confianca'],
                manual=bool(row['manual']),
                aluno_nome=row['aluno_nome'],
                aluno_matricula=row['aluno_matricula'],
                aluno_turma=row['aluno_turma']
            )
            registros.append(reg)

        return registros

    def contar_registros_hoje(self) -> dict:
        """Conta entradas e saídas do dia"""
        cursor = self.conn.cursor()
        hoje = date.today().isoformat()

        cursor.execute('''
            SELECT tipo, COUNT(*) as total
            FROM registros
            WHERE DATE(data_hora) = ?
            GROUP BY tipo
        ''', (hoje,))

        resultado = {'entrada': 0, 'saida': 0}
        for row in cursor.fetchall():
            resultado[row['tipo']] = row['total']

        return resultado

    def ultimo_registro_aluno(self, aluno_id: int) -> Optional[Registro]:
        """Retorna o último registro de um aluno"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT r.*, a.nome as aluno_nome, a.matricula as aluno_matricula, a.turma as aluno_turma
            FROM registros r
            JOIN alunos a ON r.aluno_id = a.id
            WHERE r.aluno_id = ?
            ORDER BY r.data_hora DESC
            LIMIT 1
        ''', (aluno_id,))

        row = cursor.fetchone()
        if row:
            return Registro(
                id=row['id'],
                aluno_id=row['aluno_id'],
                tipo=row['tipo'],
                data_hora=datetime.fromisoformat(row['data_hora']) if row['data_hora'] else None,
                confianca=row['confianca'],
                manual=bool(row['manual']),
                aluno_nome=row['aluno_nome'],
                aluno_matricula=row['aluno_matricula'],
                aluno_turma=row['aluno_turma']
            )
        return None

    def close(self):
        """Fecha a conexão com o banco de dados"""
        if self.conn:
            self.conn.close()
