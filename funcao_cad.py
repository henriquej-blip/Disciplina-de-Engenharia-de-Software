from dataclasses import dataclass
import re
import sqlite3


# ==================== MODELO ====================
@dataclass
class usuario:
    nome: str
    cpf: str
    tel: str       
    email: str



# ==================== VALIDAÇÕES ====================
def validar_cpf(cpf: str) -> bool:
    cpf_limpo = "".join(filter(str.isdigit, str(cpf)))
    if len(cpf_limpo) != 11 or cpf_limpo == cpf_limpo[0] * 11:
        return False

    def digito_verificador(digs: str, pesos: range) -> int:
        soma = sum(int(d) * p for d, p in zip(digs, pesos))
        resto = soma % 11
        return 0 if resto < 2 else 11 - resto

    primeiro = digito_verificador(cpf_limpo[:9], range(10, 1, -1))
    segundo = digito_verificador(cpf_limpo[:10], range(11, 1, -1))
    return cpf_limpo[9:] == f"{primeiro}{segundo}"


def formatar_cpf(cpf: str) -> str:
    cpf_limpo = "".join(filter(str.isdigit, str(cpf)))
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"


def validar_email_gmail(email: str) -> bool:
    padrao = r"^[a-zA-Z0-9._%+-]+@gmail\.com$"
    return bool(re.match(padrao, email.strip().lower()))


def formatar_email(email: str) -> str:
    return email.strip().lower()


# ==================== BANCO DE DADOS ====================
class GerenciadorUsuariosDB:
    def __init__(self, caminho: str = "usuarios.db"):
        self._conn = sqlite3.connect(caminho)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                cpf   TEXT PRIMARY KEY,
                nome  TEXT NOT NULL,
                tel   TEXT,
                email TEXT NOT NULL
            )
        """)

    @staticmethod
    def _chave(cpf: str) -> str:
        return "".join(filter(str.isdigit, str(cpf)))

    def cadastrar(self, u: usuario) -> tuple[bool, str]:
        cpf_limpo = self._chave(u.cpf)

        if not validar_cpf(cpf_limpo):
            return False, "CPF inválido."
        if not validar_email_gmail(u.email):
            return False, "E-mail inválido (apenas @gmail.com)."

        try:
            self._conn.execute(
                "INSERT INTO usuarios (cpf, nome, tel, email) VALUES (?, ?, ?, ?)",
                (cpf_limpo, u.nome, u.tel, formatar_email(u.email)),
            )
            self._conn.commit()
            return True, "Usuário cadastrado com sucesso."
        except sqlite3.IntegrityError:
            return False, "CPF já cadastrado."

    def buscar(self, cpf: str) -> usuario | None:
        row = self._conn.execute(
            "SELECT nome, cpf, tel, email FROM usuarios WHERE cpf = ?",
            (self._chave(cpf),),
        ).fetchone()
        if row is None:
            return None
        nome, cpf, tel, email = row
        return usuario(nome, formatar_cpf(cpf), tel, email)

    def excluir(self, cpf: str) -> bool:
        cur = self._conn.execute(
            "DELETE FROM usuarios WHERE cpf = ?",
            (self._chave(cpf),),
        )
        self._conn.commit()
        return cur.rowcount > 0

    def listar(self) -> list[usuario]:
        rows = self._conn.execute(
            "SELECT nome, cpf, tel, email FROM usuarios ORDER BY nome"
        ).fetchall()
        return [usuario(nome, formatar_cpf(cpf), tel, email)
                for nome, cpf, tel, email in rows]

    def fechar(self) -> None:
        self._conn.close()


# ==================== MENU ====================
def menu_cadastrar(g: GerenciadorUsuariosDB) -> None:
    print("\n--- Cadastrar usuário ---")
    nome  = input("Nome: ").strip()
    cpf   = input("CPF: ")
    tel   = input("Telefone: ").strip()
    email = input("E-mail (gmail): ")

    if not nome:
        print("Nome não pode ser vazio.")
        return

    _, msg = g.cadastrar(usuario(nome, cpf, tel, email))
    print(msg)


def menu_buscar(g: GerenciadorUsuariosDB) -> None:
    print("\n--- Buscar usuário ---")
    u = g.buscar(input("CPF: "))
    if u is None:
        print("Usuário não encontrado.")
    else:
        print(f"Nome: {u.nome}")
        print(f"CPF: {u.cpf}")
        print(f"Telefone: {u.tel}")
        print(f"E-mail: {u.email}")


def menu_listar(g: GerenciadorUsuariosDB) -> None:
    print("\n--- Usuários cadastrados ---")
    usuarios = g.listar()
    if not usuarios:
        print("Nenhum usuário cadastrado.")
        return
    for i, u in enumerate(usuarios, 1):
        print(f"{i}. {u.nome} | {u.cpf} | {u.tel} | {u.email}")
    print(f"Total: {len(usuarios)} usuário(s)")


def menu_excluir(g: GerenciadorUsuariosDB) -> None:
    print("\n--- Excluir usuário ---")
    cpf = input("CPF: ")
    u = g.buscar(cpf)
    if u is None:
        print("Usuário não encontrado.")
        return
    print(f"Usuário: {u.nome} ({u.cpf})")
    if input("Confirmar exclusão? [s/N] ").strip().lower() == "s":
        g.excluir(cpf)
        print("Usuário excluído.")
    else:
        print("Operação cancelada.")

def povoar_exemplos(g: GerenciadorUsuariosDB) -> list[str]:
    exemplos = [
        usuario("João Silva", "000.000.001-91", "(11) 99999-0001", "joao.silva@gmail.com"),
        usuario("Maria Souza", "000.000.002-72", "(21) 98888-0002", "maria.souza@gmail.com"),
        usuario("Paulo Lima", "000.000.003-53", "(31) 97777-0003", "paulo.lima@gmail.com"),
    ]
    resultados = []
    for u in exemplos:
        ok, msg = g.cadastrar(u)
        resultados.append(f"{u.nome}: {msg}")
    return resultados


def menu_povoar(g: GerenciadorUsuariosDB) -> None:
    print("\n--- Povoar com exemplos ---")
    for linha in povoar_exemplos(g):
        print(linha)


def main() -> None:
    g = GerenciadorUsuariosDB() 
    opcoes = {
        "1": ("Cadastrar usuário", menu_cadastrar),
        "2": ("Buscar usuário",    menu_buscar),
        "3": ("Listar usuários",   menu_listar),
        "4": ("Excluir usuário",   menu_excluir),
        "5": ("Povoar exemplos",   menu_povoar),
    }

    while True:
        print("\n===== MENU =====")
        for k, (descricao, _) in opcoes.items():
            print(f"{k} - {descricao}")
        print("0 - Sair")

        escolha = input("Opção: ").strip()
        if escolha == 0:
            break

        acao = opcoes.get(escolha)
        if acao is None:
            print("Opção inválida.")
        else:
            acao[1](g)

    g.fechar()
    print("Até mais!")