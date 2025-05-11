from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

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
        # GERAL
        "title": "🌹 Gerenciador de COMPS - Albion Online",

        # CAMPOS DO INDEX
        "create": "➕ Criar Nova Comp",
        "edit": "✏️ Editar / Visualizar COMPs",
        "view": "Visualizar",
        "no_comp": "Nenhuma comp criada ainda.",
        "enter_password": "Senha para edição",
        "edit_btn": "Editar",

        # CAMPOS DO VIEW
        "view_title": "Visualizando '{comp}' com {num} jogadores",

        # CAMPOS DO CREATE
        "comp_name": "Nome da Comp",
        "password": "Senha para edição",
        "num_players": "Quantidade de Jogadores",
        "create_btn": "Criar",
        "role": "Função do Jogador",

        # MENSAGENS DE SISTEMA
        "error": "Preencha todos os campos corretamente.",
        "success": "Comp '{comp}' criada com sucesso!",
        "password_invalid": "Senha inválida.",
        "delete_success": "Comp '{comp}' deletada com sucesso.",
        "edit_success": "Comp '{comp}' atualizada com sucesso.",

        # CAMPOS DO LOOT SPLIT
        "loot_split_title": "Loot Split",
        "participant_count": "Quantidade de Participantes:",
        "participant_label": "Nome do Participante",
        "participant_placeholder": "Participante",
        "total_loot_value": "Valor Total do Loot (silver):",
        "repair_cost": "Custo com Reparos (silver):",
        "calculate_btn": "Calcular Split",
        "fill_all_fields": "Por favor, preencha todos os campos corretamente.",
        "fill_name_field": "Por favor, preencha o nome do Participante {num}.",
        "result_liquid_value": "Valor Líquido",
        "result_guild_tax": "Taxa da Guilda (10%)",
        "result_division_value": "Valor para Dividir",
        "result_value_per_player": "Valor por Jogador",
        "result_chest_distribution": "Distribuição dos Baús"
    },
    "en": {
        # GENERAL
        "title": "🌹 COMPS Manager - Albion Online",

        # INDEX FIELDS
        "create": "➕ Create New Comp",
        "edit": "✏️ Edit / View COMPs",
        "view": "View",
        "no_comp": "No comps created yet.",
        "enter_password": "Password to edit",
        "edit_btn": "Edit",

        # VIEW FIELDS
        "view_title": "Viewing '{comp}' with {num} players",

        # CREATE FIELDS
        "comp_name": "Comp Name",
        "password": "Password",
        "num_players": "Number of Players",
        "create_btn": "Create",
        "role": "Player Role",

        # SYSTEM MESSAGES
        "error": "Please fill in all fields correctly.",
        "success": "Comp '{comp}' created successfully!",
        "password_invalid": "Invalid password.",
        "delete_success": "Comp '{comp}' successfully deleted.",
        "edit_success": "Comp '{comp}' updated successfully.",

        # LOOT SPLIT FIELDS
        "loot_split_title": "Loot Split",
        "participant_count": "Number of Participants:",
        "participant_label": "Participant Name",
        "participant_placeholder": "Participant",
        "total_loot_value": "Total Loot Value (silver):",
        "repair_cost": "Repair Cost (silver):",
        "calculate_btn": "Calculate Split",
        "fill_all_fields": "Please fill in all fields correctly.",
        "fill_name_field": "Please enter the name of Participant {num}.",
        "result_liquid_value": "Net Value",
        "result_guild_tax": "Guild Tax (10%)",
        "result_division_value": "Value to Split",
        "result_value_per_player": "Value per Player",
        "result_chest_distribution": "Chest Distribution"
    },
    "es": {
        # GENERAL
        "title": "🌹 Administrador de COMPS - Albion Online",

        # INDEX FIELDS
        "create": "➕ Crear Nueva Comp",
        "edit": "✏️ Editar / Ver COMPs",
        "view": "Ver",
        "no_comp": "No se han creado comps.",
        "enter_password": "Contraseña para editar",
        "edit_btn": "Editar",

        # VIEW FIELDS
        "view_title": "Viendo '{comp}' con {num} jugadores",

        # CREATE FIELDS
        "comp_name": "Nombre de la Comp",
        "password": "Contraseña",
        "num_players": "Cantidad de Jugadores",
        "create_btn": "Crear",
        "role": "Rol del Jugador",

        # SYSTEM MESSAGES
        "error": "Por favor completa todos los campos correctamente.",
        "success": "Comp '{comp}' creada exitosamente!",
        "password_invalid": "Contraseña inválida.",
        "delete_success": "Comp '{comp}' eliminada exitosamente.",
        "edit_success": "Comp '{comp}' actualizada exitosamente.",

        # LOOT SPLIT FIELDS
        "loot_split_title": "Loot Split",
        "participant_count": "Cantidad de Participantes:",
        "participant_label": "Nombre del Participante",
        "participant_placeholder": "Participante",
        "total_loot_value": "Valor Total del Botín (silver):",
        "repair_cost": "Costo de Reparación (silver):",
        "calculate_btn": "Calcular Split",
        "fill_all_fields": "Por favor, completa todos los campos correctamente.",
        "fill_name_field": "Por favor, ingresa el nombre del Participante {num}.",
        "result_liquid_value": "Valor Neto",
        "result_guild_tax": "Impuesto de la Guilda (10%)",
        "result_division_value": "Valor a Dividir",
        "result_value_per_player": "Valor por Jugador",
        "result_chest_distribution": "Distribución de Cofres"
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
                "pocao": request.form.get(f"pocao_{i}"),
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
                "pocao": request.form.get(f"pocao_{i}"),
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
    for jogador in comp["players"]:
        preco_jogador = 0
        for slot in ["Arma", "Capuz", "Peito", "Bota", "Capa", "Comida", "pocao"]:
            item_id = jogador.get(slot)
            if item_id:
                preco_jogador += get_item_price(item_id)
        jogador["preco"] = preco_jogador
        total += preco_jogador
    return render_template("view.html", idioma=idioma, texts=texts[idioma], comp_id=comp_id, comp=comp, preco_total=total, roles=roles, itens=itens, colors=ROLE_COLORS)

@app.route("/loot_split")
def loot_split():
    idioma = get_idioma()
    return render_template("loot_split.html", idioma=idioma, texts=texts[idioma])

@app.route("/set_language/<lang>")
def set_language(lang):
    session["idioma"] = lang
    return redirect(request.referrer or url_for("index"))


DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1370991835111227463/GwJ_wu5mGcvE0DYTXSizBTsZnXLJcsO6nm32J-cly2jeCpwJerk3lGYIqxrLCIbBmGL1"

@app.route("/enviar_discord", methods=["POST"])
def enviar_discord():
    return #Desativado por Romero.
    data = request.get_json()
    evento_id = data.get("evento_id")
    id_canal = data.get("id_canal")

    if not evento_id or not id_canal:
        return jsonify({"error": "Dados incompletos"}), 400

    payload = {
        "content": f"🚨 <@&1368258045968121887> Loot Split Evento: {evento_id}\n➡️ Clique <#{id_canal}> para acessar o canal.",
        "username": "Loot Split",
        "allowed_mentions": {
            "parse": ["users", "roles"]
        }
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            return jsonify({"success": True}), 200
        else:
            return jsonify({"error": f"Erro Discord: {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
