import re

# Caminho do arquivo de entrada e saída
input_file = "README.md"
output_file = "neuro_links.txt"

# Expressão regular para encontrar links
link_pattern = re.compile(r'https?://[\w./?=&%-]+')

# Lê o arquivo e extrai os links
with open(input_file, "r", encoding="utf-8") as f:
    content = f.read()
    links = link_pattern.findall(content)

# Salva os links em um arquivo de saída
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(links))

print(f"Arquivo '{output_file}' criado com {len(links)} links.")