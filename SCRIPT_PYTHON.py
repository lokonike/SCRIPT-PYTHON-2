import subprocess #pra rodar comandos de terminal
import argparse   #para ler o que digitei no terminal

#guarda os status que quero exibir e apagar
STATUS_EXIBIR = ["Released", "Failed"]
STATUS_APAGAR = ["Failed"] 

def listar_pvs():
    cmd = ["oc", "get", "pv"]
    resultado = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )

    if resultado.returncode != 0:
        print(f"Erro ao rodar 'oc get pv': {resultado.stderr.strip()}")
        return []
    linhas = resultado.stdout.strip().split("\n") #pega o texto e quebra em lista de linhas 
    return linhas


def filtrar_pvs(linhas, status_exibir):
    pvs_encontrados = []

    for linha in linhas[1:]: #pula a primeira linha (cabeçalho)
        if not linha.strip():  # Ignora linhas vazias
            continue

        colunas = linha.split()
        if len(colunas) < 5: #se tiver menos de 5 colunas, ignora a linha
            continue # pula linhas que nao tem colunas suficientes

        nome = colunas[0] #nome dos pv
        status = colunas[4] #colunas de status 

        if status in status_exibir:  #Se o status da linha estiver na lista status_exibir passada como parametro, guarda (nome, status) na lista de resultados
            pvs_encontrados.append((nome, status)) 
    return pvs_encontrados

#função para rodar e apagar os pvs que estão na lista de resultados
def apagar_pv(nome): 
    cmd = ["oc", "delete", "pv", nome]
    resultado = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True
    )

    if resultado.returncode == 0:
        return True, resultado.stdout.strip()
    else:
        return False, resultado.stderr.strip()

def main():
    parser = argparse.ArgumentParser(
        description="Mostra PVs com os status Released e Failed, e apaga PVs com status Failed."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mostra os PVs que seriam apagados, sem apagar eles",
    )
    args = parser.parse_args()

    print("Buscando PVs com status: Released ou Failed ...\n")

#Chama a função que roda oc get pv, se vier vazia, imprime mensagem de erro e retorna
    linhas = listar_pvs()
    if not linhas:
        print("Nao foi possivel obter a lista de PVs")
        return

    #Filtra os PVs que estão em Released OU Failed, se nao achar ele encerra
    pvs_exibicao = filtrar_pvs(linhas, STATUS_EXIBIR)
    if not pvs_exibicao:
        print("Nenhum PV com esse status foi encontrado")
        return

#Mostra todos na tela (Released e Failed), pra revisar
    print(f"Encontrados {len(pvs_exibicao)} PV(s):")
    for nome, status in pvs_exibicao:
        print(f"- {nome} (Status: {status})")

#Lista reduzida para EXCLUSAO: somente Failed

    pvs_apagar = [(nome, status) for nome, status in pvs_exibicao if status in STATUS_APAGAR]

    #e não tiver nenhum Failed, para por aqui
    if not pvs_apagar:
        print("\nNenhum PV com status 'Failed' para apagar, nada apagado")

        return
    #Mostra especificamente quais serão apagados
    print(f"\nDesses, {len(pvs_apagar)} estao em Failed e serao apagados:")
    for nome, status in pvs_apagar:
        print(f"- {nome} (Status: {status})")
    #--dry-run foi usada, para aqui — não apaga nada, só mostrou o que faria.
    if args.dry_run:
        print("\nDry run ativado, nenhum PV sera apagado.")
        return

    print()
    confirmacao = input(
        f"Confirma a exclusao desses {len(pvs_apagar)} PV(s) em Failed? ... Digite 'sim' para continuar: "
    )

    #Pede confirmação manual digitando "sim" (case-insensitive, por causa do .lower()).
    if confirmacao.strip().lower() != "sim":
        print("Cancelado pelo usuario. Nenhum PV foi apagado.")
        return

    #
    print()
    sucesso = 0
    falha = 0

    for nome, status in pvs_apagar:
        print(f"Apagando {nome} ({status})... ", end="", flush=True)
        ok, msg = apagar_pv(nome)
        if ok:
            print(f"OK -> {msg}")
            sucesso += 1
        else:
            print(f"FALHOU -> {msg}")
            falha += 1
 
    print(f"\nTotal: {sucesso} apagado(s), {falha} falharam")
 
 
if __name__ == "__main__":
    main()