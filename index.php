<?php
require_once 'functions.php';
$page = $_GET['page'] ?? null;

// Login POST
if($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'login'){
    $mat = trim($_POST['matricula'] ?? '');
    $senha = $_POST['senha'] ?? '';
    if(!$mat || !$senha){ $_SESSION['flash'] = ['type'=>'err','msg'=>'Informe matrícula e senha.']; header('Location: index.php'); exit; }
    $row = query_one('SELECT id_usuario, matricula, nome, funcao, area, perfil, ativo, senha_hash FROM usuarios WHERE deletado_em IS NULL AND matricula = ? LIMIT 1', [$mat]);
    if(!$row || intval($row['ativo']) !== 1){ $_SESSION['flash']=['type'=>'err','msg'=>'Matrícula inexistente ou usuário inativo.']; header('Location: index.php'); exit; }
    if(!password_verify($senha, $row['senha_hash'] ?? '')){ $_SESSION['flash']=['type'=>'err','msg'=>'Senha inválida.']; header('Location: index.php'); exit; }
    $_SESSION['user'] = ['id_usuario'=>$row['id_usuario'],'matricula'=>$row['matricula'],'nome'=>$row['nome'],'perfil'=>$row['perfil']];
    $_SESSION['flash']=['type'=>'ok','msg'=>'Login realizado com sucesso.'];
    header('Location: index.php?page=home'); exit;
}

// logout
if($page === 'logout'){ session_destroy(); header('Location: index.php'); exit; }

// public registration
if($_SERVER['REQUEST_METHOD']==='POST' && isset($_POST['action']) && $_POST['action']==='cadastro_publico'){
    $cd = trim($_POST['cd'] ?? ''); $mat = trim($_POST['matricula'] ?? ''); $nome = trim($_POST['nome'] ?? ''); $senha = $_POST['senha'] ?? '';
    if(!$cd || !$mat || !$nome || !$senha){ $_SESSION['flash']=['type'=>'err','msg'=>'Preencha CD, matrícula, nome e senha.']; header('Location: index.php?page=cadastro_publico'); exit; }
    if(query_one('SELECT id_usuario FROM usuarios WHERE matricula=? AND deletado_em IS NULL LIMIT 1',[$mat])){ $_SESSION['flash']=['type'=>'err','msg'=>'Já existe usuário com esta matrícula.']; header('Location: index.php?page=cadastro_publico'); exit; }
    $hash = password_hash($senha, PASSWORD_DEFAULT);
    exec_sql('INSERT INTO usuarios (cd,matricula,nome,area,turno,funcao,perfil,senha_hash,ativo,usuario_movimentacao) VALUES (?,?,?,?,?,?,?,?,?,?)', [$cd,$mat,$nome,null,null,null,'USER',$hash,1,$mat]);
    $_SESSION['flash']=['type'=>'ok','msg'=>'Usuário cadastrado. Faça login.'];
    header('Location: index.php'); exit;
}

// Protected pages
if(in_array($page, ['home','coletores','usuarios','reservar','devolver','manutencao','coletores_import','usuarios_import'])){
    require_login();
}

// Include header
$title = 'Sistema de Coletores'; $header = 'Controle de Coletores'; $db_info = DB_NAME.' @ '.DB_HOST;
include 'header.php';

// Router
if(!$page){
    // Show login form
    ?>
    <h3>Login</h3>
    <form method="post" autocomplete="off">
      <label>Matrícula</label><input name="matricula" required>
      <label>Senha</label><input type="password" name="senha" required>
      <input type="hidden" name="action" value="login">
      <br><br><button class="btn" type="submit">Entrar</button>
    </form>
    <br>
    <a class="btn secondary" href="index.php?page=cadastro_publico">Cadastrar usuário</a>
    <p class="muted"><?php echo htmlspecialchars( (function(){ try { $c=conectar_banco(); $c->close(); return '✅ Conectado ao banco de dados!'; } catch(Exception $e){ return '❌ Erro: '.$e->getMessage(); } })() ); ?></p>
    <?php
    include 'footer.php'; exit;
}

