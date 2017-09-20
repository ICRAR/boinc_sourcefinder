DROP SCHEMA IF EXISTS sourcefinder_visualisation;
CREATE SCHEMA IF NOT EXISTS sourcefinder_visualisation DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE sourcefinder_visualisation;

# A sourcefinding application that will have generated results.
CREATE TABLE IF NOT EXISTS sourcefinder_visualisation.`app` (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100),

    PRIMARY KEY (id)
) ENGINE = InnoDB;

# Cube - Made up of slices.
CREATE TABLE IF NOT EXISTS sourcefinder_visualisation.`cube` (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,

    PRIMARY KEY (id)
) ENGINE = InnoDB;

# Slice - Each slice in the CUBE fits file. Each slice here contains at least one source. A result source contains
#         the frequency that it was found. This can be used to determine the slice that the source was found in.
CREATE TABLE IF NOT EXISTS sourcefinder_visualisation.`slice` (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    cube_id BIGINT UNSIGNED NOT NULL, # Cube that this slice is part of

    freq FLOAT, # Frequency of the slice
    size_x INT, # x pixel width of the slice
    size_y INT, # y pixel width of the slice

    PRIMARY KEY (id),
    FOREIGN KEY (cube_id) REFERENCES sourcefinder_visualisation.`cube`(`id`)
) ENGINE = InnoDB;

# Sources - Each source exists within a slice. Sources contain information to allow them to be outlined in the slice image.
CREATE TABLE IF NOT EXISTS sourcefinder_visualisation.`source` (
	id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    slice_id BIGINT UNSIGNED NOT NULL, # Slice that the source was found in.
    parameter_id INT UNSIGNED, # Parameter ID that found the source. Either a Duchamp or SoFiA parameter ID.
    app_id INT UNSIGNED, # Sourcefinding application that found this source.

    ra FLOAT, # Right ascention
    `dec` FLOAT, # Declination

    # Where to place highlight on the slice to show this source.
    highlight_x INT,
    highlight_y INT,
    highlight_radius FLOAT, # pixels

    PRIMARY KEY (id),
    FOREIGN KEY (slice_id) REFERENCES sourcefinder_visualisation.`slice`(`id`),
    FOREIGN KEY (app_id) REFERENCES sourcefinder_visualisation.`app`(`id`)

) ENGINE = InnoDB;

# User - A user who found a source.
CREATE TABLE IF NOT EXISTS sourcefinder_visualisation.`user` (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    boinc_name VARCHAR(300) NOT NULL,
    boinc_user_id BIGINT UNSIGNED NOT NULL,

    PRIMARY KEY (id)
) ENGINE = InnoDB;

# Found-By - Connects a user to a source.
CREATE TABLE IF NOT EXISTS sourcefinder_visualisation.`found_by` (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    source_id BIGINT UNSIGNED NOT NULL,

    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES sourcefinder_visualisation.`user`(`id`),
    FOREIGN KEY (source_id) REFERENCES sourcefinder_visualisation.`source`(`id`)
) ENGINE = InnoDB;


