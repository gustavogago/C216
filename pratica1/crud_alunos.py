def exibir_menu():
    print("\n=== CRUD DE ALUNOS ===")
    print("1. Cadastrar aluno")
    print("2. Listar alunos")
    print("3. Buscar aluno por matricula")
    print("4. Atualizar aluno")
    print("5. Excluir aluno")
    print("0. Sair")


def ler_texto(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor:
            return valor
        print("Campo obrigatorio. Tente novamente.")


def ler_email(mensagem):
    while True:
        email = input(mensagem).strip()
        if "@" in email and "." in email:
            return email
        print("Email invalido. Tente novamente.")


def ler_curso(mensagem):
    while True:
        curso = input(mensagem).strip().upper()
        if curso:
            return curso
        print("Curso obrigatorio. Tente novamente.")


def gerar_matricula(curso, contadores):
    if curso not in contadores:
        contadores[curso] = 0

    contadores[curso] += 1
    return f"{curso}{contadores[curso]}"


def exibir_aluno(aluno):
    print(f"Matricula: {aluno['matricula']}")
    print(f"Nome: {aluno['nome']}")
    print(f"Email: {aluno['email']}")
    print(f"Curso: {aluno['curso']}")


def cadastrar_aluno(alunos, contadores):
    print("\n=== CADASTRO DE ALUNO ===")
    nome = ler_texto("Nome: ")
    email = ler_email("Email: ")
    curso = ler_curso("Curso: ")
    matricula = gerar_matricula(curso, contadores)

    alunos[matricula] = {
        "nome": nome,
        "email": email,
        "curso": curso,
        "matricula": matricula,
    }

    print(f"Aluno cadastrado com sucesso. Matricula gerada: {matricula}")


def listar_alunos(alunos):
    print("\n=== LISTA DE ALUNOS ===")
    if not alunos:
        print("Nenhum aluno cadastrado.")
        return

    for aluno in alunos.values():
        exibir_aluno(aluno)
        print("-" * 30)


def buscar_aluno(alunos):
    print("\n=== BUSCAR ALUNO ===")
    matricula = input("Digite a matricula do aluno: ").strip().upper()

    aluno = alunos.get(matricula)
    if aluno is None:
        print("Aluno nao encontrado.")
        return

    exibir_aluno(aluno)


def atualizar_aluno(alunos, contadores):
    print("\n=== ATUALIZAR ALUNO ===")
    matricula = input("Digite a matricula do aluno: ").strip().upper()

    aluno = alunos.get(matricula)
    if aluno is None:
        print("Aluno nao encontrado.")
        return

    novo_nome = input(f"Novo nome [{aluno['nome']}]: ").strip()
    novo_email = input(f"Novo email [{aluno['email']}]: ").strip()
    novo_curso = input(f"Novo curso [{aluno['curso']}]: ").strip().upper()

    if novo_nome:
        aluno["nome"] = novo_nome

    if novo_email:
        if "@" not in novo_email or "." not in novo_email:
            print("Email invalido. Atualizacao de email cancelada.")
        else:
            aluno["email"] = novo_email

    if novo_curso and novo_curso != aluno["curso"]:
        nova_matricula = gerar_matricula(novo_curso, contadores)
        aluno["curso"] = novo_curso
        aluno["matricula"] = nova_matricula
        alunos[nova_matricula] = aluno
        del alunos[matricula]
        print(f"Curso atualizado. Nova matricula: {nova_matricula}")
        return

    print("Aluno atualizado com sucesso.")


def excluir_aluno(alunos):
    print("\n=== EXCLUIR ALUNO ===")
    matricula = input("Digite a matricula do aluno: ").strip().upper()

    if matricula in alunos:
        del alunos[matricula]
        print("Aluno excluido com sucesso.")
    else:
        print("Aluno nao encontrado.")
