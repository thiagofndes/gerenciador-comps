from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import uuid
from datetime import datetime
import requests

app = Flask(__name__)
app.secret_key = "chave_super_secreta"
DATA_PATH = "data"

roles = ["TANK", "HEALER", "DPS", "SUPORTE"]
ROLE_COLORS = {
    "TANK": "#1E3A8A",
    "HEALER": "#047857",
    "DPS": "#7F1D1D",
    "SUPORTE": "#78350F"
}

texts = {
    "pt": {
        "title": "🌹 Gerenciador de COMPS - Albion Online",
        "create": "➕ Criar Nova Comp",
        "edit": "✏️ Editar / Visualizar COMPs",
        "comp_name": "Nome da Comp",
        "num_players": "Quantidade de Jogadores",
        "password": "Senha para edição",
        "role": "Função do Jogador",
        "create_btn": "✅ Criar Comp",
        "success": "Comp '{comp}' criada com sucesso!",
        "error": "Você precisa preencher todos os campos obrigatórios.",
        "edit_title": "Editando: {comp} ({num} jogadores)",
        "save": "💾 Salvar Alterações",
        "delete": "🗑️ Excluir COMP",
        "edit_success": "Comp '{comp}' atualizada com sucesso!",
        "delete_success": "Comp '{comp}' excluída com sucesso!",
        "view": "Visualizar",
        "edit_btn": "Editar",
        "no_comp": "Nenhuma comp criada ainda.",
        "password_invalid": "Senha incorreta para esta comp.",
        "enter_password": "Digite a senha para editar esta COMP:"
    }
}

def get_idioma():
    return session.get("idioma", "pt")

