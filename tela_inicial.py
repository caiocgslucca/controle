# tela_inicial.py
import bcrypt
import csv
import io
from datetime import datetime, timezone
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, make_response, jsonify
from jinja2 import DictLoader
from conexao import conectar_banco, HOST, USER, DATABASE

web = Blueprint("web", __name__)

# ---------------- Templates ----------------
WEB_TEMPLATES = {
    # ====== HOME ======
    "home_web.html": """
{% extends "base.html" %}
{% block content %}
<style>
  body .wrap{max-width:unset;margin:0 16px;}
  .grid2{display:grid;grid-template-columns:1.3fr 1.7fr;gap:20px;align-items:start}
  .panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}
  .panel h3{margin:4px 0 10px 0}
  .scrollbox-disp,.scrollbox-uso{height:78vh;overflow-y:scroll;overflow-x:auto;scrollbar-gutter:stable;border:1px solid #30363d;border-radius:10px}
  table{width:100%;border-collapse:collapse;table-layout:fixed}
  thead th{position:sticky;top:0;background:#161b22;border-bottom:1px solid #30363d;z-index:3}
  thead tr.filters th{top:34px;background:#0f1420;z-index:2}
  th,td{border-bottom:1px solid #30363d;padding:8px 10px;text-align:left;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .filters input{width:100%;padding:6px;border-radius:8px;border:1px solid #30363d;background:#0e1117;color:#e6edf3;font-size:13px}
  .muted{color:#8b949e}
  .actions{display:flex;gap:12px;margin-bottom:12px;align-items:center;flex-wrap:wrap}
  #tblDisp{width:max(700px,100%);} #tblDisp.compact th,#tblDisp.compact td{padding:6px 8px;font-size:13px}
  #tblDisp th:nth-child(1),#tblDisp td:nth-child(1){width:34%}
  #tblDisp th:nth-child(2),#tblDisp td:nth-child(2){width:33%}
  #tblDisp th:nth-child(3),#tblDisp td:nth-child(3){width:33%}
  #tblUso{width:max(1200px,100%);}
  #tblUso th:nth-child(1), #tblUso td:nth-child(1){width:13%}
  #tblUso th:nth-child(2), #tblUso td:nth-child(2){width:13%}
  #tblUso th:nth-child(3), #tblUso td:nth-child(3){width:13%}
  #tblUso th:nth-child(4), #tblUso td:nth-child(4){width:10%}
  #tblUso th:nth-child(5), #tblUso td:nth-child(5){width:18%}
  #tblUso th:nth-child(6), #tblUso td:nth-child(6){width:11%}
  #tblUso th:nth-child(7), #tblUso td:nth-child(7){width:9%}
  #tblUso th:nth-child(8), #tblUso td:nth-child(8){width:8%}
  #tblUso th:nth-child(9), #tblUso td:nth-child(9){width:17%}
  #tblUso th:nth-child(10),#tblUso td:nth-child(10){width:8%}
  @media (max-width:1200px){.grid2{grid-template-columns:1fr}.scrollbox-disp,.scrollbox-uso{height:65vh}}
</style>

<div class="actions">
  <a class="btn" href="{{ url_for('web.reservar') }}">Reservar Coletor</a>
  <a class="btn secondary" href="{{ url_for('web.devolver') }}">Devolver Coletor</a>
  <a class="btn secondary" href="{{ url_for('web.manutencao') }}">Manutenção</a>
  <a class="btn secondary" href="{{ url_for('web.coletores_list') }}">Coletores</a>
  <a class="btn secondary" href="{{ url_for('web.usuarios_list') }}">Usuários</a>
  <span class="muted">Logado como: {{ user.nome }} ({{ user.matricula }}) · Perfil: {{ user.perfil }}</span>
</div>

<div class="grid2">
  <div class="panel">
    <h3>Coletores Disponíveis</h3>
    <div class="scrollbox-disp">
      <table id="tblDisp" class="compact">
        <thead>
          <tr><th>Número</th><th>Modelo</th><th>Serial</th></tr>
          <tr class="filters">
            <th><input placeholder="Filtro Número" oninput="filterTable('tblDisp',0,this.value)"></th>
            <th><input placeholder="Filtro Modelo" oninput="filterTable('tblDisp',1,this.value)"></th>
            <th><input placeholder="Filtro Serial" oninput="filterTable('tblDisp',2,this.value)"></th>
          </tr>
        </thead>
        <tbody>
        {% for c in disponiveis %}
          <tr>
            <td title="{{ c.numero_coletor }}">{{ c.numero_coletor }}</td>
            <td title="{{ c.tipo_equipamento }}">{{ c.tipo_equipamento }}</td>
            <td title="{{ c.serial }}">{{ c.serial }}</td>
          </tr>
        {% endfor %}
        {% if not disponiveis %}
          <tr><td colspan="3" class="muted">Sem coletores disponíveis.</td></tr>
        {% endif %}
        </tbody>
      </table>
    </div>
  </div>

  <div class="panel">
    <h3>Coletores em Uso</h3>
    <div class="scrollbox-uso">
      <table id="tblUso">
        <thead>
          <tr>
            <th>Número</th><th>Modelo</th><th>Serial</th>
            <th>Matrícula</th><th>Nome</th><th>Cargo</th><th>Setor</th>
            <th>Turno</th><th>Data Hora Retirado</th><th>Tempo em Uso</th>
          </tr>
          <tr class="filters">
            <th><input placeholder="Filtro Número" oninput="filterTable('tblUso',0,this.value)"></th>
            <th><input placeholder="Filtro Modelo" oninput="filterTable('tblUso',1,this.value)"></th>
            <th><input placeholder="Filtro Serial" oninput="filterTable('tblUso',2,this.value)"></th>
            <th><input placeholder="Filtro Matrícula" oninput="filterTable('tblUso',3,this.value)"></th>
            <th><input placeholder="Filtro Nome" oninput="filterTable('tblUso',4,this.value)"></th>
            <th><input placeholder="Filtro Cargo" oninput="filterTable('tblUso',5,this.value)"></th>
            <th><input placeholder="Filtro Setor" oninput="filterTable('tblUso',6,this.value)"></th>
            <th><input placeholder="Filtro Turno" oninput="filterTable('tblUso',7,this.value)"></th>
            <th><input placeholder="Filtro Data" oninput="filterTable('tblUso',8,this.value)"></th>
            <th><input placeholder="Filtro Tempo" oninput="filterTable('tblUso',9,this.value)"></th>
          </tr>
        </thead>
        <tbody>
        {% for r in em_uso %}
          <tr>
            <td>{{ r.numero_coletor }}</td>
            <td>{{ r.tipo_equipamento }}</td>
            <td>{{ r.serial }}</td>
            <td>{{ r.matricula }}</td>
            <td>{{ r.nome }}</td>
            <td>{{ r.funcao or '' }}</td>
            <td>{{ r.area or '' }}</td>
            <td>{{ r.turno or '' }}</td>
            <td>{{ r.dt_hora_retirada_fmt }}</td>
            <td>{{ r.tempo_em_uso }}</td>
          </tr>
        {% endfor %}
        {% if not em_uso %}
          <tr><td colspan="10" class="muted">Nenhum coletor em uso no momento.</td></tr>
        {% endif %}
        </tbody>
      </table>
    </div>
  </div>
</div>

<script>
function filterTable(tableId, colIndex, query){
  const q=(query||"").toLowerCase();
  const rows=document.querySelectorAll("#"+tableId+" tbody tr");
  rows.forEach(tr=>{
    const td=tr.querySelectorAll("td")[colIndex];
    if(!td){return;}
    const text=(td.innerText||"").toLowerCase();
    tr.style.display = text.includes(q) ? "" : "none";
  });
}
</script>
{% endblock %}
""",

    # ====== COLETORES ======
    "coletores_list.html": """
{% extends "base.html" %}
{% block content %}
<style>
  .panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}
  .actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
  .muted{color:#8b949e}
  .scroll{max-height:78vh;overflow:auto;border:1px solid #30363d;border-radius:10px}
  table{width:100%;border-collapse:collapse;table-layout:fixed}
  thead th{position:sticky;top:0;background:#161b22;border-bottom:1px solid #30363d;z-index:3}
  thead tr.filters th{top:34px;background:#0f1420;z-index:2}
  th,td{border-bottom:1px solid #30363d;padding:8px 10px;text-align:left;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .filters input{width:100%;padding:6px;border-radius:8px;border:1px solid #30363d;background:#0e1117;color:#e6edf3;font-size:13px}
  a.btn.sm{padding:6px 10px;font-size:13px}
</style>

<div class="actions">
  <a class="btn" href="{{ url_for('web.coletores_novo') }}">Cadastrar Coletor</a>
  <a class="btn secondary" href="{{ url_for('web.coletores_importar') }}">Importar CSV</a>
  <a class="btn secondary" href="{{ url_for('web.coletores_exportar_modelo') }}">Exportar Modelo CSV</a>
  <a class="btn secondary" href="{{ url_for('web.coletores_exportar_banco') }}">Exportar Coletores (CSV)</a>
  <a class="btn secondary" href="{{ url_for('web.home_web') }}">Voltar</a>
  <span class="muted">Total: {{ coletores|length }}</span>
</div>

<div class="panel">
  <div class="scroll">
    <table id="tblCol">
      <thead>
        <tr>
          <th>CD</th><th>Número</th><th>Serial</th><th>Modelo</th><th>Status</th><th>Ações</th>
        </tr>
        <tr class="filters">
          <th><input placeholder="Filtrar CD" oninput="f(0,this.value)"></th>
          <th><input placeholder="Filtrar Número" oninput="f(1,this.value)"></th>
          <th><input placeholder="Filtrar Serial" oninput="f(2,this.value)"></th>
          <th><input placeholder="Filtrar Modelo" oninput="f(3,this.value)"></th>
          <th><input placeholder="Filtrar Status" oninput="f(4,this.value)"></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
      {% for c in coletores %}
        <tr>
          <td>{{ c.cd }}</td>
          <td>{{ c.numero_coletor }}</td>
          <td>{{ c.serial }}</td>
          <td>{{ c.tipo_equipamento }}</td>
          <td>{{ c.status }}</td>
          <td><a class="btn sm" href="{{ url_for('web.coletores_editar', coletor_id=c.id) }}">Editar</a></td>
        </tr>
      {% endfor %}
      {% if not coletores %}<tr><td colspan="6" class="muted">Nenhum coletor cadastrado.</td></tr>{% endif %}
      </tbody>
    </table>
  </div>
</div>

<script>
function f(col, q){
  const rows=document.querySelectorAll("#tblCol tbody tr");
  const s=(q||"").toLowerCase();
  rows.forEach(tr=>{
    const td=tr.querySelectorAll("td")[col];
    if(!td) return;
    tr.style.display = (td.innerText||"").toLowerCase().includes(s) ? "" : "none";
  });
}
</script>
{% endblock %}
""",

    "coletores_form.html": """
{% extends "base.html" %}
{% block content %}
<style>.panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}.row{display:flex;gap:16px;flex-wrap:wrap}.row > div{min-width:260px;flex:1}input,select{width:100%}</style>
<div class="panel">
  <h3>{{ 'Editar Coletor' if coletor else 'Cadastrar Coletor' }}</h3>
  <form method="post">
    <div class="row">
      <div><label>CD</label><input name="cd" value="{{ coletor.cd if coletor else '' }}" required></div>
      <div><label>Número do Coletor</label><input name="numero_coletor" value="{{ coletor.numero_coletor if coletor else '' }}" required></div>
    </div>
    <div class="row">
      <div><label>Serial</label><input name="serial" value="{{ coletor.serial if coletor else '' }}" required></div>
      <div><label>Modelo</label><input name="tipo_equipamento" value="{{ coletor.tipo_equipamento if coletor else '' }}" required></div>
    </div>
    <div class="row">
      <div>
        <label>Status</label>
        <select name="status" required>
          {% set st = coletor.status if coletor else 'DISPONIVEL' %}
          {% for s in ['DISPONIVEL','EM_USO','MANUTENCAO','INATIVO'] %}
          <option value="{{ s }}" {{ 'selected' if s==st else '' }}>{{ s }}</option>
          {% endfor %}
        </select>
      </div>
    </div>
    <div class="row">
      <div><button class="btn" type="submit">Salvar</button></div>
      <div><a class="btn secondary" href="{{ url_for('web.coletores_list') }}">Cancelar</a></div>
    </div>
  </form>
</div>
{% endblock %}
""",

    "coletores_importar.html": """
{% extends "base.html" %}
{% block content %}
<style>.panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}.muted{color:#8b949e}ul{margin:8px 0 0 18px}</style>
<div class="panel">
  <h3>Importar Coletores (CSV)</h3>
  <p class="muted">Colunas: <b>cd;numero_coletor;serial;tipo_equipamento</b>. O status será <b>DISPONIVEL</b>.</p>
  <p class="muted">Baixe o <a href="{{ url_for('web.coletores_exportar_modelo') }}">modelo CSV</a>.</p>
  <form method="post" enctype="multipart/form-data">
    <input type="file" name="arquivo" accept=".csv" required>
    <button class="btn" type="submit">Importar</button>
    <a class="btn secondary" href="{{ url_for('web.coletores_list') }}">Voltar</a>
  </form>
  {% if resultado %}
    <hr><p><b>Resultado:</b></p>
    <ul><li>Inseridos: {{ resultado.inseridos }}</li><li>Ignorados (serial duplicado): {{ resultado.ignorados }}</li><li>Erros de linha: {{ resultado.erros }}</li></ul>
  {% endif %}
</div>
{% endblock %}
""",

    # ====== USUÁRIOS (LISTA/FORM/IMPORT) ======
    "usuarios_list.html": """
{% extends "base.html" %}
{% block content %}
<style>
 .panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}
 .actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:10px}
 .scroll{max-height:78vh;overflow:auto;border:1px solid #30363d;border-radius:10px}
 table{width:100%;border-collapse:collapse;table-layout:fixed}
 thead th{position:sticky;top:0;background:#161b22;border-bottom:1px solid #30363d;z-index:3}
 thead tr.filters th{top:34px;background:#0f1420;z-index:2}
 th,td{border-bottom:1px solid #30363d;padding:8px 10px;text-align:left;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .filters input{width:100%;padding:6px;border-radius:8px;border:1px solid #30363d;background:#0e1117;color:#e6edf3}
 a.btn.sm{padding:6px 10px;font-size:13px}
 form.inline{display:inline}
 .muted{color:#8b949e}
</style>

<div class="actions">
  <a class="btn" href="{{ url_for('web.usuarios_novo') }}">Cadastrar Usuário</a>
  <a class="btn secondary" href="{{ url_for('web.usuarios_importar') }}">Importar CSV</a>
  <a class="btn secondary" href="{{ url_for('web.usuarios_exportar_modelo') }}">Exportar Modelo CSV</a>
  <a class="btn secondary" href="{{ url_for('web.usuarios_exportar_banco') }}">Exportar Usuários (CSV)</a>
  <a class="btn secondary" href="{{ url_for('web.home_web') }}">Voltar</a>
  <span class="muted">Total: {{ usuarios|length }}</span>
</div>

<div class="panel">
  <div class="scroll">
    <table id="tblUsu">
      <thead>
        <tr>
          <th>CD</th><th>Matrícula</th><th>Nome</th><th>Área</th><th>Turno</th><th>Cargo</th><th>Perfil</th><th>Ativo</th><th>Ações</th>
        </tr>
        <tr class="filters">
          <th><input placeholder="Filtrar CD" oninput="f(0,this.value)"></th>
          <th><input placeholder="Filtrar Matrícula" oninput="f(1,this.value)"></th>
          <th><input placeholder="Filtrar Nome" oninput="f(2,this.value)"></th>
          <th><input placeholder="Filtrar Área" oninput="f(3,this.value)"></th>
          <th><input placeholder="Filtrar Turno" oninput="f(4,this.value)"></th>
          <th><input placeholder="Filtrar Cargo" oninput="f(5,this.value)"></th>
          <th><input placeholder="Filtrar Perfil" oninput="f(6,this.value)"></th>
          <th><input placeholder="Ativo? (1/0)" oninput="f(7,this.value)"></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
      {% for u in usuarios %}
        <tr>
          <td>{{ u.cd }}</td>
          <td>{{ u.matricula }}</td>
          <td>{{ u.nome }}</td>
          <td>{{ u.area or '' }}</td>
          <td>{{ u.turno or '' }}</td>
          <td>{{ u.funcao or '' }}</td>
          <td>{{ u.perfil }}</td>
          <td>{{ 1 if u.ativo else 0 }}</td>
          <td>
            <a class="btn sm" href="{{ url_for('web.usuarios_editar', id_usuario=u.id_usuario) }}">Editar</a>
            <form class="inline" method="post" action="{{ url_for('web.usuarios_excluir', id_usuario=u.id_usuario) }}" onsubmit="return confirm('Excluir este usuário?');">
              <button class="btn sm secondary" type="submit">Excluir</button>
            </form>
          </td>
        </tr>
      {% endfor %}
      {% if not usuarios %}<tr><td colspan="9" class="muted">Nenhum usuário.</td></tr>{% endif %}
      </tbody>
    </table>
  </div>
</div>

<script>
function f(col,q){
  const s=(q||"").toLowerCase();
  document.querySelectorAll("#tblUsu tbody tr").forEach(tr=>{
    const td=tr.querySelectorAll("td")[col]; if(!td) return;
    tr.style.display=((td.innerText||"").toLowerCase().includes(s))? "":"none";
  });
}
</script>
{% endblock %}
""",

    "usuarios_form.html": """
{% extends "base.html" %}
{% block content %}
<style>.panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}.row{display:flex;gap:16px;flex-wrap:wrap}.row>div{min-width:240px;flex:1}input,select{width:100%}</style>
<div class="panel">
  <h3>{{ 'Editar Usuário' if usuario else 'Cadastrar Usuário' }}</h3>
  <form method="post">
    <div class="row">
      <div><label>CD</label><input name="cd" value="{{ usuario.cd if usuario else '' }}" required></div>
      <div><label>Matrícula</label><input name="matricula" value="{{ usuario.matricula if usuario else '' }}" {{ 'readonly' if usuario else '' }} {{ '' if usuario else 'required' }}></div>
      <div><label>Nome</label><input name="nome" value="{{ usuario.nome if usuario else '' }}" required></div>
    </div>
    <div class="row">
      <div><label>Área</label><input name="area" value="{{ usuario.area if usuario else '' }}"></div>
      <div><label>Turno</label><input name="turno" value="{{ usuario.turno if usuario else '' }}"></div>
      <div><label>Cargo</label><input name="funcao" value="{{ usuario.funcao if usuario else '' }}"></div>
    </div>
    <div class="row">
      <div>
        <label>Perfil</label>
        <select name="perfil" required>
          {% set p = usuario.perfil if usuario else 'USER' %}
          {% for op in ['USER','ADMIN','MASTER'] %}
          <option value="{{ op }}" {{ 'selected' if op==p else '' }}>{{ op }}</option>
          {% endfor %}
        </select>
      </div>
      <div>
        <label>Ativo</label>
        <select name="ativo"><option value="1" {{ 'selected' if (usuario and usuario.ativo) or not usuario else '' }}>Ativo</option><option value="0" {{ 'selected' if usuario and not usuario.ativo else '' }}>Inativo</option></select>
      </div>
      <div><label>Senha {{ '(deixe em branco para manter)' if usuario else '' }}</label><input type="password" name="senha" {{ '' if usuario else 'required' }}></div>
    </div>
    <div class="row">
      <div><button class="btn" type="submit">Salvar</button></div>
      <div><a class="btn secondary" href="{{ url_for('web.usuarios_list') }}">Cancelar</a></div>
    </div>
  </form>
</div>
{% endblock %}
""",

    "usuarios_importar.html": """
{% extends "base.html" %}
{% block content %}
<style>.panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}.muted{color:#8b949e}ul{margin:8px 0 0 18px}</style>
<div class="panel">
  <h3>Importar Usuários (CSV)</h3>
  <p class="muted">Colunas: <b>cd;matricula;nome;area;turno;funcao;perfil;ativo;senha</b>. Obrigatórios: <b>cd;matricula;nome</b>.</p>
  <p class="muted">Se <b>senha</b> faltar, será usado <b>123456</b>. Se <b>perfil</b> faltar, usa <b>USER</b>. Se <b>ativo</b> faltar, usa <b>1</b>.</p>
  <p class="muted">Baixe o <a href="{{ url_for('web.usuarios_exportar_modelo') }}">modelo CSV</a>.</p>
  <form method="post" enctype="multipart/form-data">
    <input type="file" name="arquivo" accept=".csv" required>
    <button class="btn" type="submit">Importar</button>
    <a class="btn secondary" href="{{ url_for('web.usuarios_list') }}">Voltar</a>
  </form>
  {% if resultado %}
    <hr><p><b>Resultado:</b></p>
    <ul><li>Inseridos: {{ resultado.inseridos }}</li><li>Ignorados (matrícula duplicada): {{ resultado.ignorados }}</li><li>Erros de linha: {{ resultado.erros }}</li></ul>
  {% endif %}
</div>
{% endblock %}
""",

    # ====== CADASTRO PÚBLICO ======
    "cadastro_publico.html": """
{% extends "base.html" %}
{% block content %}
  <h3 class="mb0">Cadastro de Usuário</h3>
  <p class="muted mt8">Cria um usuário com perfil <b>USER</b>.</p>
  <form method="post" autocomplete="off">
    <div class="row">
      <div><label>CD</label><input name="cd" required></div>
      <div><label>Matrícula</label><input name="matricula" required></div>
      <div><label>Nome</label><input name="nome" required></div>
    </div>
    <div class="row mt8">
      <div><label>Cargo</label><input name="funcao" placeholder="Ex: Operador"></div>
      <div><label>Área</label><input name="area" placeholder="Ex: CD Guarulhos"></div>
      <div><label>Turno</label><input name="turno" placeholder="Ex: 1º Turno"></div>
    </div>
    <div class="row mt8">
      <div><label>Senha</label><input type="password" name="senha" required></div>
      <div><label>Confirmar senha</label><input type="password" name="senha2" required></div>
    </div>
    <button class="btn block mt16" type="submit">Cadastrar</button>
    <a class="btn secondary mt8" href="{{ url_for('login') }}">Voltar ao Login</a>
{% endblock %}
""",

    # ====== MANUTENÇÃO ======
    "manutencao.html": """
{% extends "base.html" %}
{% block content %}
<style>.panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}.row{display:flex;gap:16px;flex-wrap:wrap}.row > div{min-width:220px;flex:1}input,select,textarea{width:100%}textarea{min-height:100px}.readonly{background:#0e1117;border:1px dashed #30363d;border-radius:8px;padding:10px;color:#e6edf3}.muted{color:#8b949e}</style>
<div class="panel">
  <h3>Enviar Coletor para Manutenção</h3>
  <div class="row"><div><label>Buscar coletor</label><input id="filterColetor" placeholder="Digite número, modelo ou serial..."></div></div>
  <form id="frmMan" method="post" onsubmit="return validaObs()">
    <div class="row">
      <div><label>Coletor (apenas disponíveis)</label>
        <select id="coletor_id" name="coletor_id" required>
          <option value="" disabled selected>-- selecione --</option>
          {% for c in coletores %}
            <option value="{{ c.id }}" data-last_matricula="{{ c.last_matricula or '' }}" data-last_nome="{{ c.last_nome or '' }}" data-last_turno="{{ c.last_turno or '' }}">{{ c.numero_coletor }} · {{ c.tipo_equipamento }} · {{ c.serial }}</option>
          {% endfor %}
        </select>
      </div>
      <div><label>Status</label>
        <select name="status" required><option value="MANUTENCAO" selected>MANUTENCAO</option><option value="PREVENTIVA">PREVENTIVA</option><option value="CORRETIVA">CORRETIVA</option><option value="AGUARDANDO_PECA">AGUARDANDO_PECA</option></select>
      </div>
    </div>
    <div class="row">
      <div><label>Última matrícula</label><div id="ultima_matricula" class="readonly muted">—</div></div>
      <div><label>Último usuário</label><div id="ultimo_usuario" class="readonly muted">—</div></div>
      <div><label>Turno</label><div id="turno" class="readonly muted">—</div></div>
    </div>
    <div class="row"><div><label>Observação <span class="muted">(obrigatório)</span></label><textarea id="observacao" name="observacao" maxlength="500" required placeholder="Descreva o problema/serviço..."></textarea></div></div>
    <div class="row"><div><button class="btn" type="submit">Enviar para manutenção</button></div><div><a class="btn secondary" href="{{ url_for('web.home_web') }}">Voltar</a></div></div>
  </form>
</div>
<script>
 const inputFilter=document.getElementById('filterColetor'); const sel=document.getElementById('coletor_id');
 inputFilter?.addEventListener('input',()=>{const q=inputFilter.value.toLowerCase(); for(const opt of sel.options){ if(!opt.value) continue; opt.hidden=!opt.text.toLowerCase().includes(q);} if(sel.selectedIndex>0 && sel.options[sel.selectedIndex].hidden){ sel.selectedIndex=0; }});
 sel?.addEventListener('change',()=>{const opt=sel.options[sel.selectedIndex]; if(!opt||!opt.value){ setLast('—','—','—'); return;} const m=opt.dataset.last_matricula||'', n=opt.dataset.last_nome||'', t=opt.dataset.last_turno||''; if(m||n||t) setLast(m||'Sem histórico',n||'Sem histórico',t||'Sem histórico'); else setLast('Sem histórico','Sem histórico','Sem histórico');});
 function setLast(m,n,t){document.getElementById('ultima_matricula').textContent=m; document.getElementById('ultimo_usuario').textContent=n; document.getElementById('turno').textContent=t;}
 function validaObs(){const v=(document.getElementById('observacao').value||'').trim(); if(!v){alert('Observação é obrigatória.'); return false;} return true;}
</script>
{% endblock %}
""",

    # ====== RESERVAR (SELECIONA COLETOR + MATRÍCULA) ======
    "reservar.html": """
{% extends "base.html" %}
{% block content %}
<style>.panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}.row{display:flex;gap:16px;flex-wrap:wrap}.row>div{min-width:240px;flex:1}input,select{width:100%}.card{border:1px solid #30363d;border-radius:10px;padding:10px;margin-top:8px}</style>
<div class="panel">
  <h3>Reservar Coletor</h3>
  <div class="row"><div><label>Filtrar coletor</label><input id="filtro" placeholder="Digite número/serial/modelo..."></div></div>
  <form method="post">
    <div class="row">
      <div>
        <label>Coletor (apenas disponíveis)</label>
        <select id="coletor_id" name="coletor_id" required size="8">
          {% for c in disponiveis %}
          <option value="{{ c.id }}">{{ c.cd }} · {{ c.numero_coletor }} · {{ c.serial }}</option>
          {% endfor %}
        </select>
      </div>
      <div>
        <label>Matrícula</label>
        <input id="matricula" name="matricula" placeholder="Digite a matrícula" required>
        <div id="cardUser" class="card" style="display:none">
          <div><b>Nome:</b> <span id="u_nome"></span></div>
          <div><b>Área:</b> <span id="u_area"></span> · <b>Turno:</b> <span id="u_turno"></span></div>
          <div><b>Função:</b> <span id="u_funcao"></span> · <b>Perfil:</b> <span id="u_perfil"></span> · <b>Ativo:</b> <span id="u_ativo"></span></div>
        </div>
      </div>
    </div>
    <div class="row"><div><button id="btn" class="btn" type="submit">Reservar</button></div><div><a class="btn secondary" href="{{ url_for('web.home_web') }}">Voltar</a></div></div>
  </form>
</div>
<script>
const filtro=document.getElementById('filtro'); const sel=document.getElementById('coletor_id');
filtro?.addEventListener('input',()=>{const q=filtro.value.toLowerCase(); for(const op of sel.options){op.hidden=!op.text.toLowerCase().includes(q);}});

const elMat=document.getElementById('matricula'), card=document.getElementById('cardUser');
const nome=document.getElementById('u_nome'), area=document.getElementById('u_area'), turno=document.getElementById('u_turno'), func=document.getElementById('u_funcao'), perf=document.getElementById('u_perfil'), ativ=document.getElementById('u_ativo'), btn=document.getElementById('btn');
async function busca(m){
  if(!m){card.style.display='none';btn.disabled=true;return;}
  try{
    const r=await fetch(`{{ url_for('web.api_usuario') }}?matricula=${encodeURIComponent(m)}`);
    const d=await r.json();
    if(d && d.ok && d.usuario){
      nome.textContent=d.usuario.nome||''; area.textContent=d.usuario.area||''; turno.textContent=d.usuario.turno||'';
      func.textContent=d.usuario.funcao||''; perf.textContent=d.usuario.perfil||''; ativ.textContent=(d.usuario.ativo==1?'Sim':'Não');
      card.style.display='block'; btn.disabled=(d.usuario.ativo!=1);
    }else{card.style.display='none'; btn.disabled=true;}
  }catch(e){card.style.display='none'; btn.disabled=true;}
}
elMat.addEventListener('keyup',e=>busca(e.target.value.trim()));
elMat.addEventListener('blur',e=>busca(e.target.value.trim()));
</script>
{% endblock %}
""",

    # ====== DEVOLVER (SELECIONA O COLETOR EM USO) ======
    "devolver.html": """
{% extends "base.html" %}
{% block content %}
<style>.panel{background:#0d1117;border:1px solid #30363d;border-radius:12px;padding:12px}.row{display:flex;gap:16px;flex-wrap:wrap}.row>div{min-width:240px;flex:1}input,select{width:100%}</style>
<div class="panel">
  <h3>Devolver Coletor</h3>
  <div class="row"><div><label>Filtrar coletor em uso</label><input id="filtro" placeholder="Digite número/serial/modelo/matrícula..."></div></div>
  <form method="post">
    <div class="row">
      <div>
        <label>Selecionar coletor para devolução</label>
        <select id="coletor_id" name="coletor_id" required size="10">
          {% for r in em_uso %}
          <option value="{{ r.coletor_id }}">
            {{ r.numero_coletor }} · {{ r.tipo_equipamento }} · {{ r.serial }} · {{ r.matricula }} - {{ r.nome }}
          </option>
          {% endfor %}
        </select>
      </div>
    </div>
    <div class="row"><div><button class="btn" type="submit">Devolver</button></div><div><a class="btn secondary" href="{{ url_for('web.home_web') }}">Voltar</a></div></div>
  </form>
</div>
<script>
const filtro=document.getElementById('filtro'); const sel=document.getElementById('coletor_id');
filtro?.addEventListener('input',()=>{const q=filtro.value.toLowerCase(); for(const op of sel.options){op.hidden=!op.text.toLowerCase().includes(q);}});
</script>
{% endblock %}
"""
}