// cadastro público
if($page === 'cadastro_publico'){
    ?>
    <h3>Cadastro de Usuário</h3>
    <form method="post" autocomplete="off">
      <label>CD</label><input name="cd" required>
      <label>Matrícula</label><input name="matricula" required>
      <label>Nome</label><input name="nome" required>
      <label>Senha</label><input type="password" name="senha" required>
      <input type="hidden" name="action" value="cadastro_publico">
      <br><br><button class="btn" type="submit">Cadastrar</button>
      <a class="btn secondary" href="index.php">Voltar ao Login</a>
    </form>
    <?php include 'footer.php'; exit;
}

// HOME - lista disponíveis e em uso
if($page === 'home'){
    $u = $_SESSION['user'];
    $disponiveis = query_all("""
        SELECT c.id, c.cd, c.numero_coletor, c.serial, c.tipo_equipamento, c.status
        FROM coletores c
        LEFT JOIN uso_atual ua ON ua.coletor_id = c.id
        WHERE ua.id IS NULL AND c.deletado_em IS NULL AND c.status = 'DISPONIVEL'
        ORDER BY c.cd, c.numero_coletor
    """);
    $em_uso_raw = query_all("""
        SELECT c.numero_coletor, c.tipo_equipamento, c.serial, c.status,
               ua.matricula, ua.turno, ua.dt_hora_retirada, ua.coletor_id,
               u.nome, u.funcao, u.area, u.cd
        FROM uso_atual ua
        JOIN coletores c ON c.id = ua.coletor_id
        LEFT JOIN usuarios u ON u.matricula = ua.matricula
        ORDER BY ua.dt_hora_retirada DESC
    """);
    echo '<div style="display:flex;gap:16px">';
    echo '<div style="flex:1"><h3>Coletores Disponíveis</h3><table><thead><tr><th>Número</th><th>Modelo</th><th>Serial</th></tr></thead><tbody>';
    if(count($disponiveis)){
        foreach($disponiveis as $c){ echo "<tr><td>{$c['numero_coletor']}</td><td>{$c['tipo_equipamento']}</td><td>{$c['serial']}</td></tr>"; }
    } else echo '<tr><td colspan="3" class="muted">Sem coletores disponíveis.</td></tr>';
    echo '</tbody></table></div>';
    echo '<div style="flex:1"><h3>Coletores em Uso</h3><table><thead><tr><th>Número</th><th>Modelo</th><th>Serial</th><th>Matrícula</th><th>Nome</th><th>Turno</th><th>Data Hora Retirado</th><th>Tempo em Uso</th></tr></thead><tbody>';
    if(count($em_uso_raw)){
        foreach($em_uso_raw as $r){
            $dthr = $r['dt_hora_retirada']; $dthr_fmt = $dthr ? date('d/m/Y H:i:s', strtotime($dthr)) : '';
            $seconds = $dthr ? (time() - strtotime($dthr)) : 0;
            $tempo = humanize_seconds($seconds);
            echo "<tr><td>{$r['numero_coletor']}</td><td>{$r['tipo_equipamento']}</td><td>{$r['serial']}</td><td>{$r['matricula']}</td><td>{$r['nome']}</td><td>{$r['turno']}</td><td>{$dthr_fmt}</td><td>{$tempo}</td></tr>";
        }
    } else echo '<tr><td colspan="8" class="muted">Nenhum coletor em uso no momento.</td></tr>';
    echo '</tbody></table></div></div>';
    include 'footer.php'; exit;
}

