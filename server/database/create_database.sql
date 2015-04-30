CREATE SCHEMA IF NOT EXISTS sourcefinder DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE sourcefinder ;

CREATE TABLE IF NOT EXISTS sourcefinder.`run` (
  `run_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`run_id`)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`parameter` (
  `parameter_id` BIGINT UNSIGNED NOT NULL,
  'parameter_name' VARCHAR(45),
  PRIMARY KEY ('run_id')
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`parameter_range` (
  `parameter_range_id` INT UNSIGNED    NOT NULL,
  `start`              FLOAT           NOT NULL,
  `stop`               FLOAT           NOT NULL,
  `increment`          FLOAT           NOT NULL,
  `parameter_id`       BIGINT UNSIGNED NOT NULL,
  `run_id`             INT UNSIGNED    NOT NULL,

  PRIMARY KEY (`parameter_range_id`),
  INDEX `fk_parameter_range_parameter_idx` (`parameter_id` ASC),
  INDEX `fk_parameter_range_run1_idx` (`run_id` ASC),
  CONSTRAINT `fk_parameter_range_parameter`

  FOREIGN KEY (`parameter_id`)
  REFERENCES sourcefinder.`parameter` (`parameter_id`),
  CONSTRAINT `fk_parameter_range_run1`
  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder.`run` (`run_id`)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`parameter_grouping` (
  `parameter_grouping_id` BIGINT UNSIGNED NOT NULL,
  `run_id` BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`parameter_grouping_id`),
  INDEX `fk_grouping_run1_idx` (`run_id` ASC),
  CONSTRAINT `fk_grouping_run1`

  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder.`run` (`run_id`)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`parameter_values` (
  `value_id`     BIGINT UNSIGNED NOT NULL,
  `value`        FLOAT           NOT NULL,
  `parameter_grouping_id` BIGINT UNSIGNED NOT NULL,
  `parameter_id` BIGINT UNSIGNED NOT NULL,

  PRIMARY KEY (`value_id`),
  INDEX `fk_value_grouping1_idx` (`parameter_grouping_id` ASC),
  INDEX `fk_value_parameter1_idx` (`parameter_id` ASC),
  CONSTRAINT `fk_value_grouping1`

  FOREIGN KEY (`parameter_grouping_id`)
  REFERENCES sourcefinder.`parameter_grouping` (`parameter_grouping_id`),
  CONSTRAINT `fk_value_parameter1`

  FOREIGN KEY (`parameter_id`)
  REFERENCES sourcefinder.`parameter` (`parameter_id`)
)ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS sourcefinder.`cube` (
  `cube_id` INT UNSIGNED NOT NULL,
  `cube_name` VARCHAR(2000) NOT NULL,
  `run_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`cube_id`),
  INDEX `fk_cube_run1_idx` (`run_id` ASC),
  CONSTRAINT `fk_cube_run1`
  FOREIGN KEY (`run_id`)
  REFERENCES sourcefinder.`run` (`run_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`result`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS sourcefinder.`result` (
  `result_id` BIGINT UNSIGNED NOT NULL,
  `parameter_grouping_id` BIGINT UNSIGNED NOT NULL,
  `cube_id` INT UNSIGNED NOT NULL,
  PRIMARY KEY (`result_id`),
  INDEX `fk_result_grouping1_idx` (`parameter_grouping_id` ASC),
  INDEX `fk_result_cube1_idx` (`cube_id` ASC),
  CONSTRAINT `fk_result_grouping1`
  FOREIGN KEY (`parameter_grouping_id`)
  REFERENCES sourcefinder.`parameter_grouping` (`parameter_grouping_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_result_cube1`
  FOREIGN KEY (`cube_id`)
  REFERENCES sourcefinder.`cube` (`cube_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
  ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `mydb`.`cube_user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS sourcefinder.`cube_user` (
  `cube_user_id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `cube_id` BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (`cube_user_id`),
  INDEX `user_id_index` (`user_id` ASC),
  INDEX `user_index` (`cube_id` ASC),
  INDEX `user_cube_index` (`user_id` ASC, `cube_id` ASC),
  CONSTRAINT `fk_cube_user_cube1`
  FOREIGN KEY (`cube_id`)
  REFERENCES sourcefinder.`cube` (`cube_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
  ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
