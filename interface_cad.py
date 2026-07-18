import tkinter as tk
from tkinter import messagebox

from funcao_cad import GerenciadorUsuariosDB, usuario, povoar_exemplos


class CadastroApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Cadastro de Usuários")
        self.root.geometry("520x520")
        self.root.resizable(False, False)

        self.db = GerenciadorUsuariosDB()

        self._criar_widgets()

    def _criar_widgets(self) -> None:
        frame = tk.Frame(self.root, padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Nome:", anchor="w").grid(row=0, column=0, sticky="w")
        self.nome_entry = tk.Entry(frame, width=40)
        self.nome_entry.grid(row=0, column=1, pady=4, sticky="w")

        tk.Label(frame, text="CPF:", anchor="w").grid(row=1, column=0, sticky="w")
        self.cpf_entry = tk.Entry(frame, width=40)
        self.cpf_entry.grid(row=1, column=1, pady=4, sticky="w")

        tk.Label(frame, text="Telefone:", anchor="w").grid(row=2, column=0, sticky="w")
        self.tel_entry = tk.Entry(frame, width=40)
        self.tel_entry.grid(row=2, column=1, pady=4, sticky="w")

        tk.Label(frame, text="E-mail (gmail):", anchor="w").grid(row=3, column=0, sticky="w")
        self.email_entry = tk.Entry(frame, width=40)
        self.email_entry.grid(row=3, column=1, pady=4, sticky="w")

        botao_frame = tk.Frame(frame)
        botao_frame.grid(row=4, column=0, columnspan=2, pady=12)

        tk.Button(botao_frame, text="Cadastrar", width=12, command=self.cadastrar).grid(row=0, column=0, padx=4)
        tk.Button(botao_frame, text="Buscar", width=12, command=self.buscar).grid(row=0, column=1, padx=4)
        tk.Button(botao_frame, text="Listar", width=12, command=self.listar).grid(row=0, column=2, padx=4)
        tk.Button(botao_frame, text="Excluir", width=12, command=self.excluir).grid(row=0, column=3, padx=4)

        tk.Button(frame, text="Povoar exemplos", width=52, command=self.povoar).grid(row=5, column=0, columnspan=2, pady=6)

        self.status_label = tk.Label(frame, text="Pronto.", fg="#1f5f1f", anchor="w")
        self.status_label.grid(row=6, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.output_text = tk.Text(frame, width=62, height=14, wrap="none", state="disabled")
        self.output_text.grid(row=7, column=0, columnspan=2, pady=4)

        self.scrollbar = tk.Scrollbar(frame, command=self.output_text.yview)
        self.scrollbar.grid(row=7, column=2, sticky="ns", pady=4)
        self.output_text.configure(yscrollcommand=self.scrollbar.set)

    def _atualizar_status(self, mensagem: str, erro: bool = False) -> None:
        self.status_label.config(text=mensagem, fg="#a00" if erro else "#1f5f1f")

    def _limpar_mensagem(self) -> None:
        self.status_label.config(text="Pronto.", fg="#1f5f1f")

    def _mostrar_output(self, texto: str) -> None:
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, texto)
        self.output_text.configure(state="disabled")

    def cadastrar(self) -> None:
        nome = self.nome_entry.get().strip()
        cpf = self.cpf_entry.get().strip()
        tel = self.tel_entry.get().strip()
        email = self.email_entry.get().strip()

        if not nome:
            self._atualizar_status("Nome não pode ser vazio.", erro=True)
            return

        ok, msg = self.db.cadastrar(usuario(nome, cpf, tel, email))
        self._atualizar_status(msg, erro=not ok)
        if ok:
            self._mostrar_output(f"Cadastrado: {nome} | {cpf} | {tel} | {email}")

    def buscar(self) -> None:
        cpf = self.cpf_entry.get().strip()
        if not cpf:
            self._atualizar_status("Informe o CPF para buscar.", erro=True)
            return

        resultado = self.db.buscar(cpf)
        if resultado is None:
            self._mostrar_output("Usuário não encontrado.")
            self._atualizar_status("Usuário não encontrado.", erro=True)
        else:
            self._mostrar_output(
                f"Nome: {resultado.nome}\nCPF: {resultado.cpf}\nTelefone: {resultado.tel}\nE-mail: {resultado.email}"
            )
            self._atualizar_status("Busca concluída.")

    def listar(self) -> None:
        usuarios = self.db.listar()
        if not usuarios:
            self._mostrar_output("Nenhum usuário cadastrado.")
            self._atualizar_status("Nenhum usuário encontrado.", erro=True)
            return

        linhas = [f"{i+1}. {u.nome} | {u.cpf} | {u.tel} | {u.email}" for i, u in enumerate(usuarios)]
        self._mostrar_output("\n".join(linhas))
        self._atualizar_status(f"{len(usuarios)} usuário(s) listados.")

    def excluir(self) -> None:
        cpf = self.cpf_entry.get().strip()
        if not cpf:
            self._atualizar_status("Informe o CPF para excluir.", erro=True)
            return

        usuario_excluido = self.db.buscar(cpf)
        if usuario_excluido is None:
            self._mostrar_output("Usuário não encontrado.")
            self._atualizar_status("Usuário não encontrado.", erro=True)
            return

        if messagebox.askyesno("Excluir usuário", f"Excluir {usuario_excluido.nome} ({usuario_excluido.cpf})?"):
            self.db.excluir(cpf)
            self._mostrar_output(f"Usuário excluído: {usuario_excluido.nome}")
            self._atualizar_status("Usuário excluído com sucesso.")
        else:
            self._atualizar_status("Exclusão cancelada.")

    def povoar(self) -> None:
        resultados = povoar_exemplos(self.db)
        self._mostrar_output("\n".join(resultados))
        self._atualizar_status("Povoamento concluído.")

    def fechar(self) -> None:
        self.db.fechar()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    app = CadastroApp(root)
    root.protocol("WM_DELETE_WINDOW", app.fechar)
    root.mainloop()
