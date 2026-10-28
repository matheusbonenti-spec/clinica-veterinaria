CREATE DATABASE IF NOT EXISTS clinica_veterinaria;
USE clinica_veterinaria;

DROP TABLE IF EXISTS agendamentos;
DROP TABLE IF EXISTS pets;
DROP TABLE IF EXISTS tutores;
DROP TABLE IF EXISTS usuarios;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL
);

CREATE TABLE tutores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf_criptografado VARCHAR(255) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    endereco VARCHAR(150) NOT NULL
);

CREATE TABLE pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_pet VARCHAR(50) NOT NULL,
    especie VARCHAR(50) NOT NULL,
    raca VARCHAR(50) NOT NULL,
    categoria VARCHAR(50) NOT NULL DEFAULT 'Terrestre',
    id_tutor INT NOT NULL,
    FOREIGN KEY (id_tutor) REFERENCES tutores(id) ON DELETE CASCADE
);

CREATE TABLE agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_hora DATETIME NOT NULL,
    motivo VARCHAR(255) NOT NULL,
    id_tutor INT NOT NULL,
    id_pet INT NOT NULL,
    FOREIGN KEY (id_tutor) REFERENCES tutores(id) ON DELETE CASCADE,
    FOREIGN KEY (id_pet) REFERENCES pets(id) ON DELETE CASCADE
);

USE clinica_veterinaria;

ALTER TABLE pets ADD COLUMN categoria VARCHAR(50) NOT NULL DEFAULT 'Terrestre';

-- Dados Iniciais
INSERT INTO usuarios (nome, email, senha) VALUES 
('matheus bonenti', 'matheusbonenti@gmail.com', '123'),
('Carlos Lima', 'carlos@vet.com', '123456'),
('Beatriz Costa', 'beatriz@vet.com', '123456');

INSERT INTO tutores (nome, cpf_criptografado, telefone, endereco) VALUES 
('bonenti', '13529195910', '41988559392', 'Rua dos canarios, 452'),
('João Pereira', 'enc_222.333.444-55', '(41) 98766-2222', 'Av. Central, 456'),
('Fernanda Souza', 'enc_333.444.555-66', '(41) 97111-3333', 'Rua XV de Novembro, 789');

INSERT INTO pets (nome_pet, especie, raca, categoria, id_tutor) VALUES 
('amilton', 'urubu-rei', 'nordestino', 'Aéreo', 1),
('bufo regularis', 'sapo', 'venenoso', 'Anfíbio', 2),
('orochinho', 'cobra', 'jiboia arco iris', 'Terrestre', 3);

INSERT INTO agendamentos (data_hora, motivo, id_tutor, id_pet) VALUES 
('2026-06-10 09:00:00', 'depilação de minhoca', 1, 1),
('2026-06-11 14:30:00', 'aparelho auditivo para morcego', 2, 2),
('2026-06-12 10:15:00', 'Banho e tosa do bufo regularis', 3, 3);


USE clinica_veterinaria;

-- Recria as chaves estrangeiras com suporte a exclusão em cascata (Cascade Delete)
ALTER TABLE pets DROP FOREIGN KEY pets_ibfk_1;
ALTER TABLE pets ADD CONSTRAINT pets_ibfk_1 FOREIGN KEY (id_tutor) REFERENCES tutores(id) ON DELETE CASCADE;

ALTER TABLE agendamentos DROP FOREIGN KEY agendamentos_ibfk_1;
ALTER TABLE agendamentos ADD CONSTRAINT agendamentos_ibfk_1 FOREIGN KEY (id_tutor) REFERENCES tutores(id) ON DELETE CASCADE;

ALTER TABLE agendamentos DROP FOREIGN KEY agendamentos_ibfk_2;
ALTER TABLE agendamentos ADD CONSTRAINT agendamentos_ibfk_2 FOREIGN KEY (id_pet) REFERENCES pets(id) ON DELETE CASCADE;