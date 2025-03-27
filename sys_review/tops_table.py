import re
import pandas as pd
from tabulate import tabulate

def extract_tops_values(text_file):
    """Extrai valores numéricos associados a TOPS, TOPS/W e área (mm²) de um arquivo de texto."""
    with open(text_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    data = []
    current_file = None
    
    for line in lines:
        if line.startswith("Arquivo: "):
            current_file = line.strip().replace("Arquivo: ", "")
        
        match_tops = re.findall(r"(\d+\.?\d*)\s*(TOPS/W)", line, re.IGNORECASE)
        match_area = re.findall(r"(\d+\.?\d*)\s*mm2", line, re.IGNORECASE)
        area_value = float(match_area[0][0]) if match_area else None
        
        if match_tops and current_file:
            for value, unit in match_tops:
                data.append((current_file, f"{float(value)} {unit}", area_value))
    
    return data

def save_to_txt(data, output_file):
    """Salva os dados extraídos em um arquivo TXT formatado com tabulate, gerando tabelas separadas para área e TOPS/W."""
    df = pd.DataFrame(data, columns=["Arquivo", "TOPS/W", "Área (mm²)"])
    df = df.loc[df.groupby("Arquivo")["TOPS/W"].idxmax()]
    
    df_tops_w = df[df["TOPS/W"].notna()].sort_values(by=["TOPS/W"], ascending=False)
    df_area   = df.dropna(subset=["Área (mm²)"]).sort_values(by=["Área (mm²)"], ascending=False)
    
    table_tops_w = tabulate(df_tops_w, headers='keys', tablefmt='double_grid', showindex=False)
    table_area   = tabulate(df_area,   headers='keys', tablefmt='double_grid', showindex=False)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Tabela para TOPS/W:\n")
        f.write(table_tops_w + "\n\n")
        f.write("Tabela para Área (mm²):\n")
        f.write(table_area + "\n")
    
    print(f"Tabelas salvas em {output_file}")

if __name__ == "__main__":
    input_file = "info.txt"        # Arquivo de entrada
    output_txt = "info_table.txt"  # Arquivo de saída
    
    tops_data = extract_tops_values(input_file)
    save_to_txt(tops_data, output_txt)
