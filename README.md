Script de Limpeza de PVs

Script Python que localiza Persistent Volumes (PVs) com status Released ou Failed no OpenShift, exibe todos para revisão, e apaga automaticamente apenas os que estão em Failed, com confirmação manual antes da exclusao

Python 3 instalado
CLI oc (OpenShift) instalado e configurado

Para rodar :

python3 SCRIPT_PYTHON.py --dry-run (mostra os pvs que podem ser apagados mas sem apagar de verdade)
python3 SCRIPT_PYTHON.py (roda o comando de verdade mas com uma confirmação)

Ao rodar, o script vai: 

Mostrar os PVs Released/Failed
Mostrar quais Failed serão apagados
Pedir confirmação:
