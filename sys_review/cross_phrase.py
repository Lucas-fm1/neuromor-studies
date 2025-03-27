import os
import re
from tabulate import tabulate

#=================================================================
"""
database = ["e-prop", "CIFAR10", "CIFAR100", "CIFAR-100", 
            "N-MNIST", "Fashion MNIST", "N-TIDIGIT",
            "ImageNet", "TinyImageNet", "Tiny-ImageNet"]

network  = ["ResNet-12", "ResNet-18", "ResNet-50",
            "VGG5", "VGG8", "VGG-8", "VGG-11", "VGG16", "VGG-16"]
"""

database = ["Hebbian"]
network  = [""]

#=================================================================

def encontrar_combinacoes(texto):
    combinacoes = []
    for db in database:
        for net in network:
            if re.search(rf'\b{db}\b.*\b{net}\b|\b{net}\b.*\b{db}\b', texto, re.IGNORECASE):
                combinacoes.append((db, net))
    return combinacoes

#=================================================================

#diretorio  = 'output_database'
diretorio  = 'output_learning'
resultados = set()

# Dentro do loop, adicione as combinações como tuplas ao conjunto
for nome_arquivo in os.listdir(diretorio):
    if nome_arquivo.endswith('.txt'):
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            texto = arquivo.read()
            combinacoes = encontrar_combinacoes(texto)
            for db, net in combinacoes:
                resultados.add((nome_arquivo.replace('.txt', ''), db, net))  # Adiciona tuplas ao conjunto

# Converte o conjunto de volta para uma lista para exibição
resultados = list(resultados)

#=================================================================
#               Exibe os resultados em uma tabela
#=================================================================

print("      _       _        _                                         _                      _     ")
print("     | |     | |      | |                       _               | |                    | |    ")
print("   __| | __ _| |_ __ _| |__   __ _ ___  ___   _| |_   _ __   ___| |___      ___ __ ___ | | __ ")
print("  / _` |/ _` | __/ _` | '_ \ / _` / __|/ _ \ |_   _| | '_ \ / _ \ __\ \ /\ / / '__/ _ \| |/ / ")
print(" | (_| | (_| | || (_| | |_) | (_| \__ \  __/   |_|   | | | |  __/ |_ \ V  V /| | | (_) |   <  ")
print("  \__,_|\__,_|\__\__,_|_.__/ \__,_|___/\___|         |_| |_|\___|\__| \_/\_/ |_|  \___/|_|\_\ ")

print("\n"+"="*100)
print(tabulate(resultados, headers=["ARTIGO", "DATABASE", "NETWORK"], tablefmt="fancy_grid"))

#=================================================================


results = {}

# Percorre todos os arquivos no diretório
for nome_arquivo in os.listdir(diretorio):
    if nome_arquivo.endswith('.txt'):
        caminho_arquivo = os.path.join(diretorio, nome_arquivo)
        with open(caminho_arquivo, 'r', encoding='utf-8') as arquivo:
            texto = arquivo.read()
            combinacoes = encontrar_combinacoes(texto)
            for db, net in combinacoes:
                chave = f"{db} + {net}"  # Cria a chave no formato "Database + Network"
                if chave not in results:
                    results[chave] = set()  # Usa um conjunto para evitar arquivos duplicados
                results[chave].add(nome_arquivo.replace('.txt', ''))  # Adiciona o arquivo sem a extensão

print("\n" + "-"*50 + "\n")
# Exibe os results no formato desejado
for combinacao, arquivos in results.items():
    print(f"{combinacao}:")
    for arquivo in arquivos:
        print(f"  {arquivo}")
    print()  # Linha em branco para separar as combinações
