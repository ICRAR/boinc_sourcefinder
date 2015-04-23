CREATE SCHEMA sourcefinder;
USE sourcefinder;

CREATE TABLE parameters (
  parameters_id BIGINT UNSIGNED NOT NULL PRIMARY KEY,
  threshold SMALLINT NOT NULL,
  recon_dim SMALLINT NOT NULL,
  snr_recon  SMALLINT NOT NULL,
  scale_min  SMALLINT NOT NULL,
  min_pix  SMALLINT NOT NULL ,
  min_chan SMALLINT NOT NULL ,
  flag_growth SMALLINT NOT NULL ,
  growth_threshold FLOAT(7,7) NOT NULL ,

  INDEX (parameters_id)
)CHARACTER SET utf8 ENGINE = InnoDB;

CREATE TABLE run(
  run_id BIGINT UNSIGNED NOT NULL PRIMARY KEY ,
  supercube_name VARCHAR(15),
  completion INT NOT NULL ,

  INDEX (run_id),
  INDEX (supercube_name)
)CHARACTER SET utf8 ENGINE = InnoDB;

CREATE TABLE cube_status(
  cube_status_id BIGINT UNSIGNED NOT NULL PRIMARY KEY ,
  description VARCHAR(250) NOT NULL
)CHARACTER SET utf8 ENGINE =InnoDB;

INSERT INTO cube_status VALUES (0, 'REGISTERED');
INSERT INTO cube_status VALUES (1, 'COMPUTING');
INSERT INTO cube_status VALUES (2, 'PROCESSED');
INSERT INTO cube_status VALUES (3, 'ARCHIVED');
INSERT INTO cube_status VALUES (4, 'SOURCED'); /*We have done our sourcefinding checks in the data*/

CREATE TABLE parameters_run(
  parameters_run_id BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  parameters_id BIGINT UNSIGNED NOT NULL ,
  run_id BIGINT UNSIGNED NOT NULL ,

  FOREIGN KEY (parameters_id) REFERENCES parameters(parameters_id),
  FOREIGN KEY (run_id) REFERENCES run(run_id) ,

  INDEX  (run_id),
  INDEX (parameters_id)
) CHARACTER SET utf8 ENGINE=InnoDB

CREATE TABLE register (
  register_id BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  cube_filename VARCHAR(128) NOT NULL ,
  register_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  create_time TIMESTAMP NULL DEFAULT NULL ,
  run_id BIGINT UNSIGNED NOT NULL ,

  INDEX (cube_filename),
  INDEX (create_time, register_time),

  FOREIGN KEY (run_id) REFERENCES run(run_id)
) CHARACTER SET utf8 ENGINE = InnoDb;

CREATE TABLE cube (
  cube_id BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  cube_name VARCHAR(128) NOT NULL ,
  ra  FLOAT NOT NULL ,
  dec FLOAT NOT NULL ,
  frequency FLOAT NOT NULL,
  status_id SMALLINT UNSIGNED NOT NULL DEFAULT 0,
  run_id BIGINT UNSIGNED NOT NULL,

  FOREIGN KEY (run_id) REFERENCES run(run_id),
  FOREIGN KEY (status_id) REFERENCES cube_status(cube_id),

  INDEX (run_id),
  INDEX (cube_name)
) CHARACTER SET utf8 ENGINE = InnoDB;

CREATE TABLE results (
  result_id BIGINT UNSIGNED NOT NULL PRIMARY KEY AUTO_INCREMENT,
  parameter_id BIGINT UNSIGNED NOT NULL,
  cube_name VARCHAR(128) NOT NULL ,
  sources_found SMALLINT NOT NULL,
  correct_sources SMALLINT NOT NULL,

  FOREIGN KEY (parameter_id) REFERENCES parameters(parameters_id),
  FOREIGN KEY (cube_name) REFERENCES cube(cube_id),

  INDEX (result_id)
)