// COLETORES - list & actions minimal (view, add, edit)
if($page === 'coletores'){
    if($_SERVER['REQUEST_METHOD']==='POST' && isset($_POST['action']) && $_POST['action']==='novo_coletor'){
        $cd = trim($_POST['cd'] ?? ''); $numero = trim($_POST['numero_coletor'] ?? ''); $serial = trim($_POST['serial'] ?? ''); $tipo = trim($_POST['tipo_equipamento'] ?? '');
        $status = trim($_POST['status'] ?? 'DISPONIVEL');
        if(!$cd || !$numero || !$serial || !$tipo){ $_SESSION['flash']=['type'=>'err','msg'=>'Preencha CD, Número, Serial e Modelo.']; header('Location: index.php?page=coletores'); exit; }
        if(query_one('SELECT id FROM coletores WHERE serial=? AND deletado_em IS NULL LIMIT 1',[$serial])){ $_SESSION['flash']=['type'=>'err','msg'=>'Já existe coletor com este SERIAL.']; header('Location: index.php?page=coletores'); exit; }
        exec_sql('INSERT INTO coletores (cd,numero_coletor,serial,tipo_equipamento,status,usuario_movimentacao) VALUES (?,?,?,?,?,?)',[$cd,$numero,$serial,$tipo,$status,$_SESSION['user']['matricula']]);
        $_SESSION['flash']=['type'=>'ok','msg'=>'Coletor cadastrado.']; header('Location: index.php?page=coletores'); exit;
    }
    $coletores = query_all('SELECT id, cd, numero_coletor, serial, tipo_equipamento, status FROM coletores WHERE deletado_em IS NULL ORDER BY cd, numero_coletor');
    echo '<h3>Coletores <a class="btn" href="index.php?page=coletores&action=novo">Cadastrar Coletor</a> <a class="btn secondary" href="index.php?page=home">Voltar</a></h3>';
    if(isset($_GET['action']) && $_GET['action']==='novo'){
        ?>
        <form method="post">
          <label>CD</label><input name="cd" required>
          <label>Número do Coletor</label><input name="numero_coletor" required>
          <label>Serial</label><input name="serial" required>
          <label>Modelo</label><input name="tipo_equipamento" required>
          <label>Status</label><select name="status"><option>DISPONIVEL</option><option>EM_USO</option><option>MANUTENCAO</option><option>INATIVO</option></select>
          <input type="hidden" name="action" value="novo_coletor">
          <br><br><button class="btn" type="submit">Salvar</button> <a class="btn secondary" href="index.php?page=coletores">Cancelar</a>
        </form>
        <?php
        include 'footer.php'; exit;
    }
    echo '<table><thead><tr><th>CD</th><th>Número</th><th>Serial</th><th>Modelo</th><th>Status</th></tr></thead><tbody>';
    foreach($coletores as $c){ echo "<tr><td>{$c['cd']}</td><td>{$c['numero_coletor']}</td><td>{$c['serial']}</td><td>{$c['tipo_equipamento']}</td><td>{$c['status']}</td></tr>"; }
    echo '</tbody></table>';
    include 'footer.php'; exit;
}

