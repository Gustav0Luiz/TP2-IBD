PRAGMA foreign_keys = ON;

CREATE TABLE RacaCor (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE EtniaIndigena (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE UF (sigla TEXT PRIMARY KEY, nome TEXT);
CREATE TABLE Municipio (
    codigo TEXT PRIMARY KEY,
    nome TEXT,
    uf_sigla TEXT,
    FOREIGN KEY (uf_sigla) REFERENCES UF(sigla)
);
CREATE TABLE Fabricante (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE DoseVacina (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE GrupoAtendimento (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE CategoriaAtendimento (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE TipoEstabelecimento (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE NaturezaEstabelecimento (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE LocalAplicacao (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE ViaAdministracao (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE EstrategiaVacinacao (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE CondicaoMaternal (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE OrigemRegistro (codigo TEXT PRIMARY KEY, descricao TEXT);
CREATE TABLE SistemaOrigem (codigo TEXT PRIMARY KEY, descricao TEXT);

CREATE TABLE Paciente (
    id TEXT PRIMARY KEY,
    sexo TEXT,
    idade INTEGER,
    cep TEXT,
    nacionalidade TEXT,
    raca_cor_fk TEXT,
    municipio_fk TEXT,
    etnia_indigena_fk TEXT,
    FOREIGN KEY (raca_cor_fk) REFERENCES RacaCor(codigo),
    FOREIGN KEY (municipio_fk) REFERENCES Municipio(codigo),
    FOREIGN KEY (etnia_indigena_fk) REFERENCES EtniaIndigena(codigo)
);

CREATE TABLE Estabelecimento (
    id TEXT PRIMARY KEY,
    razao_social TEXT,
    nome_fantasia TEXT,
    municipio_fk TEXT,
    tipo_fk TEXT,
    natureza_fk TEXT,
    FOREIGN KEY (municipio_fk) REFERENCES Municipio(codigo),
    FOREIGN KEY (tipo_fk) REFERENCES TipoEstabelecimento(codigo),
    FOREIGN KEY (natureza_fk) REFERENCES NaturezaEstabelecimento(codigo)
);

CREATE TABLE Vacina (
    id TEXT PRIMARY KEY,
    descricao TEXT,
    sigla TEXT,
    fabricante_fk TEXT,
    grupo_atendimento_fk TEXT,
    categoria_atendimento_fk TEXT,
    FOREIGN KEY (fabricante_fk) REFERENCES Fabricante(codigo),
    FOREIGN KEY (grupo_atendimento_fk) REFERENCES GrupoAtendimento(codigo),
    FOREIGN KEY (categoria_atendimento_fk) REFERENCES CategoriaAtendimento(codigo)
);

CREATE TABLE Aplicacao (
    id TEXT PRIMARY KEY,
    data_aplicacao TEXT,
    lote TEXT,
    status_documento TEXT,
    paciente_fk TEXT,
    vacina_fk TEXT,
    estabelecimento_fk TEXT,
    dose_fk TEXT,
    local_aplicacao_fk TEXT,
    via_administracao_fk TEXT,
    estrategia_fk TEXT,
    condicao_maternal_fk TEXT,
    origem_registro_fk TEXT,
    sistema_origem_fk TEXT,
    FOREIGN KEY (paciente_fk) REFERENCES Paciente(id),
    FOREIGN KEY (vacina_fk) REFERENCES Vacina(id),
    FOREIGN KEY (estabelecimento_fk) REFERENCES Estabelecimento(id),
    FOREIGN KEY (dose_fk) REFERENCES DoseVacina(codigo),
    FOREIGN KEY (local_aplicacao_fk) REFERENCES LocalAplicacao(codigo),
    FOREIGN KEY (via_administracao_fk) REFERENCES ViaAdministracao(codigo),
    FOREIGN KEY (estrategia_fk) REFERENCES EstrategiaVacinacao(codigo),
    FOREIGN KEY (condicao_maternal_fk) REFERENCES CondicaoMaternal(codigo),
    FOREIGN KEY (origem_registro_fk) REFERENCES OrigemRegistro(codigo),
    FOREIGN KEY (sistema_origem_fk) REFERENCES SistemaOrigem(codigo)
);
