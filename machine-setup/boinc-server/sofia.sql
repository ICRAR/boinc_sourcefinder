DROP SCHEMA IF EXISTS sourcefinder_sofia;
CREATE SCHEMA IF NOT EXISTS sourcefinder_sofia DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE sourcefinder_sofia ;

# Runs
CREATE TABLE IF NOT EXISTS sourcefinder_sofia.`run` (
  run_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`run_id`)
) ENGINE = InnoDB;

# Parameter files
CREATE TABLE IF NOT EXISTS sourcefinder_sofia.`parameter_file` (
  parameter_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  parameter_file_name VARCHAR(100),

  PRIMARY KEY (parameter_id)
) ENGINE = InnoDB;

# Link parameters to runs
CREATE TABLE IF NOT EXISTS sourcefinder_sofia.`parameter_run` (
  parameter_run BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  run_id BIGINT UNSIGNED NOT NULL,
  parameter_id BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (parameter_run),

  FOREIGN KEY (run_id)
    REFERENCES sourcefinder_sofia.`run`(`run_id`),

  FOREIGN KEY (parameter_id)
    REFERENCES sourcefinder_sofia.`parameter_file` (`parameter_id`)
) ENGINE = InnoDB;

# Cube processing status
CREATE TABLE IF NOT EXISTS sourcefinder_sofia.`cube_status` (
  cube_status_id BIGINT UNSIGNED NOT NULL,
  status VARCHAR(100) NOT NULL,

  PRIMARY KEY (cube_status_id)

) ENGINE = InnoDB;

INSERT INTO sourcefinder_sofia.`cube_status` (cube_status_id, status) VALUES (0, 'Started');
INSERT INTO sourcefinder_sofia.`cube_status` (cube_status_id, status) VALUES (1, 'WorkunitCreated');
INSERT INTO sourcefinder_sofia.`cube_status` (cube_status_id, status) VALUES (2, 'ResultReceived');

# Cubes
CREATE TABLE IF NOT EXISTS sourcefinder_sofia.`cube` (
  cube_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  cube_name VARCHAR(2000) NOT NULL,
  progress  BIGINT UNSIGNED NOT NULL, #0 for registered, 1 for Work generated, 2 for assimilated
  ra FLOAT NOT NULL ,
  declin FLOAT NOT NULL ,
  freq FLOAT NOT NULL ,
  run_id BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`cube_id`),

  INDEX cube_run_index (`run_id` ASC),

  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder_sofia.`run` (`run_id`),

  FOREIGN KEY (`progress`)
    REFERENCES sourcefinder_sofia.`cube_status` (cube_status_id)
) ENGINE = InnoDB;

# Results
CREATE TABLE IF NOT EXISTS sourcefinder_sofia.`result` (
  `result_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `cube_id`   BIGINT UNSIGNED    NOT NULL,
  `parameter_id` BIGINT UNSIGNED NOT NULL,
  `run_id` BIGINT UNSIGNED NOT NULL,

  `id` DOUBLE,
  `name` VARCHAR(200),
  `x` DOUBLE,
  `y` DOUBLE,
  `z` DOUBLE,
  `x_geo` DOUBLE,
  `y_geo` DOUBLE,
  `z_geo` DOUBLE,
  `rms` DOUBLE,
  `rel` DOUBLE,
  `x_min` DOUBLE,
  `x_max` DOUBLE,
  `y_min` DOUBLE,
  `y_max` DOUBLE,
  `z_min` DOUBLE,
  `z_max` DOUBLE,
  `n_pix` DOUBLE,
  `n_los` DOUBLE,
  `n_chan` DOUBLE,
  `ra` DOUBLE,
  `dec` DOUBLE,
  `lon` DOUBLE,
  `lat` DOUBLE,
  `freq` DOUBLE,
  `velo` DOUBLE,
  `w20` DOUBLE,
  `w50` DOUBLE,
  `wm50` DOUBLE,
  `f_peak` DOUBLE,
  `f_int` DOUBLE,
  `f_wm50` DOUBLE,
  `ell_maj` DOUBLE,
  `ell_min` DOUBLE,
  `ell_pa` DOUBLE,
  `ell3s_maj` DOUBLE,
  `ell3s_min` DOUBLE,
  `ell3s_pa` DOUBLE,
  `kin_pa` DOUBLE,
  `bf_a` DOUBLE,
  `bf_b1` DOUBLE,
  `bf_b2` DOUBLE,
  `bf_c` DOUBLE,
  `bf_xe` DOUBLE,
  `bf_xp` DOUBLE,
  `bf_w` DOUBLE,
  `bf_chi2` DOUBLE,
  `bf_flag` DOUBLE,
  `bf_z` DOUBLE,
  `bf_w20` DOUBLE,
  `bf_w50` DOUBLE,
  `bf_f_peak` DOUBLE,
  `bf_f_int` DOUBLE,
  `workunit_name` VARCHAR(200),

  PRIMARY KEY (`result_id`),
  INDEX result_cube_index (`cube_id` ASC),

  FOREIGN KEY (`cube_id`)
  REFERENCES sourcefinder_sofia.`cube` (`cube_id`),

  FOREIGN KEY (`parameter_id`)
    REFERENCES sourcefinder_sofia.`parameter_file` (`parameter_id`),

  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder_sofia.`run` (`run_id`)

)  ENGINE = InnoDB;


