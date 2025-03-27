import os
import fitz  # PyMuPDF
import time
import re
from tabulate import tabulate

#======================================================================================================
# File:     extract_phrases.py 
# Author:   Lucas Farias Martins
# Contennt: Extrai informações de frases que contenham os termos de interesse e formata corretamente.
#           Filtra frases contendo citações acadêmicas, mantém apenas frases com números (exceto aqueles 
#           isolados entre colchetes, como [8]) e evita que abreviações como "Fig. 1" sejam divididas.
#------------------------------------------------------------------------------------------------------
# Lista de termos para buscar (altere aqui)
#
"""
TERMOS_DE_INTERESSE = ["TOPS/W", "Mixed", "mixed"
                       "area", 
                       "frequency", 
                       "power", "energy",
                       "MNIST", "Caltech", "ImageNet", "CIFAR-10", "CIFAR-100", "TIDIGIT", "ResNet", "VGG"] # BASES DE DADOS"""
#======================================================================================================

TERMOS_DE_INTERESSE = ["STDP", "RSTDP", "BP-STDP",
                       "e-prop", "eprop",
                       "Hebbian",
                       "LSM",
                       "Feedback Alignment",
                       "Spike-Frequency Adaptation", "spike-frequency adaptation",
                       "ReSuMe",
                       "Surrogate Gradient", "surrogate gradient"]

def extract_info(pdf_path):
    """
    Extrai informações de frases que contenham os termos de interesse e formata corretamente.
    Filtra frases contendo citações acadêmicas e mantém apenas frases com números.
    """
    doc = fitz.open(pdf_path)
    texto_completo = ""
    for page in doc:
        texto_completo += " " + page.get_text("text")
    
    # Remove quebras de linha e divide o texto em frases
    texto_completo = re.sub(r'-\n+', '', texto_completo)
    frases = re.split(r'(?<=[.;])\s+(?!\d)', texto_completo.strip())

    info = []
    for frase in frases:
        frase = frase.strip() # Remove espaços extras
        #frase = re.sub(r'\[\d+\]', '', frase).strip() # Remove citações numéricas entre colchetes ([8] ou [12])
        if not any(termo in frase for termo in TERMOS_DE_INTERESSE):
            continue # Verifica se a frase contém termos de interesse
        if not re.search(r'\d', frase):
            continue # Verifica se a frase contém números
        if re.search(r"\w+ et al\.,?", frase) or re.search(r"(IEEE|ACM|Nature|Springer|Elsevier|Symp\.)", frase, re.IGNORECASE):
            continue # Filtra frases que parecem ser citações acadêmicas
        info.append(frase)

    return info

def save_to_txt(pdf_path, info, output_dir):
    """
    Salva as informações extraídas em um arquivo TXT com frases completas.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_file = os.path.join(output_dir, f"{pdf_name}.txt")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-" * 50 + "\n")
        f.write(f"Arquivo: {pdf_path}\n")
        f.write("-" * 50 + "\n\n")
        for phrase in info:
            f.write(f"{phrase}\n\n")
    
    print(f" |-- {pdf_name}.txt")

def process_directory(directory, output_dir):
    """
    Processa todos os arquivos PDF em um diretório.
    """
    cont_termos = {termo: 0 for termo in TERMOS_DE_INTERESSE}
    print("Arquivos gerados:\n |")
    
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(directory, filename)
            info = extract_info(pdf_path)
            if info:
                save_to_txt(pdf_path, info, output_dir)
                for phrase in info:
                    for termo in TERMOS_DE_INTERESSE:
                        if termo in phrase:
                            cont_termos[termo] += 1
                            break
    
    return cont_termos

####=============================================================================####
##                            __  ___  ___     ____  _  __                         ##
##                           /  |/  / / _ |   /  _/ / |/ /                         ##
##                          / /|_/ / / __ |  _/ /  /    /                          ##
##                         /_/  /_/ /_/ |_| /___/ /_/|_/                           ##
####=============================================================================####

if __name__ == "__main__":
    
    print("  _____  _                           ______      _                  _             ")
    print(" |  __ \| |                         |  ____|    | |                | |            ")
    print(" | |__) | |__  _ __ __ _ ___  ___   | |__  __  _| |_ _ __ __ _  ___| |_ ___  _ __ ")
    print(" |  ___/| '_ \| '__/ _` / __|/ _ \  |  __| \ \/ / __| '__/ _` |/ __| __/ _ \| '__|")
    print(" | |    | | | | | | (_| \__ \  __/  | |____ >  <| |_| | | (_| | (__| || (_) | |   ")
    print(" |_|    |_| |_|_|  \__,_|___/\___|  |______/_/\_\___|_|  \__,_|\___|\__\___/|_|   ")     
    print("\n" + "="*80 + "\n")

    #---------- PATHS and TIMING PARAMETERS -------
    directory  = "./database"
    output_dir = "./output_learning"
    
    #--------------------------- Processing -------
    start_time   = time.time()
    cont_termos  = process_directory(directory, output_dir)
    end_time     = time.time()
    elapsed_time = end_time - start_time

    #tabela_resumo = [["Termo", "Ocorrências"], *[[termo, contagem] for termo, contagem in cont_termos.items()], ["Tempo total de execução", f"{elapsed_time:.2f} seg"]]
    tabela_resumo = [["Termo", "Ocorrências"]] + [[termo, contagem] for termo, contagem in cont_termos.items() if contagem > 0] + [["Tempo total de execução", f"{elapsed_time:.2f} seg"]]
    print("\nResumo da execução:")
    print(tabulate(tabela_resumo, headers="firstrow", tablefmt="double_grid"))
