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

  `id` INT,
  `name` VARCHAR(200),
  `x` FLOAT,
  `y` FLOAT,
  `z` FLOAT,
  `x_geo` FLOAT,
  `y_geo` FLOAT,
  `z_geo` FLOAT,
  `rms` FLOAT,
  `rel` FLOAT,
  `x_min` FLOAT,
  `x_max` FLOAT,
  `y_min` FLOAT,
  `y_max` FLOAT,
  `z_min` FLOAT,
  `z_max` FLOAT,
  `n_pix` FLOAT,
  `n_los` FLOAT,
  `n_chan` FLOAT,
  `ra` FLOAT,
  `dec` FLOAT,
  `lon` FLOAT,
  `lat` FLOAT,
  `freq` FLOAT,
  `velo` FLOAT,
  `w20` FLOAT,
  `w50` FLOAT,
  `wm50` FLOAT,
  `f_peak` FLOAT,
  `f_int` FLOAT,
  `f_wm50` FLOAT,
  `ell_maj` FLOAT,
  `ell_min` FLOAT,
  `ell_pa` FLOAT,
  `ell3s_maj` FLOAT,
  `ell3s_min` FLOAT,
  `ell3s_pa` FLOAT,
  `kin_pa` FLOAT,
  `bf_a` FLOAT,
  `bf_b1` FLOAT,
  `bf_b2` FLOAT,
  `bf_c` FLOAT,
  `bf_xe` FLOAT,
  `bf_xp` FLOAT,
  `bf_w` FLOAT,
  `bf_chi2` FLOAT,
  `bf_flag` FLOAT,
  `bf_z` FLOAT,
  `bf_w20` FLOAT,
  `bf_w50` FLOAT,
  `bf_f_peak` FLOAT,
  `bf_f_int` FLOAT,
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