# ---------------- Helpers ----------------
def query_all(sql, params=()):
    conn = conectar_banco(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params); rows = cur.fetchall()
    cur.close(); conn.close(); return rows

def query_one(sql, params=()):
    conn = conectar_banco(); cur = conn.cursor(dictionary=True)
    cur.execute(sql, params); row = cur.fetchone()
    cur.close(); conn.close(); return row

def exec_sql(sql, params=()):
    conn = conectar_banco(); cur = conn.cursor()
    cur.execute(sql, params); conn.commit()
    cur.close(); conn.close()

def require_login():
    if not session.get("user"):
        flash("Faça login para continuar.", "err")
        return False
    return True

def _humanize_seconds(seconds:int)->str:
    if seconds < 0: seconds = 0
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    if d: return f"{d}d {h}h {m}m"
    if h: return f"{h}h {m}m"
    if m: return f"{m}m {s}s"
    return f"{s}s"

# ---------------- API aux (buscar usuário por matrícula) ----------------
@web.route("/api/usuario")
def api_usuario():
    mat = (request.args.get("matricula") or "").strip()
    if not mat:
        return jsonify({"ok": False, "msg": "Informe a matrícula."})
    u = query_one("""SELECT id_usuario, cd, matricula, nome, area, turno, funcao, perfil, ativo
                     FROM usuarios WHERE matricula=%s AND deletado_em IS NULL LIMIT 1""", (mat,))
    return jsonify({"ok": True, "usuario": u})

