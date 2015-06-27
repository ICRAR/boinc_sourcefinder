CREATE SCHEMA IF NOT EXISTS sourcefinder DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE sourcefinder ;

CREATE TABLE IF NOT EXISTS sourcefinder.`run` (
  run_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`run_id`)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`parameter` (
  parameter_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  parameter_name VARCHAR(100),
  PRIMARY KEY (parameter_id)

) ENGINE = InnoDB;

#INSERT INTO parameter VALUES (0, 'reconDim');
#INSERT INTO parameter VALUES (1, 'snrRecon');
#INSERT INTO parameter VALUES (2, 'scaleMin');
#INSERT INTO parameter VALUES (3, 'minPix');
#INSERT INTO parameter VALUES (4, 'minChan');
#INSERT INTO parameter VALUES (5, 'flagGrowth');
#INSERT INTO parameter VALUES (6, 'growthThreshold');
#INSERT INTO parameter VALUES (7, 'threshold');


CREATE TABLE IF NOT EXISTS sourcefinder.`parameter_range` (
  `parameter_range_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `paramater_string`   VARCHAR(20),
  `parameter_id`       BIGINT UNSIGNED NOT NULL,
  `run_id`             BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`parameter_range_id`),
  INDEX parameter_range_parameter_index (`parameter_id` ASC),
  INDEX parameter_range_run_index (`run_id` ASC),

  FOREIGN KEY (`parameter_id`)
  REFERENCES sourcefinder.`parameter` (`parameter_id`),
  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder.`run` (`run_id`)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`parameter_grouping` (
  `parameter_grouping_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `run_id` BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`parameter_grouping_id`),
  INDEX grouping_run_index (`run_id` ASC),

  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder.`run` (`run_id`)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`parameter_values` (
  `value_id`     BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `value`        FLOAT           NOT NULL,
  `parameter_grouping_id` BIGINT UNSIGNED NOT NULL,
  `parameter_id` BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`value_id`),
  INDEX value_grouping_index (`parameter_grouping_id` ASC),
  INDEX value_parameter_index (`parameter_id` ASC),

  FOREIGN KEY (`parameter_grouping_id`)
  REFERENCES sourcefinder.`parameter_grouping` (`parameter_grouping_id`),

  FOREIGN KEY (`parameter_id`)
  REFERENCES sourcefinder.`parameter` (`parameter_id`)
)ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`cube` (
  cube_id   BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  cube_name VARCHAR(2000) NOT NULL,
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
  `parameter_grouping_id` BIGINT UNSIGNED NOT NULL,
  `cube_id`   BIGINT UNSIGNED    NOT NULL,

  PRIMARY KEY (`result_id`),
  INDEX result_grouping_index (`parameter_grouping_id` ASC),
  INDEX result_cube_index (`cube_id` ASC),

  FOREIGN KEY (`parameter_grouping_id`)
  REFERENCES sourcefinder.`parameter_grouping` (`parameter_grouping_id`),

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


