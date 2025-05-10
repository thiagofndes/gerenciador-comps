import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# Caminho para o arquivo JSON
with open("data/itens_db_t8_completo.json", "r", encoding="utf-8") as f:
    data = json.load(f)

itens = data["pt"]  # você pode testar também "en" ou "es"

# Valida a existência da imagem
def validar_item(nome_e_id):
    nome, item_id = nome_e_id
    url = f"https://render.albiononline.com/v1/item/{item_id}.png"
    try:
        response = requests.head(url, timeout=5)
        if response.status_code != 200:
            return nome, item_id
    except:
        return nome, item_id
    return None

# Lista de itens a validar
lista_itens = list(itens.items())

print("🔎 Validando itens... (pode levar até 1 minuto)")

# Executa em paralelo com 20 threads
erros = []
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(validar_item, item) for item in lista_itens]
    for future in as_completed(futures):
        resultado = future.result()
        if resultado:
            erros.append(resultado)

# Resultado final
if erros:
    print(f"\n⚠️ {len(erros)} itens com erro:\n")
    for nome, item_id in erros:
        print(f"{nome} → {item_id}")
else:
    print("✅ Todos os itens foram validados com sucesso!")