# ---------------- Página inicial ----------------
@web.route("/web")
def home_web():
    if not require_login(): return redirect(url_for("login"))
    u = session["user"]

    disponiveis = query_all("""
        SELECT c.id, c.cd, c.numero_coletor, c.serial, c.tipo_equipamento, c.status
        FROM coletores c
        LEFT JOIN uso_atual ua ON ua.coletor_id = c.id
        WHERE ua.id IS NULL AND c.deletado_em IS NULL AND c.status = 'DISPONIVEL'
        ORDER BY c.cd, c.numero_coletor
    """)

    em_uso_raw = query_all("""
        SELECT c.numero_coletor, c.tipo_equipamento, c.serial, c.status,
               ua.matricula, ua.turno, ua.dt_hora_retirada, ua.coletor_id,
               u.nome, u.funcao, u.area, u.cd
        FROM uso_atual ua
        JOIN coletores c ON c.id = ua.coletor_id
        LEFT JOIN usuarios u ON u.matricula = ua.matricula
        ORDER BY ua.dt_hora_retirada DESC
    """)

    em_uso = []
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for r in em_uso_raw:
        dthr = r["dt_hora_retirada"]
        dthr_fmt = dthr.strftime("%d/%m/%Y %H:%M:%S") if dthr else ""
        seconds = int((now - dthr).total_seconds()) if dthr else 0
        em_uso.append({**r, "dt_hora_retirada_fmt": dthr_fmt, "tempo_em_uso": _humanize_seconds(seconds)})

    return render_template("home_web.html", title="Início", header="Início",
                           user=u, disponiveis=disponiveis, em_uso=em_uso,
                           dbname=DATABASE, host=HOST, dbuser=USER)

