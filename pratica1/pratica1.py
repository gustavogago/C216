from pratica1.crud_alunos import (
    atualizar_aluno,
    buscar_aluno,
    cadastrar_aluno,
    excluir_aluno,
    exibir_menu,
    listar_alunos,
)


def main():
    alunos = {}
    contadores = {}

    while True:
        exibir_menu()
        opcao = input("Escolha uma opcao: ").strip()

        if opcao == "1":
            cadastrar_aluno(alunos, contadores)
        elif opcao == "2":
            listar_alunos(alunos)
        elif opcao == "3":
            buscar_aluno(alunos)
        elif opcao == "4":
            atualizar_aluno(alunos, contadores)
        elif opcao == "5":
            excluir_aluno(alunos)
        elif opcao == "0":
            print("Programa encerrado.")
            break
        else:
            print("Opcao invalida. Tente novamente.")


if __name__ == "__main__":
    main()
