import pdfplumber
from tabulate import tabulate
import os
import re

def clean_value(value):
    """
    Remove caracteres inválidos de um valor antes de convertê-lo para float.
    Mantém apenas um ponto decimal, se houver.
    """
    cleaned_value = re.sub(r"[^0-9\.]", "", value)
    if cleaned_value.count(".") > 1:
        parts = cleaned_value.split(".")
        cleaned_value = parts[0] + "." + "".join(parts[1:])
    
    return cleaned_value

def extract_numerical_data(pdf_path):
    numerical_data = {
        "area_mm2": None,
        "energy_consumption_mW": None,
        "performance_TOPS/W": None,
        "performance_pJ/SOP": None,
        "frequency_MHz": None,
        "process_technology_nm": None,
        "other_metrics": []
    }

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Extrair área e converter para mm²
                if "area" in text.lower():
                    if "area" in text:
                        area_value = text.split("area")[1].split()[0]
                        if "mm²" in area_value:
                            cleaned_value = clean_value(area_value.replace("mm²", ""))
                            if cleaned_value:  # Verifica se a string não está vazia
                                numerical_data["area_mm2"] = float(cleaned_value)
                        elif "µm²" in area_value:
                            cleaned_value = clean_value(area_value.replace("µm²", ""))
                            if cleaned_value:
                                numerical_data["area_mm2"] = float(cleaned_value) / 1e6
                        elif "nm²" in area_value:
                            cleaned_value = clean_value(area_value.replace("nm²", ""))
                            if cleaned_value:
                                numerical_data["area_mm2"] = float(cleaned_value) / 1e12

                # Extrair consumo energético e converter para mW
                if "energy consumption" in text.lower():
                    if "energy consumption" in text:
                        energy_value = text.split("energy consumption")[1].split()[0]
                        if "mW" in energy_value:
                            cleaned_value = clean_value(energy_value.replace("mW", ""))
                            if cleaned_value:
                                numerical_data["energy_consumption_mW"] = float(cleaned_value)
                        elif "W" in energy_value:
                            cleaned_value = clean_value(energy_value.replace("W", ""))
                            if cleaned_value:
                                numerical_data["energy_consumption_mW"] = float(cleaned_value) * 1000
                        elif "µW" in energy_value:
                            cleaned_value = clean_value(energy_value.replace("µW", ""))
                            if cleaned_value:
                                numerical_data["energy_consumption_mW"] = float(cleaned_value) / 1000

                # Extrair performance (TOPS/W, pJ/SOP)
                if "TOPS/W" in text:
                    performance_value = text.split("TOPS/W")[0].split()[-1]
                    cleaned_value = clean_value(performance_value)
                    if cleaned_value:
                        numerical_data["performance_TOPS/W"] = float(cleaned_value)
                if "pJ/SOP" in text:
                    performance_value = text.split("pJ/SOP")[0].split()[-1]
                    cleaned_value = clean_value(performance_value)
                    if cleaned_value:
                        numerical_data["performance_pJ/SOP"] = float(cleaned_value)

                # Extrair frequência de operação e converter para MHz
                if "frequency" in text.lower():
                    if "frequency" in text:
                        freq_value = text.split("frequency")[1].split()[0]
                        if "GHz" in freq_value:
                            cleaned_value = clean_value(freq_value.replace("GHz", ""))
                            if cleaned_value:
                                numerical_data["frequency_MHz"] = float(cleaned_value) * 1000
                        elif "MHz" in freq_value:
                            cleaned_value = clean_value(freq_value.replace("MHz", ""))
                            if cleaned_value:
                                numerical_data["frequency_MHz"] = float(cleaned_value)
                        elif "kHz" in freq_value:
                            cleaned_value = clean_value(freq_value.replace("kHz", ""))
                            if cleaned_value:
                                numerical_data["frequency_MHz"] = float(cleaned_value) / 1000

                # Extrair tecnologia do processo (em nm)
                if "process technology" in text.lower():
                    if "process technology" in text:
                        process_value = text.split("process technology")[1].split()[0]
                        if "nm" in process_value:
                            cleaned_value = clean_value(process_value.replace("nm", ""))
                            if cleaned_value:
                                numerical_data["process_technology_nm"] = float(cleaned_value)

                # Outras métricas (exemplo: energy-delay product)
                if "energy-delay product" in text.lower():
                    if "energy-delay product" in text:
                        edp_value = text.split("energy-delay product")[1].split()[0]
                        numerical_data["other_metrics"].append(f"energy-delay product: {edp_value}")

    return numerical_data

def process_pdfs_in_folder(folder_path):
    # Lista para armazenar os dados de todos os PDFs
    all_data = []

    # Usar os.walk para percorrer recursivamente a pasta e subpastas
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                print(f"Processando arquivo: {pdf_path}")
                data = extract_numerical_data(pdf_path)
                all_data.append((pdf_path, data))

    return all_data

def save_tables_to_file(all_data, output_file="tables_info.txt"):
    with open(output_file, "w") as f:
        for pdf_path, data in all_data:
            f.write(f"Arquivo: {pdf_path}\n")
            table_data = []
            for key, value in data.items():
                if isinstance(value, list):
                    table_data.append([key, "\n".join(value)])
                else:
                    table_data.append([key, value])
            f.write(tabulate(table_data, headers=["Metric", "Value"], tablefmt="pretty"))
            f.write("\n\n")

def main():

    print("\n Iniciando artigos do Arxiv")

    folder_path = "./arxiv_pdfs/"
    all_data = process_pdfs_in_folder(folder_path)

    # Exibir as tabelas no terminal
    for pdf_path, data in all_data:
        print(f"Arquivo: {pdf_path}")
        table_data = []
        for key, value in data.items():
            if isinstance(value, list):
                table_data.append([key, "\n".join(value)])
            else:
                table_data.append([key, value])
        print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="pretty"))
        print("\n")

    save_tables_to_file(all_data, "tables_arx.txt")
    
    print("\n Iniciando artigos do IEEE")
    
    folder_path = "./ieee_pdfs/"
    all_data = process_pdfs_in_folder(folder_path)

    # Exibir as tabelas no terminal
    for pdf_path, data in all_data:
        print(f"Arquivo: {pdf_path}")
        table_data = []
        for key, value in data.items():
            if isinstance(value, list):
                table_data.append([key, "\n".join(value)])
            else:
                table_data.append([key, value])
        print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="pretty"))
        print("\n")

    save_tables_to_file(all_data, "tables_ieee.txt")

if __name__ == "__main__":
    main()