// USUÁRIOS - list & add minimal
if($page === 'usuarios'){
    if($_SERVER['REQUEST_METHOD']==='POST' && isset($_POST['action']) && $_POST['action']==='novo_usuario'){
        $cd = trim($_POST['cd'] ?? ''); $mat = trim($_POST['matricula'] ?? ''); $nome = trim($_POST['nome'] ?? ''); $senha = $_POST['senha'] ?? '';
        if(!$cd || !$mat || !$nome || !$senha){ $_SESSION['flash']=['type'=>'err','msg'=>'Preencha CD, matrícula, nome e senha.']; header('Location: index.php?page=usuarios'); exit; }
        if(query_one('SELECT id_usuario FROM usuarios WHERE matricula=? AND deletado_em IS NULL',[$mat])){ $_SESSION['flash']=['type'=>'err','msg'=>'Já existe usuário com esta matrícula.']; header('Location: index.php?page=usuarios'); exit; }
        $hash = password_hash($senha, PASSWORD_DEFAULT);
        exec_sql('INSERT INTO usuarios (cd,matricula,nome,area,turno,funcao,perfil,senha_hash,ativo,usuario_movimentacao) VALUES (?,?,?,?,?,?,?,?,?,?)',[$cd,$mat,$nome,null,null,null,'USER',$hash,1,$_SESSION['user']['matricula']]);
        $_SESSION['flash']=['type'=>'ok','msg'=>'Usuário cadastrado.']; header('Location: index.php?page=usuarios'); exit;
    }
    $usuarios = query_all('SELECT id_usuario, cd, matricula, nome, area, turno, funcao, perfil, ativo FROM usuarios WHERE deletado_em IS NULL ORDER BY cd, nome');
    echo '<h3>Usuários <a class="btn" href="index.php?page=usuarios&action=novo">Cadastrar Usuário</a> <a class="btn secondary" href="index.php?page=home">Voltar</a></h3>';
    if(isset($_GET['action']) && $_GET['action']==='novo'){
        ?>
        <form method="post">
          <label>CD</label><input name="cd" required>
          <label>Matrícula</label><input name="matricula" required>
          <label>Nome</label><input name="nome" required>
          <label>Senha</label><input type="password" name="senha" required>
          <input type="hidden" name="action" value="novo_usuario">
          <br><br><button class="btn" type="submit">Salvar</button> <a class="btn secondary" href="index.php?page=usuarios">Cancelar</a>
        </form>
        <?php
        include 'footer.php'; exit;
    }
    echo '<table><thead><tr><th>CD</th><th>Matrícula</th><th>Nome</th><th>Área</th><th>Turno</th><th>Perfil</th></tr></thead><tbody>';
    foreach($usuarios as $u){ echo "<tr><td>{$u['cd']}</td><td>{$u['matricula']}</td><td>{$u['nome']}</td><td>{$u['area']}</td><td>{$u['turno']}</td><td>{$u['perfil']}</td></tr>"; }
    echo '</tbody></table>';
    include 'footer.php'; exit;
}

// RESERVAR - reservar coletor
if($page === 'reservar'){
    if($_SERVER['REQUEST_METHOD']==='POST'){
        $coletor_id = $_POST['coletor_id'] ?? ''; $mat = trim($_POST['matricula'] ?? '');
        if(!$coletor_id || !$mat){ $_SESSION['flash']=['type'=>'err','msg'=>'Selecione coletor e informe matrícula.']; header('Location: index.php?page=reservar'); exit; }
        // inserir em uso_atual
        exec_sql('INSERT INTO uso_atual (coletor_id, matricula, dt_hora_retirada, turno, usuario_movimentacao) VALUES (?,?,?,?,?)', [$coletor_id, $mat, date('Y-m-d H:i:s'), null, $_SESSION['user']['matricula']]);
        exec_sql('UPDATE coletores SET status = "EM_USO", usuario_movimentacao = ? WHERE id = ?', [$_SESSION['user']['matricula'], $coletor_id]);
        $_SESSION['flash']=['type'=>'ok','msg'=>'Coletor reservado.']; header('Location: index.php?page=home'); exit;
    }
    $disponiveis = query_all('SELECT id, cd, numero_coletor, serial, tipo_equipamento FROM coletores WHERE deletado_em IS NULL AND status="DISPONIVEL"');
    ?>
    <h3>Reservar Coletor</h3>
    <form method="post">
      <label>Coletor</label>
      <select name="coletor_id" required>
        <?php foreach($disponiveis as $c) echo "<option value='{$c['id']}'>{$c['cd']} · {$c['numero_coletor']} · {$c['serial']}</option>"; ?>
      </select>
      <label>Matrícula</label><input name="matricula" required>
      <br><br><button class="btn" type="submit">Reservar</button> <a class="btn secondary" href="index.php?page=home">Voltar</a>
    </form>
    <?php include 'footer.php'; exit;
}