def load_comps():
    try:
        with open(os.path.join(DATA_PATH, "comps.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_comps(comps):
    with open(os.path.join(DATA_PATH, "comps.json"), "w", encoding="utf-8") as f:
        json.dump(comps, f, ensure_ascii=False, indent=4)

def load_itens(idioma):
    with open(os.path.join(DATA_PATH, "nomes_itens.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def load_precos():
    try:
        with open(os.path.join(DATA_PATH, "precos_itens.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_precos(precos):
    with open(os.path.join(DATA_PATH, "precos_itens.json"), "w", encoding="utf-8") as f:
        json.dump(precos, f, ensure_ascii=False, indent=4)

def get_item_price(item_id):
    if not item_id:
        return 0

    precos = load_precos()

    if item_id in precos:
        return precos[item_id]

    # Caso não exista, busca na API e salva
    try:
        url = f"https://www.albion-online-data.com/api/v2/stats/prices/{item_id}.json"
        response = requests.get(url, timeout=5)
        data = response.json()
        thetford_q2 = [x for x in data if x["city"] == "Thetford" and x["quality"] == 2]
        medias = [(x["sell_price_min"] + x["sell_price_max"]) / 2 for x in thetford_q2 if x["sell_price_min"] > 0 and x["sell_price_max"] > 0]
        preco_final = round(sum(medias) / len(medias)) if medias else 0
        precos[item_id] = preco_final
        save_precos(precos)
        return preco_final
    except:
        return 0

@app.route("/")
def index():
    idioma = get_idioma()
    comps = load_comps()
    return render_template("index.html", idioma=idioma, texts=texts[idioma], comps=comps)

@app.route("/create", methods=["GET", "POST"])
def create():
    idioma = get_idioma()
    comps = load_comps()
    itens = load_itens(idioma)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        senha = request.form.get("senha", "").strip()
        qtde = request.form.get("qtde")

        if not nome or not senha or not qtde:
            flash(texts[idioma]["error"], "error")
            return redirect(url_for("create"))

        try:
            qtde = int(qtde)
        except:
            flash(texts[idioma]["error"], "error")
            return redirect(url_for("create"))

        jogadores = []
        for i in range(qtde):
            jogadores.append({
                "Role": request.form.get(f"role_{i}"),
                "Arma": request.form.get(f"arma_{i}"),
                "Capuz": request.form.get(f"capuz_{i}"),
                "Peito": request.form.get(f"peito_{i}"),
                "Bota": request.form.get(f"bota_{i}"),
                "Capa": request.form.get(f"capa_{i}"),
                "Comida": request.form.get(f"comida_{i}"),
                "Poção": request.form.get(f"pocao_{i}"),
                "skills_arma": request.form.get(f"skills_arma_{i}", ""),
                "skills_capuz": request.form.get(f"skills_capuz_{i}", ""),
                "skills_peito": request.form.get(f"skills_peito_{i}", ""),
                "skills_bota": request.form.get(f"skills_bota_{i}", "")
            })

        comp_id = str(uuid.uuid4())
        comps[comp_id] = {
            "id": comp_id,
            "nome": nome,
            "senha": senha,
            "qtde_jogadores": qtde,
            "players": jogadores
        }

        save_comps(comps)
        flash(texts[idioma]["success"].format(comp=nome), "success")
        return redirect(url_for("index"))

    return render_template("create.html", idioma=idioma, texts=texts[idioma], roles=roles, itens=itens)

@app.route("/validate_password/<comp_id>", methods=["POST"])
def validate_password(comp_id):
    idioma = get_idioma()
    comps = load_comps()
    senha_input = request.form.get("senha", "").strip()

    if comp_id not in comps or senha_input != comps[comp_id]["senha"]:
        flash(texts[idioma]["password_invalid"], "error")
        return redirect(url_for("index"))

    return redirect(url_for("edit_comp", comp_id=comp_id))

@app.route("/edit/<comp_id>", methods=["GET", "POST"])
def edit_comp(comp_id):
    idioma = get_idioma()
    comps = load_comps()

    if comp_id not in comps:
        flash("Comp não encontrada", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        if "delete" in request.form:
            del comps[comp_id]
            save_comps(comps)
            flash(texts[idioma]["delete_success"].format(comp=comp_id), "success")
            return redirect(url_for("index"))

        qtde = comps[comp_id]["qtde_jogadores"]
        jogadores = []
        for i in range(qtde):
            jogadores.append({
                "Role": request.form.get(f"role_{i}"),
                "Arma": request.form.get(f"arma_{i}"),
                "Capuz": request.form.get(f"capuz_{i}"),
                "Peito": request.form.get(f"peito_{i}"),
                "Bota": request.form.get(f"bota_{i}"),
                "Capa": request.form.get(f"capa_{i}"),
                "Comida": request.form.get(f"comida_{i}"),
                "Poção": request.form.get(f"pocao_{i}"),
                "skills_arma": request.form.get(f"skills_arma_{i}", ""),
                "skills_capuz": request.form.get(f"skills_capuz_{i}", ""),
                "skills_peito": request.form.get(f"skills_peito_{i}", ""),
                "skills_bota": request.form.get(f"skills_bota_{i}", "")
            })

        comps[comp_id]["players"] = jogadores
        descricao_hist = request.form.get("descricao_hist", "").strip()
        if descricao_hist:
            historico = comps[comp_id].get("historico", [])
            historico.append({
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "descricao": descricao_hist
            })
            comps[comp_id]["historico"] = historico

        save_comps(comps)
        flash(texts[idioma]["edit_success"].format(comp=comps[comp_id]["nome"]), "success")
        return redirect(url_for("index"))

    comp = comps[comp_id]
    itens = load_itens(idioma)
    return render_template("edit.html", idioma=idioma, texts=texts[idioma], comp_name=comp["nome"], comp=comp, roles=roles, itens=itens)

@app.route("/view/<comp_id>")
def view_comp(comp_id):
    idioma = get_idioma()
    comps = load_comps()
    itens = load_itens(idioma)

    if comp_id not in comps:
        flash("Comp não encontrada", "error")
        return redirect(url_for("index"))

    comp = comps[comp_id]
    total = 0
    valores_por_jogador = []

    for jogador in comp["players"]:
        total_jogador = sum(get_item_price(jogador.get(slot)) for slot in ["Arma", "Capuz", "Peito", "Bota", "Capa", "Comida", "Poção"] if jogador.get(slot))
        valores_por_jogador.append({
            "role": jogador["Role"],
            "preco": total_jogador,
            "skills_arma": jogador.get("skills_arma", ""),
            "skills_capuz": jogador.get("skills_capuz", ""),
            "skills_peito": jogador.get("skills_peito", ""),
            "skills_bota": jogador.get("skills_bota", "")
        })
        total += total_jogador

    return render_template(
        "view.html",
        idioma=idioma,
        texts=texts[idioma],
        comp_id=comp_id,
        comp=comp,
        preco_total=total,
        valores_por_jogador=valores_por_jogador,
        roles=roles,
        itens=itens,
        colors=ROLE_COLORS
    )

@app.route("/set_language/<lang>")
def set_language(lang):
    session["idioma"] = lang
    return redirect(request.referrer or url_for("index"))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
