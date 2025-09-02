<?php
require_once 'functions.php';
header('Content-Type: application/json; charset=utf-8');
$mat = $_GET['matricula'] ?? '';
$mat = trim($mat);
if(!$mat){ echo json_encode(['ok'=>false,'msg'=>'matricula requerida']); exit; }
$row = query_one('SELECT id_usuario, matricula, nome, area, turno, funcao, perfil, ativo FROM usuarios WHERE deletado_em IS NULL AND matricula = ? LIMIT 1', [$mat]);
if(!$row) echo json_encode(['ok'=>true,'exists'=>false,'usuario'=>null]);
else echo json_encode(['ok'=>true,'exists'=>true,'usuario'=>$row]);
?>