// DEVOLVER - devolver coletor em uso
if($page === 'devolver'){
    if($_SERVER['REQUEST_METHOD']==='POST'){
        $coletor_id = $_POST['coletor_id'] ?? '';
        if(!$coletor_id){ $_SESSION['flash']=['type'=>'err','msg'=>'Selecione coletor.']; header('Location: index.php?page=devolver'); exit; }
        // remover uso_atual (simples): mover para historico? aqui apenas deletamos e atualizamos status
        exec_sql('DELETE FROM uso_atual WHERE coletor_id = ?', [$coletor_id]);
        exec_sql('UPDATE coletores SET status = "DISPONIVEL", usuario_movimentacao = ? WHERE id = ?', [$_SESSION['user']['matricula'], $coletor_id]);
        $_SESSION['flash']=['type'=>'ok','msg'=>'Coletor devolvido.']; header('Location: index.php?page=home'); exit;
    }
    $em_uso = query_all('SELECT ua.coletor_id, c.numero_coletor, c.tipo_equipamento, c.serial, ua.matricula, ua.dt_hora_retirada FROM uso_atual ua JOIN coletores c ON c.id = ua.coletor_id');
    ?>
    <h3>Devolver Coletor</h3>
    <form method="post">
      <label>Selecionar coletor</label>
      <select name="coletor_id" required>
        <?php foreach($em_uso as $r) echo "<option value='{$r['coletor_id']}'>{$r['numero_coletor']} · {$r['tipo_equipamento']} · {$r['serial']} · {$r['matricula']}</option>"; ?>
      </select>
      <br><br><button class="btn" type="submit">Devolver</button> <a class="btn secondary" href="index.php?page=home">Voltar</a>
    </form>
    <?php include 'footer.php'; exit;
}

// MANUTENÇÃO - enviar para manutenção
if($page === 'manutencao'){
    if($_SERVER['REQUEST_METHOD']==='POST'){
        $coletor_id = $_POST['coletor_id'] ?? ''; $status = $_POST['status'] ?? 'MANUTENCAO'; $observacao = trim($_POST['observacao'] ?? '');
        if(!$coletor_id || !$observacao){ $_SESSION['flash']=['type'=>'err','msg'=>'Selecione coletor e preencha observação.']; header('Location: index.php?page=manutencao'); exit; }
        exec_sql('UPDATE coletores SET status = ?, usuario_movimentacao = ? WHERE id = ?', [$status, $_SESSION['user']['matricula'], $coletor_id]);
        exec_sql('INSERT INTO manutencao (coletor_id, status, observacao, usuario_movimentacao, dt_hora) VALUES (?,?,?,?,?)', [$coletor_id, $status, $observacao, $_SESSION['user']['matricula'], date('Y-m-d H:i:s')]);
        $_SESSION['flash']=['type'=>'ok','msg'=>'Coletor enviado para manutenção.']; header('Location: index.php?page=home'); exit;
    }
    $coletores = query_all('SELECT id, cd, numero_coletor, serial, tipo_equipamento FROM coletores WHERE deletado_em IS NULL');
    ?>
    <h3>Enviar Coletor para Manutenção</h3>
    <form method="post">
      <label>Coletor</label><select name="coletor_id"><?php foreach($coletores as $c) echo "<option value='{$c['id']}'>{$c['numero_coletor']} · {$c['tipo_equipamento']} · {$c['serial']}</option>"; ?></select>
      <label>Status</label><select name="status"><option>MANUTENCAO</option><option>PREVENTIVA</option><option>CORRETIVA</option><option>AGUARDANDO_PECA</option></select>
      <label>Observação</label><textarea name="observacao" required></textarea>
      <br><br><button class="btn" type="submit">Enviar para manutenção</button> <a class="btn secondary" href="index.php?page=home">Voltar</a>
    </form>
    <?php include 'footer.php'; exit;
}

// fallback
echo '<p>Página não encontrada.</p>';
include 'footer.php';
?>