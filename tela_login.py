# tela_login.py
import os
import bcrypt
from datetime import timedelta
from flask import Flask, request, redirect, url_for, render_template, flash, session, jsonify
from jinja2 import DictLoader

# sua conexão
from conexao import conectar_banco, testar_conexao, HOST, USER, DATABASE

# importa e registra o blueprint da área logada
import tela_inicial

# ---------------- Templates do login (e base) ----------------
TEMPLATES = {
    "base.html": """
<!doctype html><html lang="pt-br"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title or "Controle de Coletores" }}</title>
<style>
 html,body{margin:0;padding:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu;background:#0e1117;color:#e6edf3}
 .wrap{max-width:1000px;margin:0 auto;padding:24px}
 .card{background:#161b22;border:1px solid #30363d;border-radius:14px;padding:20px}
 .btn{display:inline-block;padding:10px 14px;border-radius:10px;border:1px solid #30363d;background:#238636;color:#fff;text-decoration:none;cursor:pointer}
 .btn.secondary{background:#21262d}
 .btn.block{display:block;width:100%;text-align:center}
 input,select{width:100%;padding:10px;border-radius:10px;border:1px solid #30363d;background:#0d1117;color:#e6edf3}
 input[readonly]{opacity:.85}
 label{display:block;margin:10px 0 6px}
 .row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
 .mt8{margin-top:8px}.mt12{margin-top:12px}.mt16{margin-top:16px}
 .flex{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
 .right{margin-left:auto}
 .muted{color:#8b949e}
 .alert{padding:10px 12px;border-radius:10px;border:1px solid #30363d;margin:8px 0}
 .alert.ok{background:#132d19;border-color:#1f6f3f}
 .alert.err{background:#2a1618;border-color:#8b3434}
 a{color:#58a6ff}
</style>
</head><body>
<div class="wrap">
  <div class="flex">
    <h2 class="mb0">{{ header or "Controle de Coletores" }}</h2>
    <div class="right">
      {% if session.get('user') %}
        <a href="{{ url_for('web.home_web') }}">Início</a>
        <a href="{{ url_for('web.logout') }}">Sair</a>
      {% else %}
        <a href="{{ url_for('login') }}">Login</a>
        <a href="{{ url_for('web.cadastro_publico') }}">Cadastrar usuário</a>
      {% endif %}
    </div>
  </div>

  {% with msgs = get_flashed_messages(with_categories=true) %}
    {% if msgs %}
      {% for cat,msg in msgs %}
        <div class="alert {{ 'ok' if cat=='ok' else 'err' }}">{{ msg }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}

  <div class="card">{% block content %}{% endblock %}</div>
  <p class="muted mt12">Base: {{ dbname }} · Host: {{ host }} · Usuário DB: {{ dbuser }}</p>
</div>
</body></html>
""",
    "login.html": """
{% extends "base.html" %}
{% block content %}
<form method="post" id="frmLogin" autocomplete="off">
  <label>Matrícula</label>
  <input id="matricula" name="matricula" required autofocus>

  <label class="mt8">Nome</label>
  <input id="nome_preview" readonly placeholder="— preenchido automaticamente —">

  <div class="row mt8">
    <div>
      <label>Cargo</label>
      <input id="cargo_preview" readonly placeholder="— preenchido automaticamente —">
    </div>
    <div>
      <label>CD</label>
      <input id="cd_preview" readonly placeholder="— preenchido automaticamente —">
    </div>
  </div>

  <label class="mt12">Senha</label>
  <input type="password" name="senha" required>

  <button class="btn block mt16" type="submit">Entrar</button>
</form>

<div class="flex mt12">
  <a class="btn secondary" href="{{ url_for('web.cadastro_publico') }}">Cadastrar usuário</a>
</div>

<div class="muted mt16">{{ conn_status }}</div>

<script>
 const elMat=document.getElementById('matricula');
 const elNome=document.getElementById('nome_preview');
 const elCargo=document.getElementById('cargo_preview');
 const elCD=document.getElementById('cd_preview');
 async function lookup(mat){
   if(!mat){elNome.value='';elCargo.value='';elCD.value='';return;}
   try{
     const r=await fetch(`{{ url_for('api_usuario') }}?matricula=${encodeURIComponent(mat)}`);
     if(!r.ok) return;
     const d=await r.json();
     if(d&&d.ok&&d.usuario){
       elNome.value=d.usuario.nome||'';
       elCargo.value=d.usuario.funcao||'';
       elCD.value=d.usuario.area||'';
     }else{elNome.value='';elCargo.value='';elCD.value='';}
   }catch(e){elNome.value='';elCargo.value='';elCD.value='';}
 }
 elMat.addEventListener('blur',e=>lookup(e.target.value.trim()));
 elMat.addEventListener('keyup',e=>{const v=e.target.value.trim(); if(v.length>=2) lookup(v);});
</script>
{% endblock %}
"""
}

# ---------------- App/Login ----------------
app = Flask(__name__)
app.jinja_loader = DictLoader(TEMPLATES)
app.secret_key = os.environ.get("APP_SECRET", "changeme-uma-chave-segura")
app.permanent_session_lifetime = timedelta(hours=12)

# registra o blueprint da área logada (tela_inicial)
tela_inicial.register_app(app)  # adiciona rotas /web, /reservar, /devolver, /cadastro, /cadastro-usuarios

def query_one(sql, params=()):
    conn = conectar_banco(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params); row = cur.fetchone()
    cur.close(); conn.close(); return row

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        try: conn_status = testar_conexao()
        except Exception as e: conn_status = f"❌ Erro ao testar conexão: {e}"
        return render_template("login.html", title="Login", header="Login",
                               conn_status=conn_status, dbname=DATABASE, host=HOST, dbuser=USER)

    matricula = (request.form.get("matricula") or "").strip()
    senha = request.form.get("senha") or ""
    if not matricula or not senha:
        flash("Informe matrícula e senha.", "err"); return redirect(url_for("login"))

    row = query_one("""
        SELECT id_usuario, matricula, nome, funcao, area, perfil, ativo, senha_hash
        FROM usuarios
        WHERE deletado_em IS NULL AND matricula = %s
        LIMIT 1
    """, (matricula,))
    if not row or int(row.get("ativo", 0)) != 1:
        flash("Matrícula inexistente ou usuário inativo.", "err"); return redirect(url_for("login"))

    ok = False
    try: ok = bcrypt.checkpw(senha.encode("utf-8"), (row.get("senha_hash") or "").encode("utf-8"))
    except Exception: ok = False
    if not ok:
        flash("Senha inválida.", "err"); return redirect(url_for("login"))

    session.permanent = True
    session["user"] = {"id_usuario": row["id_usuario"], "matricula": row["matricula"], "nome": row["nome"], "perfil": row["perfil"]}
    flash("Login realizado com sucesso.", "ok")
    return redirect(url_for("web.home_web"))

@app.route("/api/usuario")
def api_usuario():
    mat = (request.args.get("matricula") or "").strip()
    if not mat: return jsonify({"ok": False, "erro": "matricula requerida"}), 400
    row = query_one("""
        SELECT id_usuario, matricula, nome, area, turno, funcao, perfil, ativo
        FROM usuarios WHERE deletado_em IS NULL AND matricula=%s LIMIT 1
    """, (mat,))
    if not row: return jsonify({"ok": True, "exists": False, "usuario": None})
    return jsonify({"ok": True, "exists": True, "usuario": row})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=True)
