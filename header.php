<?php
if(session_status() === PHP_SESSION_NONE) session_start();
$user = isset($_SESSION['user']) ? $_SESSION['user'] : null;
?>
<!doctype html><html lang="pt-br"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title><?php echo htmlspecialchars($title ?? 'Controle de Coletores'); ?></title>
<style>
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu;background:#0e1117;color:#e6edf3}
.wrap{max-width:1100px;margin:0 auto;padding:20px}
.card{background:#161b22;border:1px solid #30363d;border-radius:12px;padding:16px}
.btn{display:inline-block;padding:8px 12px;border-radius:8px;border:1px solid #30363d;background:#238636;color:#fff;text-decoration:none}
.btn.secondary{background:#21262d}
.grid{display:flex;gap:16px;flex-wrap:wrap}
.muted{color:#8b949e}
table{width:100%;border-collapse:collapse}
th,td{padding:8px;border-bottom:1px solid #30363d;text-align:left}
input,select,textarea{width:100%;padding:8px;border-radius:8px;border:1px solid #30363d;background:#0d1117;color:#e6edf3}
</style>
</head><body><div class="wrap">
<div class="flex" style="display:flex;justify-content:space-between;align-items:center">
  <h2><?php echo htmlspecialchars($header ?? 'Controle de Coletores'); ?></h2>
  <div>
    <?php if($user): ?>
      <a class="btn" href="index.php?page=home">Início</a>
      <a class="btn secondary" href="index.php?page=logout">Sair</a>
    <?php else: ?>
      <a class="btn" href="index.php">Login</a>
    <?php endif; ?>
  </div>
</div>
<br />
<?php if(isset($_SESSION['flash'])): $f=$_SESSION['flash']; unset($_SESSION['flash']); ?>
  <div class="card" style="border-color:<?php echo $f['type']=='ok'? '#1f6f3f':'#8b3434' ?>;background:<?php echo $f['type']=='ok'?'#132d19':'#2a1618' ?>"><?php echo htmlspecialchars($f['msg']); ?></div><br>
<?php endif; ?>
<div class="card">