# ---------------- COLETORES (CRUD + Import/Export) ----------------
@web.route("/coletores")
def coletores_list():
    if not require_login(): return redirect(url_for("login"))
    coletores = query_all("""
        SELECT id, cd, numero_coletor, serial, tipo_equipamento, status
        FROM coletores
        WHERE deletado_em IS NULL
        ORDER BY cd, numero_coletor
    """)
    return render_template("coletores_list.html", title="Coletores", header="Coletores",
                           coletores=coletores, dbname=DATABASE, host=HOST, dbuser=USER)

@web.route("/coletores/novo", methods=["GET","POST"])
def coletores_novo():
    if not require_login(): return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("coletores_form.html", title="Cadastrar Coletor", header="Cadastrar Coletor",
                               coletor=None, dbname=DATABASE, host=HOST, dbuser=USER)
    cd = (request.form.get("cd") or "").strip()
    numero = (request.form.get("numero_coletor") or "").strip()
    serial = (request.form.get("serial") or "").strip()
    modelo = (request.form.get("tipo_equipamento") or "").strip()
    status = (request.form.get("status") or "DISPONIVEL").strip()
    if not cd or not numero or not serial or not modelo:
        flash("Preencha CD, Número, Serial e Modelo.", "err"); return redirect(url_for("web.coletores_novo"))
    dup = query_one("SELECT id FROM coletores WHERE serial=%s AND deletado_em IS NULL LIMIT 1", (serial,))
    if dup:
        flash("Já existe coletor com este SERIAL.", "err"); return redirect(url_for("web.coletores_novo"))
    exec_sql("""
        INSERT INTO coletores (cd, numero_coletor, serial, tipo_equipamento, status, usuario_movimentacao)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (cd, numero, serial, modelo, status, session["user"]["matricula"]))
    flash("Coletor cadastrado.", "ok"); return redirect(url_for("web.coletores_list"))

@web.route("/coletores/<int:coletor_id>/editar", methods=["GET","POST"])
def coletores_editar(coletor_id:int):
    if not require_login(): return redirect(url_for("login"))
    if request.method == "GET":
        c = query_one("""
            SELECT id, cd, numero_coletor, serial, tipo_equipamento, status
            FROM coletores WHERE id=%s AND deletado_em IS NULL
        """, (coletor_id,))
        if not c:
            flash("Coletor não encontrado.", "err"); return redirect(url_for("web.coletores_list"))
        return render_template("coletores_form.html", title="Editar Coletor", header="Editar Coletor",
                               coletor=c, dbname=DATABASE, host=HOST, dbuser=USER)
    cd = (request.form.get("cd") or "").strip()
    numero = (request.form.get("numero_coletor") or "").strip()
    serial = (request.form.get("serial") or "").strip()
    modelo = (request.form.get("tipo_equipamento") or "").strip()
    status = (request.form.get("status") or "DISPONIVEL").strip()
    if not cd or not numero or not serial or not modelo:
        flash("Preencha CD, Número, Serial e Modelo.", "err"); return redirect(url_for("web.coletores_editar", coletor_id=coletor_id))
    dup = query_one("SELECT id FROM coletores WHERE serial=%s AND id<>%s AND deletado_em IS NULL LIMIT 1", (serial, coletor_id))
    if dup:
        flash("Já existe outro coletor com este SERIAL.", "err"); return redirect(url_for("web.coletores_editar", coletor_id=coletor_id))
    exec_sql("""
        UPDATE coletores SET cd=%s, numero_coletor=%s, serial=%s, tipo_equipamento=%s,
            status=%s, usuario_movimentacao=%s
        WHERE id=%s
    """, (cd, numero, serial, modelo, status, session["user"]["matricula"], coletor_id))
    flash("Coletor atualizado.", "ok"); return redirect(url_for("web.coletores_list"))

@web.route("/coletores/importar", methods=["GET","POST"])
def coletores_importar():
    if not require_login(): return redirect(url_for("login"))
    resultado=None
    if request.method == "POST":
        f = request.files.get("arquivo")
        if not f:
            flash("Selecione um arquivo CSV.", "err"); return redirect(url_for("web.coletores_importar"))
        try:
            data = f.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(data), delimiter=';')
            headers = {h.strip().lower() for h in (reader.fieldnames or [])}
            required = {"cd","numero_coletor","serial","tipo_equipamento"}
            if not required.issubset(headers):
                flash("CSV inválido. Cabeçalhos: cd;numero_coletor;serial;tipo_equipamento", "err")
                return redirect(url_for("web.coletores_importar"))
            inseridos=ignorados=erros=0
            for row in reader:
                try:
                    cd=(row.get("cd") or "").strip()
                    numero=(row.get("numero_coletor") or "").strip()
                    serial=(row.get("serial") or "").strip()
                    modelo=(row.get("tipo_equipamento") or "").strip()
                    if not cd or not numero or not serial or not modelo:
                        erros+=1; continue
                    if query_one("SELECT id FROM coletores WHERE serial=%s AND deletado_em IS NULL LIMIT 1",(serial,)):
                        ignorados+=1; continue
                    exec_sql("""INSERT INTO coletores (cd,numero_coletor,serial,tipo_equipamento,status,usuario_movimentacao)
                                VALUES (%s,%s,%s,%s,'DISPONIVEL',%s)""",
                             (cd,numero,serial,modelo,session["user"]["matricula"]))
                    inseridos+=1
                except Exception:
                    erros+=1
            resultado=type("R",(),{"inseridos":inseridos,"ignorados":ignorados,"erros":erros})
            flash(f"Importação concluída. Inseridos: {inseridos}, Ignorados: {ignorados}, Erros: {erros}", "ok" if inseridos else "err")
        except Exception:
            flash("Falha ao processar CSV.", "err")
            return redirect(url_for("web.coletores_importar"))
    return render_template("coletores_importar.html", title="Importar Coletores", header="Importar Coletores",
                           resultado=resultado, dbname=DATABASE, host=HOST, dbuser=USER)

@web.route("/coletores/exportar-modelo")
def coletores_exportar_modelo():
    if not require_login(): return redirect(url_for("login"))
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["cd","numero_coletor","serial","tipo_equipamento"])
    writer.writerow(["","","",""])
    data = output.getvalue().encode("utf-8-sig")
    resp = make_response(data)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = "attachment; filename=modelo_coletores.csv"
    return resp

@web.route("/coletores/exportar-banco")
def coletores_exportar_banco():
    if not require_login(): return redirect(url_for("login"))
    rows = query_all("""
        SELECT id, cd, numero_coletor, serial, tipo_equipamento, status,
               DATE_FORMAT(dt_addrow,'%Y-%m-%d %H:%i:%s.%f') AS dt_addrow,
               DATE_FORMAT(dt_updrow,'%Y-%m-%d %H:%i:%s.%f') AS dt_updrow,
               usuario_movimentacao
        FROM coletores
        WHERE deletado_em IS NULL
        ORDER BY cd, numero_coletor
    """)
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["id","cd","numero_coletor","serial","tipo_equipamento","status","dt_addrow","dt_updrow","usuario_movimentacao"])
    for r in rows:
        writer.writerow([r["id"], r["cd"], r["numero_coletor"], r["serial"], r["tipo_equipamento"],
                         r["status"], r["dt_addrow"] or "", r["dt_updrow"] or "", r["usuario_movimentacao"] or ""])
    data = output.getvalue().encode("utf-8-sig")
    resp = make_response(data)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = "attachment; filename=coletores.csv"
    return resp

# ---------------- USUÁRIOS (CRUD + Import/Export) ----------------
@web.route("/usuarios")
def usuarios_list():
    if not require_login(): return redirect(url_for("login"))
    usuarios = query_all("""
        SELECT id_usuario, cd, matricula, nome, area, turno, funcao, perfil, ativo
        FROM usuarios
        WHERE deletado_em IS NULL
        ORDER BY cd, nome
    """)
    return render_template("usuarios_list.html", title="Usuários", header="Usuários",
                           usuarios=usuarios, dbname=DATABASE, host=HOST, dbuser=USER)

@web.route("/usuarios/novo", methods=["GET","POST"])
def usuarios_novo():
    if not require_login(): return redirect(url_for("login"))
    if request.method == "GET":
        return render_template("usuarios_form.html", title="Cadastrar Usuário", header="Cadastrar Usuário",
                               usuario=None, dbname=DATABASE, host=HOST, dbuser=USER)
    cd = (request.form.get("cd") or "").strip()
    matricula = (request.form.get("matricula") or "").strip()
    nome = (request.form.get("nome") or "").strip()
    area = (request.form.get("area") or "").strip() or None
    turno = (request.form.get("turno") or "").strip() or None
    funcao = (request.form.get("funcao") or "").strip() or None
    perfil = (request.form.get("perfil") or "USER").strip()
    ativo = 1 if (request.form.get("ativo") == "1") else 0
    senha = request.form.get("senha") or ""
    if not cd or not matricula or not nome or not senha:
        flash("Preencha CD, matrícula, nome e senha.", "err"); return redirect(url_for("web.usuarios_novo"))
    if query_one("SELECT id_usuario FROM usuarios WHERE matricula=%s AND deletado_em IS NULL", (matricula,)):
        flash("Já existe usuário com esta matrícula.", "err"); return redirect(url_for("web.usuarios_novo"))
    hashpw = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode()
    exec_sql("""INSERT INTO usuarios (cd, matricula, nome, area, turno, funcao, perfil, senha_hash, ativo, usuario_movimentacao)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
             (cd, matricula, nome, area, turno, funcao, perfil, hashpw, ativo, session["user"]["matricula"]))
    flash("Usuário cadastrado.", "ok"); return redirect(url_for("web.usuarios_list"))

