import json
import os
import requests

# Caminho fixo do seu projeto
DATA_PATH = r"D:\PROGRAMAÇÃO\gerenciador_comps\data"
IDIOMA = "pt"  # ou "en", "es"

def load_itens():
    with open(os.path.join(DATA_PATH, "nomes_itens.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def save_precos(precos):
    with open(os.path.join(DATA_PATH, "precos_itens.json"), "w", encoding="utf-8") as f:
        json.dump(precos, f, ensure_ascii=False, indent=4)

def get_item_price(item_id):
    try:
        url = f"https://www.albion-online-data.com/api/v2/stats/prices/{item_id}.json"
        response = requests.get(url, timeout=5)
        data = response.json()
        thetford_q2 = [x for x in data if x["city"] == "Thetford" and x["quality"] == 2]
        medias = [(x["sell_price_min"] + x["sell_price_max"]) / 2 for x in thetford_q2 if x["sell_price_min"] > 0 and x["sell_price_max"] > 0]
        return round(sum(medias) / len(medias)) if medias else 0
    except Exception as e:
        print(f"Erro ao buscar preço para {item_id}: {e}")
        return 0

def main():
    print("Iniciando atualização de preços...")
    itens = load_itens()
    precos = {}
    count = 0

    for item_id in itens.keys():
        # Lixo que não queremos
        if any(sub in item_id for sub in ["ARTEFACT", "UNIQUE", "QUESTITEM", "TOKEN", "EVENT", "TOOL", 
                                          "SET1", "FARM", "@", "SKILLBOOK", "FISH", "MOUNT"]):
            continue

        # Armas
        if "2H" in item_id or "MAIN_" in item_id:
            if "T8" in item_id:  # só T8 armas
                count += 1
                print(f"[{count}] Arma → {item_id}")
                precos[item_id] = get_item_price(item_id)
            continue

        # Capuz
        if "HEAD" in item_id and "T8" in item_id:
            count += 1
            print(f"[{count}] Capuz → {item_id}")
            precos[item_id] = get_item_price(item_id)
            continue

        # Peito
        if "ARMOR" in item_id and "T8" in item_id:
            count += 1
            print(f"[{count}] Peito → {item_id}")
            precos[item_id] = get_item_price(item_id)
            continue

        # Botas
        if "SHOES" in item_id and "T8" in item_id:
            count += 1
            print(f"[{count}] Bota → {item_id}")
            precos[item_id] = get_item_price(item_id)
            continue

        # Capas
        if "CAPE" in item_id and "T8" in item_id:
            count += 1
            print(f"[{count}] Capa → {item_id}")
            precos[item_id] = get_item_price(item_id)
            continue

        # Comidas
        if "MEAL" in item_id and ("T7" in item_id or "T8" in item_id):
            count += 1
            print(f"[{count}] Comida → {item_id}")
            precos[item_id] = get_item_price(item_id)
            continue

        # Poções
        if "POTION" in item_id and ("T7" in item_id or "T8" in item_id):
            count += 1
            print(f"[{count}] Poção → {item_id}")
            precos[item_id] = get_item_price(item_id)
            continue

    save_precos(precos)
    print(f"\n✅ Atualização concluída! {len(precos)} preços salvos em precos_itens.json.")

if __name__ == "__main__":
    main()
