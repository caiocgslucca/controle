<?php
// conexao.php - ajuste as constantes com seus dados
define('DB_HOST', '193.203.175.97');
define('DB_USER', 'u207281299_Controle_Colet');
define('DB_PASS', '842413Ka@cgs');
define('DB_NAME', 'u207281299_Controle_Colet');
function conectar_banco(){
    $mysqli = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
    if ($mysqli->connect_errno) {
        die('Erro conexão: ' . $mysqli->connect_error);
    }
    $mysqli->set_charset('utf8mb4');
    return $mysqli;
}
?>