@web.route("/usuarios/<int:id_usuario>/editar", methods=["GET","POST"])
def usuarios_editar(id_usuario:int):
    if not require_login(): return redirect(url_for("login"))
    if request.method == "GET":
        u = query_one("""
            SELECT id_usuario, cd, matricula, nome, area, turno, funcao, perfil, ativo
            FROM usuarios WHERE id_usuario=%s AND deletado_em IS NULL
        """, (id_usuario,))
        if not u:
            flash("Usuário não encontrado.", "err"); return redirect(url_for("web.usuarios_list"))
        return render_template("usuarios_form.html", title="Editar Usuário", header="Editar Usuário",
                               usuario=u, dbname=DATABASE, host=HOST, dbuser=USER)
    cd = (request.form.get("cd") or "").strip()
    nome = (request.form.get("nome") or "").strip()
    area = (request.form.get("area") or "").strip() or None
    turno = (request.form.get("turno") or "").strip() or None
    funcao = (request.form.get("funcao") or "").strip() or None
    perfil = (request.form.get("perfil") or "USER").strip()
    ativo = 1 if (request.form.get("ativo") == "1") else 0
    senha = request.form.get("senha") or ""
    if not cd or not nome:
        flash("Preencha CD e nome.", "err"); return redirect(url_for("web.usuarios_editar", id_usuario=id_usuario))
    if senha.strip():
        hashpw = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode()
        exec_sql("""UPDATE usuarios SET cd=%s, nome=%s, area=%s, turno=%s, funcao=%s, perfil=%s, ativo=%s, senha_hash=%s, usuario_movimentacao=%s
                    WHERE id_usuario=%s""",
                 (cd, nome, area, turno, funcao, perfil, ativo, hashpw, session["user"]["matricula"], id_usuario))
    else:
        exec_sql("""UPDATE usuarios SET cd=%s, nome=%s, area=%s, turno=%s, funcao=%s, perfil=%s, ativo=%s, usuario_movimentacao=%s
                    WHERE id_usuario=%s""",
                 (cd, nome, area, turno, funcao, perfil, ativo, session["user"]["matricula"], id_usuario))
    flash("Usuário atualizado.", "ok"); return redirect(url_for("web.usuarios_list"))

