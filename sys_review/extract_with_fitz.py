import fitz  # PyMuPDF
from tabulate import tabulate
import os
import re

def clean_value(value):
    cleaned_value = re.sub(r"[^0-9\.]+", "", value)
    return cleaned_value if cleaned_value else None

def extract_numerical_data(pdf_path):
    numerical_data = {
        "area_mm2": None,
        "energy_consumption_mW": None,
        "performance_TOPS/W": None,
        "performance_pJ/SOP": None,
        "frequency_MHz": None,
        "process_technology_nm": None
    }

    doc = fitz.open(pdf_path)  # Abre o PDF com PyMuPDF
    for page in doc:
        text = page.get_text("text")  # Extrai o texto da página
        if text:
            match_area = re.search(r"(\d+\.?\d*)\s*(mm²|µm²|um²|nm²|mm2|µm2|um2|nm2)", text, re.IGNORECASE)
            if match_area:
                value, unit = match_area.groups()
                value = float(value)
                if unit == "µm²" or unit == "um²":
                    value /= 1e6
                elif unit == "nm²":
                    value /= 1e12
                numerical_data["area_mm2"] = value

            match_energy = re.search(r"(\d+\.?\d*)\s*(mW|W|µW)", text, re.IGNORECASE)
            if match_energy:
                value, unit = match_energy.groups()
                value = float(value)
                if unit == "W":
                    value *= 1000
                elif unit == "µW" or unit == "uW":
                    value /= 1000
                numerical_data["energy_consumption_mW"] = value
                
            match_tops = re.search(r"(\d+\.?\d*)\s*(TOPS/W)", text, re.IGNORECASE)
            if match_tops:
                value, unit = match_tops.groups()
                value = float(value)
                numerical_data["performance_TOPS/W"] = value
                
            match_pj = re.search(r"(\d+\.?\d*)\s*(pJ/SOP)", text, re.IGNORECASE)
            if match_pj:
                value, unit = match_pj.groups()
                value = float(value)
                numerical_data["performance_pj/SOP"] = value
                
            match_frequency = re.search(r"(\d+\.?\d*)\s*(GHz|MHz|kHz)", text, re.IGNORECASE)
            if match_frequency:
                value, unit = match_frequency.groups()
                value = float(value)
                if unit == "GHz":
                    value *= 1000
                elif unit == "kHz":
                    value /= 1000
                numerical_data["frequency_MHz"] = value

            match_process = re.search(r"(\d+\.?\d*)\s*nm", text, re.IGNORECASE)
            if match_process:
                numerical_data["process_technology_nm"] = float(match_process.group(1))

    return numerical_data

def process_pdfs_in_folder(folder_path):
    all_data = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(root, filename)
                print(f"Processando arquivo: {pdf_path}")
                data = extract_numerical_data(pdf_path)
                all_data.append((filename, data))
    return all_data

def save_consolidated_table(all_data, output_file):
    headers = ["Artigo", "Área (mm²)", "Consumo de Energia (mW)", "Performance (TOPS/W)",
               "Energia / op.sinaptica (pJ/SOP)", "Frequência (MHz)", "Tecnologia do Processo (nm)"]
    table_data = []
    for filename, data in all_data:
        row = [
            filename,
            data.get("area_mm2", "N/A"),
            data.get("energy_consumption_mW", "N/A"),
            data.get("performance_TOPS/W", "N/A"),
            data.get("performance_pJ/SOP", "N/A"),
            data.get("frequency_MHz", "N/A"),
            data.get("process_technology_nm", "N/A")
        ]
        table_data.append(row)

    table_data.sort(key=lambda x: x[2] if isinstance(x[2], (int, float)) else float('-inf'), reverse=True)

    with open(output_file, "w") as f:
        f.write(tabulate(table_data, headers=headers, tablefmt="pretty"))
        f.write("\n")

def main():
    folder_path  = "./database"
    output_table = 'table_gpt_ieee.txt'
    all_data = process_pdfs_in_folder(folder_path)
    save_consolidated_table(all_data, output_table)
    print("Tabela consolidada salva em", output_table)

if __name__ == "__main__":
    main()