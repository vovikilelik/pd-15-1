CREATE TABLE IF NOT EXISTS "animal_types" (
	"id"	TINYINT NOT NULL,
	"name"	TEXT,
	PRIMARY KEY (id, name),
	UNIQUE (id)
);

CREATE TABLE IF NOT EXISTS "outcome_types" (
	"id"	TINYINT NOT NULL,
	"name"	TEXT,
	PRIMARY KEY (id, name),
	UNIQUE (id)
);

CREATE TABLE IF NOT EXISTS "outcome_subtypes" (
	"id"	TINYINT NOT NULL,
	"name"	TEXT,
	PRIMARY KEY (id, name),
	UNIQUE (id)
);

CREATE TABLE IF NOT EXISTS "colors" (
	"id"	SMALLINT NOT NULL,
	"name"	TEXT,
	PRIMARY KEY (id, name),
	UNIQUE (id)
);

CREATE TABLE IF NOT EXISTS "breeds" (
	"id"	SMALLINT NOT NULL,
	"name"	TEXT,
	PRIMARY KEY (id, name),
	UNIQUE (id)
);

CREATE TABLE IF NOT EXISTS "animals" (
	"id" 			TEXT,
	"name"			TEXT,
	"date_of_birth"		DATE,
	"animal_type"		TINYINT,
	"breed"			SMALLINT,
	"primary_color"		SMALLINT,
	"secondary_color"		SMALLINT,
	"outcome_subtype"	TINYINT,
	"outcome_type"		TINYINT,
	"outcome_date"		DATE,
	PRIMARY KEY (id),
	FOREIGN KEY (animal_type)
        	REFERENCES animal_types(id)
        		ON DELETE SET NULL,
	FOREIGN KEY (breed)
        	REFERENCES breeds(id)
        		ON DELETE SET NULL,
	FOREIGN KEY (primary_color)
        	REFERENCES colors(id)
        		ON DELETE SET NULL,
	FOREIGN KEY (secondary_color)
        	REFERENCES colors(id)
        		ON DELETE SET NULL,
	FOREIGN KEY (outcome_subtype)
        	REFERENCES outcome_subtypes(id)
        		ON DELETE SET NULL,
	FOREIGN KEY (outcome_type)
        	REFERENCES outcome_types(id)
        		ON DELETE SET NULL
);
