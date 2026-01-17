CREATE TABLE missions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  slug VARCHAR(64) NOT NULL UNIQUE,
  name VARCHAR(255) NOT NULL,
  location VARCHAR(255),
  description TEXT,
  verse_text TEXT,
  verse_ref VARCHAR(255),
  meeting_link VARCHAR(255)
);

CREATE INDEX idx_missions_slug ON missions (slug);

CREATE TABLE mission_about (
  mission_id INT PRIMARY KEY,
  summary TEXT,
  mission TEXT,
  vision TEXT,
  team TEXT,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE TABLE mission_values (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mission_id INT NOT NULL,
  value VARCHAR(255) NOT NULL,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE TABLE mission_help (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mission_id INT NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_mission_help_mission ON mission_help (mission_id);

CREATE TABLE mission_contact (
  mission_id INT PRIMARY KEY,
  email VARCHAR(255),
  phone VARCHAR(64),
  address TEXT,
  hours VARCHAR(255),
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE TABLE mission_contact_social (
  mission_id INT PRIMARY KEY,
  instagram VARCHAR(255),
  facebook VARCHAR(255),
  site VARCHAR(255),
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE TABLE mission_projects (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mission_id INT NOT NULL,
  project_key VARCHAR(64) NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(64),
  meeting_link VARCHAR(255),
  budget DECIMAL(10, 2) DEFAULT 0,
  closed_at DATE,
  UNIQUE KEY uniq_project (mission_id, project_key),
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_projects_mission ON mission_projects (mission_id);
CREATE INDEX idx_projects_status ON mission_projects (status);

CREATE TABLE project_tasks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mission_id INT NOT NULL,
  project_key VARCHAR(64) NOT NULL,
  title VARCHAR(255) NOT NULL,
  status VARCHAR(32),
  assignee VARCHAR(255),
  weight DECIMAL(10, 2) DEFAULT 1,
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_tasks_mission ON project_tasks (mission_id);
CREATE INDEX idx_tasks_project ON project_tasks (project_key);

CREATE TABLE mission_users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mission_id INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  institutional_email VARCHAR(255),
  role VARCHAR(64),
  status VARCHAR(32),
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_users_mission ON mission_users (mission_id);
CREATE INDEX idx_users_email ON mission_users (email);

CREATE TABLE chat_messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mission_id INT NOT NULL,
  from_email VARCHAR(255),
  from_name VARCHAR(255),
  to_email VARCHAR(255),
  message TEXT,
  sent_at VARCHAR(64),
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_chat_mission ON chat_messages (mission_id);

CREATE TABLE finance_entries (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mission_id INT NOT NULL,
  date DATE,
  type VARCHAR(16),
  amount DECIMAL(10, 2),
  description TEXT,
  category VARCHAR(255),
  receipt_link VARCHAR(255),
  project_key VARCHAR(64),
  created_by VARCHAR(255),
  created_at VARCHAR(64),
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_finance_mission ON finance_entries (mission_id);
CREATE INDEX idx_finance_project ON finance_entries (project_key);

CREATE TABLE finance_reports (
  id INT AUTO_INCREMENT PRIMARY KEY,
  mission_id INT NOT NULL,
  report_json LONGTEXT,
  created_by VARCHAR(255),
  created_at VARCHAR(64),
  FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE INDEX idx_reports_mission ON finance_reports (mission_id);

INSERT INTO missions (slug, name, location, description, verse_text, verse_ref, meeting_link) VALUES
  ('ide', 'Ide e Pregai', 'Global', 'Plataforma para tornar visivel o evangelho em movimento.', 'Ide por todo o mundo e pregai o evangelho a toda criatura.', 'Marcos 16:15', NULL),
  ('vidanova', 'Missao Vida Nova', 'Brasil', 'Apoio comunitario, evangelismo e cuidado com familias.', 'Assim brilhe a luz de voces diante dos homens.', 'Mateus 5:16', NULL),
  ('teste', 'Missao Teste', 'Brasil', 'Missao de exemplo para testes de roles e permissoes.', 'Tudo o que fizerem, facam de todo coracao.', 'Colossenses 3:23', 'https://meet.google.com/missao-teste');

INSERT INTO mission_about (mission_id, summary, mission, vision, team) VALUES
  (1, 'Rede de apoio que conecta missoes e pessoas que oram e servem.', 'Fortalecer o trabalho missionario com clareza, cuidado e unidade.', 'Ver comunidades alcancadas por meio de equipes locais bem acompanhadas.', 'Voluntarios, intercessores e lideres de campo.'),
  (2, 'Frente missionaria que atua com familias em situacao de risco.', 'Levar acolhimento, ensino biblico e suporte social.', 'Comunidades restauradas e novas liderancas locais.', 'Equipe local com educadores, voluntarios e lideres.'),
  (3, 'Missao de referencia para validar fluxos internos.', 'Treinar processos com simplicidade e seguranca.', 'Ter dados claros e operacao organizada.', 'Equipe de teste e voluntarios.');

INSERT INTO mission_values (mission_id, value) VALUES
  (1, 'Compromisso'),
  (1, 'Cuidado'),
  (1, 'Transparencia'),
  (2, 'Misericordia'),
  (2, 'Responsabilidade'),
  (2, 'Servir'),
  (3, 'Transparencia'),
  (3, 'Cuidado'),
  (3, 'Servir');

INSERT INTO mission_help (mission_id, title, description) VALUES
  (1, 'Intercessao', 'Participe dos ciclos de oracao semanais e receba temas atualizados.'),
  (1, 'Apoio local', 'Contribua com hospedagem, logistica ou pontos de apoio.'),
  (1, 'Parcerias', 'Igrejas e grupos podem adotar frentes missionarias em oracao.'),
  (2, 'Doacoes de mantimentos', 'Itens basicos para manter o atendimento diario.'),
  (2, 'Voluntariado', 'Ajuda presencial com aulas, visitas e suporte logistico.'),
  (3, 'Apoio em oracao', 'Intercessao semanal pela missao.');

INSERT INTO mission_contact (mission_id, email, phone, address, hours) VALUES
  (1, 'contato@ideepregai.org', '+55 11 90000-0000', 'Base itinerante, contato por agenda.', 'Seg a sex, 9h as 18h'),
  (2, 'contato@vidanova.org', '+55 31 90000-0000', 'Regiao central, Brasil.', 'Seg a sab, 8h as 17h'),
  (3, 'contato@missao-teste.org', '+55 11 91111-1111', 'Base de testes, Brasil.', 'Seg a sex, 9h as 18h');

INSERT INTO mission_contact_social (mission_id, instagram, facebook, site) VALUES
  (1, 'https://instagram.com/ideepregai', '', 'https://ideepregai.org'),
  (2, 'https://instagram.com/missaovidanova', 'https://facebook.com/missaovidanova', ''),
  (3, '', '', '');

INSERT INTO mission_projects (mission_id, project_key, title, description, status, meeting_link, budget, closed_at) VALUES
  (1, 'mapa-de-missoes', 'Mapa de missoes', 'Levantamento simples das frentes missionarias ativas.', 'em_andamento', NULL, 0, NULL),
  (1, 'rede-de-oracao', 'Rede de oracao', 'Calendario semanal de intercessao por equipes no campo.', 'em_andamento', NULL, 0, NULL),
  (1, 'kit-de-apoio', 'Kit de apoio', 'Materiais basicos para comunicacao com igrejas e apoiadores.', 'em_planejamento', NULL, 0, NULL),
  (2, 'casa-de-apoio', 'Casa de apoio', 'Espaco seguro para familias em vulnerabilidade temporaria.', 'em_andamento', NULL, 0, NULL),
  (2, 'escola-de-discipulado', 'Escola de discipulado', 'Turmas semanais para novos convertidos e lideres.', 'em_andamento', NULL, 0, NULL),
  (3, 'projeto-piloto', 'Projeto piloto', 'Fluxo inicial para testar publicacoes.', 'em_andamento', 'https://meet.google.com/abc-defg-hij', 2000, NULL),
  (3, 'projeto-encerrado', 'Projeto encerrado', 'Projeto concluido com prestacao de contas finalizada.', 'concluida', NULL, 500, '2023-01-10');

INSERT INTO project_tasks (mission_id, project_key, title, status, assignee, weight) VALUES
  (3, 'projeto-piloto', 'Definir entregas principais', 'done', 'Luis Lider', 2),
  (3, 'projeto-piloto', 'Reunir materiais base', 'doing', 'Nina Voluntaria', 1),
  (3, 'projeto-piloto', 'Publicar primeira atualizacao', 'todo', 'Eli Editor', 1);

INSERT INTO mission_users (mission_id, name, email, institutional_email, role, status) VALUES
  (3, 'Ana Admin', 'ana.admin@missao-teste.org', 'ana.admin@missao-teste.org', 'admin', 'active'),
  (3, 'Luis Lider', 'luis.lider@missao-teste.org', 'luis.lider@missao-teste.org', 'lider', 'active'),
  (3, 'Eli Editor', 'eli.editor@missao-teste.org', 'eli.editor@missao-teste.org', 'editor', 'active'),
  (3, 'Fabi Financeiro', 'fabi.financeiro@missao-teste.org', 'fabi.financeiro@missao-teste.org', 'financeiro', 'active'),
  (3, 'Nina Voluntaria', 'nina.voluntaria@missao-teste.org', 'nina.voluntaria@missao-teste.org', 'voluntario', 'active'),
  (3, 'Paulo Apoiador', 'paulo.apoiador@missao-teste.org', 'paulo.apoiador@missao-teste.org', 'apoiador', 'active');

INSERT INTO chat_messages (mission_id, from_email, from_name, to_email, message, sent_at) VALUES
  (3, 'luis.lider@missao-teste.org', 'Luis Lider', 'nina.voluntaria@missao-teste.org', 'Vamos alinhar as tarefas do projeto piloto hoje?', '2024-01-15 10:30'),
  (3, 'nina.voluntaria@missao-teste.org', 'Nina Voluntaria', 'luis.lider@missao-teste.org', 'Sim, posso revisar a lista agora a tarde.', '2024-01-15 11:10');

INSERT INTO finance_entries (mission_id, date, type, amount, description, category, receipt_link, project_key, created_by, created_at) VALUES
  (3, '2024-01-10', 'entrada', 1500, 'Oferta mensal da igreja', 'Doacoes', '', NULL, 'fabi.financeiro@missao-teste.org', '2024-01-10 09:00:00 UTC'),
  (3, '2024-01-12', 'saida', 420, 'Material para projeto piloto', 'Recursos', 'https://exemplo.org/comprovante/123', 'projeto-piloto', 'fabi.financeiro@missao-teste.org', '2024-01-12 15:20:00 UTC');
