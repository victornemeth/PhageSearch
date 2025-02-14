-- Create table for species information
CREATE TABLE species (
    primary_key INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(255),
    natural_host VARCHAR(255),
    lab_host VARCHAR(255),
    virus_name VARCHAR(255),
    dbxref VARCHAR(255)
);

-- Create table for protein information
CREATE TABLE proteins (
    primary_key INT AUTO_INCREMENT PRIMARY KEY,
    species_primary_key INT,
    source VARCHAR(255),
    seq_region VARCHAR(50),
    id VARCHAR(255),
    cds_start INT,
    cds_end INT,
    dbxref VARCHAR(700),
    note TEXT,
    product VARCHAR(255),
    protein_id VARCHAR(255),
    UniProt_Ref VARCHAR(255),
    FOREIGN KEY (species_primary_key) REFERENCES species(primary_key)
);

CREATE TABLE sequences (
    primary_key INT AUTO_INCREMENT PRIMARY KEY,
    proteins_primary_key INT,
    seq VARCHAR(10000),
    FOREIGN KEY (proteins_primary_key) REFERENCES proteins(primary_key)
);

-- Create table for protein information
CREATE TABLE structures (
    primary_key INT AUTO_INCREMENT PRIMARY KEY,
    proteins_primary_key INT,
    pdb_id VARCHAR(255),
    metadata VARCHAR(255),
    pdb_file VARCHAR(255),
    FOREIGN KEY (proteins_primary_key) REFERENCES proteins(primary_key)
);