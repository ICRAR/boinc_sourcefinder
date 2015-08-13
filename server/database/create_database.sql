CREATE SCHEMA IF NOT EXISTS sourcefinder DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE sourcefinder ;

CREATE TABLE IF NOT EXISTS sourcefinder.`run` (
  run_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`run_id`)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`parameter_file` (
  parameter_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  run_id BIGINT UNSIGNED NOT NULL,
  parameter_file VARCHAR(100),

  PRIMARY KEY (parameter_id),
  FOREIGN KEY (run_id)
  REFERENCES sourcefinder.run(run_id)

) ENGINE = InnoDB;



CREATE TABLE IF NOT EXISTS sourcefinder.`cube` (
  cube_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  cube_name VARCHAR(2000) NOT NULL,
  progress  INT NOT NULL, #0 for registere, 1 for Work generated, 2 for validated, 3 for assimilated
  ra FLOAT NOT NULL ,
  declin FLOAT NOT NULL ,
  freq FLOAT NOT NULL ,
  run_id BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`cube_id`),
  INDEX cube_run_index (`run_id` ASC),

  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder.`run` (`run_id`)
)ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`result` (
  `result_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `cube_id`   BIGINT UNSIGNED    NOT NULL,

  PRIMARY KEY (`result_id`),
  INDEX result_cube_index (`cube_id` ASC),

  FOREIGN KEY (`cube_id`)
  REFERENCES sourcefinder.`cube` (`cube_id`)
)  ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`cube_user` (
  `cube_user_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `cube_id` BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`cube_user_id`),
  INDEX `user_id_index` (`user_id` ASC),
  INDEX `user_index` (`cube_id` ASC),
  INDEX `user_cube_index` (`user_id` ASC, `cube_id` ASC),

  FOREIGN KEY (`cube_id`)
  REFERENCES sourcefinder.`cube` (`cube_id`)
) ENGINE = InnoDB;


