CREATE TABLE diseases(
    disease_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    disease_name VARCHAR(150) NOT NULL UNIQUE,
    synonym VARCHAR(150) NULL,
    omim VARCHAR(10) NULL,
    orphanet VARCHAR(10) NULL,
    protein VARCHAR(255) NULL,
    expasy VARCHAR(50) NULL,
    gene_locus VARCHAR(255) NULL,
    icd VARCHAR(50) NULL,
    summary TEXT NOT NULL,
	  lookup_id INT UNSIGNED NOT NULL
);

-- ALTER TABLE diseases ADD UNIQUE(disease_name);

CREATE TABLE symptoms(
    symptom_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    symptom_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL,
    disease_id INT UNSIGNED NOT NULL,
    FOREIGN KEY(disease_id) REFERENCES diseases(disease_id)
);
-- 
-- ALTER TABLE symptoms ADD UNIQUE(symptom_name);

CREATE TABLE literature(
    literature_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    link VARCHAR(120) NOT NULL,
    author VARCHAR(50) NOT NULL,
    journal VARCHAR(255) NOT NULL,
    disease_id INT UNSIGNED NOT NULL,
    FOREIGN KEY(disease_id) REFERENCES diseases(disease_id)
);


CREATE TABLE lab(
    lab_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    metabolite VARCHAR(100) NOT NULL,
    specimen VARCHAR(30) NULL,
    agegroup VARCHAR(30) NULL,
    min_value VARCHAR(10) NULL,
    max_value VARCHAR(10) NULL,
    unit VARCHAR(25) NULL,
    disease_id INT UNSIGNED NOT NULL,
    FOREIGN KEY(disease_id) REFERENCES diseases(disease_id)
);

CREATE TABLE normal_specimens(
    ns_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    metabolite VARCHAR(100) NOT NULL,
    min_value VARCHAR(10) NULL,
    max_value VARCHAR(10) NULL,
    unit VARCHAR(25) NOT NULL,
    specimen VARCHAR(30) NOT NULL,
    agegroup VARCHAR(30) NOT NULL,
    method VARCHAR(10) NULL,
    disease_id INT UNSIGNED NOT NULL,
    FOREIGN KEY(disease_id) REFERENCES diseases(disease_id)
);

CREATE TABLE disease_symptom(
		ds_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
		disease_id INT UNSIGNED NOT NULL,
		symptom_id INT UNSIGNED NOT NULL,
		FOREIGN KEY(disease_id) REFERENCES diseases(disease_id),
		FOREIGN KEY(symptom_id) REFERENCES symptoms(symptom_id)
);

CREATE TABLE disease_literature(
		dl_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
		disease_id INT UNSIGNED NOT NULL,
		literature_id INT UNSIGNED NOT NULL,
		FOREIGN KEY(disease_id) REFERENCES diseases(disease_id),
		FOREIGN KEY(literature_id) REFERENCES literature(literature_id)
);