@web.route("/usuarios/<int:id_usuario>/excluir", methods=["POST"])
def usuarios_excluir(id_usuario:int):
    if not require_login(): return redirect(url_for("login"))
    me = session["user"]["matricula"]
    u = query_one("SELECT matricula FROM usuarios WHERE id_usuario=%s", (id_usuario,))
    if u and u["matricula"] == me:
        flash("Você não pode excluir o seu próprio usuário.", "err"); return redirect(url_for("web.usuarios_list"))
    exec_sql("""UPDATE usuarios SET deletado_em = NOW(3), deletado_por=%s, usuario_movimentacao=%s WHERE id_usuario=%s""",
             (me, me, id_usuario))
    flash("Usuário excluído.", "ok"); return redirect(url_for("web.usuarios_list"))

# ---- IMPORTAÇÃO / EXPORTAÇÃO DE USUÁRIOS ----
@web.route("/usuarios/importar", methods=["GET","POST"])
def usuarios_importar():
    if not require_login(): return redirect(url_for("login"))
    resultado=None
    if request.method == "POST":
        f = request.files.get("arquivo")
        if not f:
            flash("Selecione um arquivo CSV.", "err"); return redirect(url_for("web.usuarios_importar"))
        try:
            data = f.read().decode("utf-8-sig")
            reader = csv.DictReader(io.StringIO(data), delimiter=';')
            headers = {h.strip().lower() for h in (reader.fieldnames or [])}
            required = {"cd","matricula","nome"}
            if not required.issubset(headers):
                flash("CSV inválido. Cabeçalhos mínimos: cd;matricula;nome", "err")
                return redirect(url_for("web.usuarios_importar"))
            inseridos=ignorados=erros=0
            for row in reader:
                try:
                    cd=(row.get("cd") or "").strip()
                    matricula=(row.get("matricula") or "").strip()
                    nome=(row.get("nome") or "").strip()
                    area=(row.get("area") or "").strip() or None
                    turno=(row.get("turno") or "").strip() or None
                    funcao=(row.get("funcao") or "").strip() or None
                    perfil=(row.get("perfil") or "USER").strip().upper()
                    ativo_val=(row.get("ativo") or "1").strip()
                    ativo=1 if ativo_val in ("1","true","TRUE","sim","SIM") else 0
                    senha=(row.get("senha") or "123456")
                    if not cd or not matricula or not nome:
                        erros+=1; continue
                    if query_one("SELECT id_usuario FROM usuarios WHERE matricula=%s AND deletado_em IS NULL LIMIT 1",(matricula,)):
                        ignorados+=1; continue
                    hashpw=bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode()
                    exec_sql("""INSERT INTO usuarios (cd,matricula,nome,area,turno,funcao,perfil,senha_hash,ativo,usuario_movimentacao)
                                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                             (cd,matricula,nome,area,turno,funcao,perfil,hashpw,ativo,session["user"]["matricula"]))
                    inseridos+=1
                except Exception:
                    erros+=1
            resultado=type("R",(),{"inseridos":inseridos,"ignorados":ignorados,"erros":erros})
            flash(f"Importação concluída. Inseridos: {inseridos}, Ignorados: {ignorados}, Erros: {erros}", "ok" if inseridos else "err")
        except Exception:
            flash("Falha ao processar CSV.", "err")
            return redirect(url_for("web.usuarios_importar"))
    return render_template("usuarios_importar.html", title="Importar Usuários", header="Importar Usuários",
                           resultado=resultado, dbname=DATABASE, host=HOST, dbuser=USER)

@web.route("/usuarios/exportar-modelo")
def usuarios_exportar_modelo():
    if not require_login(): return redirect(url_for("login"))
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["cd","matricula","nome","area","turno","funcao","perfil","ativo","senha"])
    writer.writerow(["","","","","","","USER","1","123456"])
    data = output.getvalue().encode("utf-8-sig")
    resp = make_response(data)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = "attachment; filename=modelo_usuarios.csv"
    return resp

@web.route("/usuarios/exportar-banco")
def usuarios_exportar_banco():
    if not require_login(): return redirect(url_for("login"))
    rows = query_all("""
        SELECT id_usuario, cd, matricula, nome, area, turno, funcao, perfil, ativo,
               DATE_FORMAT(dt_addrow,'%Y-%m-%d %H:%i:%s.%f') AS dt_addrow,
               DATE_FORMAT(dt_updrow,'%Y-%m-%d %H:%i:%s.%f') AS dt_updrow,
               usuario_movimentacao
        FROM usuarios
        WHERE deletado_em IS NULL
        ORDER BY cd, nome
    """)
    output = io.StringIO(newline="")
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["id_usuario","cd","matricula","nome","area","turno","funcao","perfil","ativo","dt_addrow","dt_updrow","usuario_movimentacao"])
    for r in rows:
        writer.writerow([
            r["id_usuario"], r["cd"], r["matricula"], r["nome"],
            r["area"] or "", r["turno"] or "", r["funcao"] or "",
            r["perfil"], (1 if r["ativo"] else 0),
            r["dt_addrow"] or "", r["dt_updrow"] or "", r["usuario_movimentacao"] or ""
        ])
    data = output.getvalue().encode("utf-8-sig")
    resp = make_response(data)
    resp.headers["Content-Type"] = "text/csv; charset=utf-8"
    resp.headers["Content-Disposition"] = "attachment; filename=usuarios.csv"
    return resp

# -------- Cadastro Público --------
@web.route("/cadastro", methods=["GET","POST"])
def cadastro_publico():
    if request.method == "GET":
        return render_template("cadastro_publico.html", title="Cadastro de Usuário", header="Cadastro de Usuário",
                               dbname=DATABASE, host=HOST, dbuser=USER)

    cd = (request.form.get("cd") or "").strip()
    matricula = (request.form.get("matricula") or "").strip()
    nome = (request.form.get("nome") or "").strip()
    funcao = (request.form.get("funcao") or "").strip() or None
    area = (request.form.get("area") or "").strip() or None
    turno = (request.form.get("turno") or "").strip() or None
    senha = request.form.get("senha") or ""
    senha2 = request.form.get("senha2") or ""
    if not cd or not matricula or not nome or not senha:
        flash("Informe CD, matrícula, nome e senha.", "err"); return redirect(url_for("web.cadastro_publico"))
    if senha != senha2:
        flash("As senhas não coincidem.", "err"); return redirect(url_for("web.cadastro_publico"))
    if query_one("SELECT id_usuario FROM usuarios WHERE matricula=%s AND deletado_em IS NULL", (matricula,)):
        flash("Já existe usuário com essa matrícula.", "err"); return redirect(url_for("web.cadastro_publico"))

    hashpw = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode()
    exec_sql("""INSERT INTO usuarios (cd, matricula, nome, area, turno, funcao, perfil, senha_hash, ativo, usuario_movimentacao)
                VALUES (%s,%s,%s,%s,%s,%s,'USER',%s,1,%s)""",
             (cd, matricula, nome, area, turno, funcao, hashpw, matricula))
    flash("Usuário cadastrado com sucesso. Faça o login.", "ok"); return redirect(url_for("login"))

# ---------------- Reservar / Devolver ----------------
@web.route("/reservar", methods=["GET", "POST"])
def reservar():
    if not require_login(): return redirect(url_for("login"))
    ulog = session["user"]

    if request.method == "GET":
        disponiveis = query_all("""
            SELECT c.id, c.cd, c.numero_coletor, c.serial, c.tipo_equipamento
            FROM coletores c
            LEFT JOIN uso_atual ua ON ua.coletor_id = c.id
            WHERE ua.id IS NULL AND c.deletado_em IS NULL AND c.status='DISPONIVEL'
            ORDER BY c.cd, c.numero_coletor
        """)
        return render_template("reservar.html", title="Reservar Coletor", header="Reservar Coletor",
                               disponiveis=disponiveis, dbname=DATABASE, host=HOST, dbuser=USER)

    coletor_id = request.form.get("coletor_id")
    matricula = (request.form.get("matricula") or "").strip()
    if not coletor_id:
        flash("Selecione um coletor.", "err"); return redirect(url_for("web.reservar"))
    if not matricula:
        flash("Informe a matrícula do colaborador.", "err"); return redirect(url_for("web.reservar"))

    usuario = query_one("""SELECT matricula, nome, turno, ativo FROM usuarios
                           WHERE matricula=%s AND deletado_em IS NULL LIMIT 1""", (matricula,))
    if not usuario:
        flash("Matrícula não encontrada.", "err"); return redirect(url_for("web.reservar"))
    if int(usuario.get("ativo",1)) != 1:
        flash("Usuário inativo. Não é possível reservar.", "err"); return redirect(url_for("web.reservar"))

    if query_one("SELECT id FROM uso_atual WHERE coletor_id=%s", (coletor_id,)):
        flash("Coletor já está em uso.", "err"); return redirect(url_for("web.reservar"))
    if query_one("SELECT id FROM uso_atual WHERE matricula=%s", (matricula,)):
        flash("Este colaborador já possui um coletor em uso.", "err"); return redirect(url_for("web.reservar"))

    turno = usuario.get("turno") or None
    exec_sql("""INSERT INTO uso_atual (coletor_id, matricula, turno, usuario_movimentacao)
                VALUES (%s,%s,%s,%s)""", (coletor_id, matricula, turno, ulog["matricula"]))
    exec_sql("""INSERT INTO movimentacoes (coletor_id, matricula, acao, status_origem, status_destino, turno, motivo_id, observacao, usuario_movimentacao)
                SELECT c.id, %s, 'RESERVA', c.status, 'EM_USO', %s, NULL, NULL, %s FROM coletores c WHERE c.id=%s
             """, (matricula, turno, ulog["matricula"], coletor_id))
    exec_sql("UPDATE coletores SET status='EM_USO' WHERE id=%s", (coletor_id,))
    flash("Coletor reservado com sucesso para a matrícula {}.".format(matricula), "ok"); return redirect(url_for("web.home_web"))

@web.route("/devolver", methods=["GET", "POST"])
def devolver():
    if not require_login(): return redirect(url_for("login"))
    ulog = session["user"]

    if request.method == "GET":
        em_uso = query_all("""
            SELECT ua.id, ua.coletor_id, ua.matricula, ua.turno, ua.dt_hora_retirada,
                   c.numero_coletor, c.tipo_equipamento, c.serial,
                   u.nome
            FROM uso_atual ua
            JOIN coletores c ON c.id = ua.coletor_id
            LEFT JOIN usuarios u ON u.matricula = ua.matricula
            ORDER BY ua.dt_hora_retirada DESC
        """)
        return render_template("devolver.html", title="Devolver Coletor", header="Devolver Coletor",
                               em_uso=em_uso, dbname=DATABASE, host=HOST, dbuser=USER)

    coletor_id = request.form.get("coletor_id")
    if not coletor_id:
        flash("Selecione um coletor para devolução.", "err"); return redirect(url_for("web.devolver"))

    uso = query_one("""SELECT id, coletor_id, matricula FROM uso_atual WHERE coletor_id=%s LIMIT 1""", (coletor_id,))
    if not uso:
        flash("Este coletor não está registrado como 'em uso'.", "err"); return redirect(url_for("web.devolver"))

    exec_sql("""INSERT INTO movimentacoes (coletor_id, matricula, acao, status_origem, status_destino, turno, motivo_id, observacao, usuario_movimentacao)
                VALUES (%s,%s,'DEVOLUCAO','EM_USO','DISPONIVEL',NULL,NULL,NULL,%s)
             """, (uso["coletor_id"], uso["matricula"], ulog["matricula"]))
    exec_sql("DELETE FROM uso_atual WHERE id=%s", (uso["id"],))
    exec_sql("UPDATE coletores SET status='DISPONIVEL' WHERE id=%s", (uso["coletor_id"],))
    flash("Coletor devolvido.", "ok"); return redirect(url_for("web.home_web"))

# ---------------- Manutenção ----------------
@web.route("/manutencao", methods=["GET", "POST"])
def manutencao():
    if not require_login(): return redirect(url_for("login"))
    u = session["user"]

    if request.method == "GET":
        coletores = query_all("""
            SELECT c.id, c.numero_coletor, c.tipo_equipamento, c.serial,
                   lm.matricula AS last_matricula, u.nome AS last_nome, lm.turno AS last_turno
            FROM coletores c
            LEFT JOIN (SELECT m.coletor_id, MAX(m.id) AS mid FROM movimentacoes m GROUP BY m.coletor_id) lm_id ON lm_id.coletor_id = c.id
            LEFT JOIN movimentacoes lm ON lm.id = lm_id.mid
            LEFT JOIN usuarios u ON u.matricula = lm.matricula
            LEFT JOIN uso_atual ua ON ua.coletor_id = c.id
            WHERE ua.id IS NULL AND c.deletado_em IS NULL AND c.status = 'DISPONIVEL'
            ORDER BY c.cd, c.numero_coletor
        """)
        return render_template("manutencao.html", title="Manutenção", header="Manutenção",
                               coletores=coletores, dbname=DATABASE, host=HOST, dbuser=USER)

    coletor_id = request.form.get("coletor_id")
    status = (request.form.get("status") or "MANUTENCAO").strip()
    observacao = (request.form.get("observacao") or "").strip()
    if not coletor_id:
        flash("Selecione um coletor.", "err"); return redirect(url_for("web.manutencao"))
    if not observacao:
        flash("Observação é obrigatória.", "err"); return redirect(url_for("web.manutencao"))

    disp = query_one("""
        SELECT c.status FROM coletores c
        LEFT JOIN uso_atual ua ON ua.coletor_id=c.id
        WHERE c.id=%s AND ua.id IS NULL
    """, (coletor_id,))
    if not disp or disp["status"] != "DISPONIVEL":
        flash("Coletor não está disponível para manutenção.", "err"); return redirect(url_for("web.manutencao"))

    last = query_one("""
        SELECT m.matricula, m.turno, u.nome
        FROM movimentacoes m
        LEFT JOIN usuarios u ON u.matricula = m.matricula
        WHERE m.coletor_id=%s
        ORDER BY m.id DESC
        LIMIT 1
    """, (coletor_id,))
    ultima_matricula = last["matricula"] if last and last.get("matricula") else None
    ultimo_usuario  = last["nome"] if last and last.get("nome") else None
    turno           = last["turno"] if last and last.get("turno") else None

    cstat = query_one("SELECT status FROM coletores WHERE id=%s", (coletor_id,))
    status_origem = cstat["status"] if cstat else None

    exec_sql("""
        INSERT INTO manutencoes (coletor_id, ultima_matricula, ultimo_usuario, turno, status, motivo_id, observacao, usuario_movimentacao)
        VALUES (%s,%s,%s,%s,%s,NULL,%s,%s)
    """, (coletor_id, ultima_matricula, ultimo_usuario, turno, status, observacao, u["matricula"]))

    exec_sql("""
        INSERT INTO movimentacoes (coletor_id, matricula, acao, status_origem, status_destino, turno, motivo_id, observacao, usuario_movimentacao)
        VALUES (%s,%s,'MANUTENCAO',%s,'MANUTENCAO',%s,NULL,%s,%s)
    """, (coletor_id, (ultima_matricula or u["matricula"]), status_origem, turno, observacao, u["matricula"]))

    exec_sql("UPDATE coletores SET status='MANUTENCAO' WHERE id=%s", (coletor_id,))

    flash("Coletor enviado para manutenção.", "ok")
    return redirect(url_for("web.home_web"))

@web.route("/logout")
def logout():
    session.clear()
    flash("Sessão encerrada.", "ok")
    return redirect(url_for("login"))

def register_app(app):
    if hasattr(app.jinja_loader, "mapping"):
        app.jinja_loader.mapping.update(WEB_TEMPLATES)
    else:
        app.jinja_loader = DictLoader(WEB_TEMPLATES)
    app.register_blueprint(web)
