<?php
require_once 'conexao.php';
session_start();

function require_login(){
    if (!isset($_SESSION['user'])){
        header('Location: index.php');
        exit;
    }
}

function query_all($sql, $params = []){
    $db = conectar_banco();
    $stmt = $db->prepare($sql);
    if($stmt === false) die($db->error);
    if($params){
        $types = str_repeat('s', count($params));
        $stmt->bind_param($types, ...$params);
    }
    $stmt->execute();
    $res = $stmt->get_result();
    $rows = $res->fetch_all(MYSQLI_ASSOC);
    $stmt->close();
    $db->close();
    return $rows;
}

function query_one($sql, $params = []){
    $rows = query_all($sql, $params);
    return count($rows) ? $rows[0] : null;
}

function exec_sql($sql, $params = []){
    $db = conectar_banco();
    $stmt = $db->prepare($sql);
    if($stmt === false) die($db->error);
    if($params){
        $types = str_repeat('s', count($params));
        $stmt->bind_param($types, ...$params);
    }
    $ok = $stmt->execute();
    if(!$ok) { $err = $stmt->error; $stmt->close(); $db->close(); die('SQL Error: '.$err); }
    $stmt->close();
    $db->close();
    return true;
}

function humanize_seconds($seconds){
    if($seconds < 0) $seconds = 0;
    $m = floor($seconds / 60);
    $s = $seconds % 60;
    $h = floor($m / 60);
    $m = $m % 60;
    $d = floor($h / 24);
    $h = $h % 24;
    if($d) return "{$d}d {$h}h {$m}m";
    if($h) return "{$h}h {$m}m";
    if($m) return "{$m}m {$s}s";
    return "{$s}s";
}
?>