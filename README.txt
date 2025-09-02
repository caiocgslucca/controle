Como usar este pacote PHP (deploy na Hostinger - hospedagem compartilhada)
1) Faça upload da pasta 'coletor_php' para public_html no painel da Hostinger (via FTP ou File Manager).
2) Ajuste arquivo conexao.php com as credenciais do banco, se necessário.
3) Certifique-se de que as tabelas do seu banco correspondem aos nomes usados: usuarios, coletores, uso_atual, manutencao.
   - A estrutura mínima esperada (exemplo):
     usuarios(id_usuario INT AUTO_INCREMENT PRIMARY KEY, cd VARCHAR(50), matricula VARCHAR(50), nome VARCHAR(255), area VARCHAR(255), turno VARCHAR(100),
              funcao VARCHAR(255), perfil VARCHAR(50), senha_hash VARCHAR(255), ativo TINYINT DEFAULT 1, deletado_em DATETIME NULL, usuario_movimentacao VARCHAR(50))
     coletores(id INT AUTO_INCREMENT PRIMARY KEY, cd VARCHAR(50), numero_coletor VARCHAR(50), serial VARCHAR(100), tipo_equipamento VARCHAR(255), status VARCHAR(50), deletado_em DATETIME NULL, usuario_movimentacao VARCHAR(50))
     uso_atual(id INT AUTO_INCREMENT PRIMARY KEY, coletor_id INT, matricula VARCHAR(50), dt_hora_retirada DATETIME, turno VARCHAR(50), usuario_movimentacao VARCHAR(50))
     manutencao(id INT AUTO_INCREMENT PRIMARY KEY, coletor_id INT, status VARCHAR(50), observacao TEXT, usuario_movimentacao VARCHAR(50), dt_hora DATETIME)
4) Acesse via browser: https://SEU_DOMINIO/index.php
5) Para importar CSVs e funcionalidades mais avançadas você pode estender as rotas já existentes.
Observações:
- Este é um port simplificado do app Flask -> PHP. Preservamos a lógica principal (login, CRUD básico, reservar, devolver, manutenção, API de usuário).
- Validações, proteção CSRF e controles de permissões podem ser incrementados conforme necessário.
