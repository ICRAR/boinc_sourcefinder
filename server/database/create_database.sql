CREATE SCHEMA IF NOT EXISTS sourcefinder DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE sourcefinder ;

# Runs
CREATE TABLE IF NOT EXISTS sourcefinder.`run` (
  run_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`run_id`)
) ENGINE = InnoDB;

# Parameter files
CREATE TABLE IF NOT EXISTS sourcefinder.`parameter_file` (
  parameter_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  parameter_file_name VARCHAR(100),

  PRIMARY KEY (parameter_id)
) ENGINE = InnoDB;

# Link parameters to runs
CREATE TABLE IF NOT EXISTS sourcefinder.`parameter_run` (
  parameter_run BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  run_id BIGINT NOT NULL,
  parameter_id BIGINT NOT NULL,

  PRIMARY KEY (parameter_run),

  FOREIGN KEY (run_id)
    REFERENCES sourcefinder.`run`(`run_id`),

  FOREIGN KEY (parameter_id)
    REFERENCES sourcefinder.`parameter_file` (`parameter_id`)
) ENGINE = InnoDB;

# Cube processing status
CREATE TABLE IF NOT EXISTS sourcefinder.`cube_status` (
  cube_status_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  status VARCHAR(100) NOT NULL,

  PRIMARY KEY (cube_status_id)

) ENGINE = InnoDB;

INSERT INTO sourcefinder.`cube_status` (status) VALUES ('Started');
INSERT INTO sourcefinder.`cube_status` (status) VALUES ('WorkunitCreated');
INSERT INTO sourcefinder.`cube_status` (status) VALUES ('ResultReceived');

# Cubes
CREATE TABLE IF NOT EXISTS sourcefinder.`cube` (
  cube_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  cube_name VARCHAR(2000) NOT NULL,
  progress  INT NOT NULL, #0 for registered, 1 for Work generated, 2 for assimilated
  ra FLOAT NOT NULL ,
  declin FLOAT NOT NULL ,
  freq FLOAT NOT NULL ,
  run_id BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`cube_id`),

  INDEX cube_run_index (`run_id` ASC),

  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder.`run` (`run_id`),

  FOREIGN KEY (`progress`)
    REFERENCES sourcefinder.`cube_status` (cube_status_id)
) ENGINE = InnoDB;

# Results
CREATE TABLE IF NOT EXISTS sourcefinder.`result` (
  `result_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `cube_id`   BIGINT UNSIGNED    NOT NULL,
  `parameter_id` BIGINT UNSIGNED NOT NULL,
  `run_id` BIGINT UNSIGNED NOT NULL,
  `RA` FLOAT NOT NULL,
  `DEC` FLOAT NOT NULL,
  `freq` FLOAT NOT NULL,
  `w_50` FLOAT NOT NULL,
  `w_20` FLOAT NOT NULL,
  `w_FREQ` FLOAT NOT NULL,
  `F_int` FLOAT NOT NULL,
  `F_tot` FLOAT NOT NULL,
  `F_peak` FLOAT NOT NULL,
  `Nvoxel` FLOAT NOT NULL,
  `Nchan` FLOAT NOT NULL,
  `Nspatpix` FLOAT NOT NULL,
  `workunit_name` VARCHAR(200),

  PRIMARY KEY (`result_id`),
  INDEX result_cube_index (`cube_id` ASC),

  FOREIGN KEY (`cube_id`)
  REFERENCES sourcefinder.`cube` (`cube_id`),

  FOREIGN KEY (`parameter_id`)
    REFERENCES sourcefinder.`parameter_file` (`parameter_id`),

  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder.`run` (`run_id`)

)  ENGINE = InnoDB;


