# -*- coding: utf-8 -*-
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

DROP SCHEMA IF EXISTS sourcefinder_results;
CREATE SCHEMA IF NOT EXISTS sourcefinder_results DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE sourcefinder_results;

# Stores the various categories of data we have.
CREATE TABLE IF NOT EXISTS category (
  id BIGINT UNSIGNED NOT NULL,
  name VARCHAR(16),

  PRIMARY KEY (id)
) ENGINE = InnoDB;

INSERT INTO category (id, name) VALUES (0, '10MB Duchamp');
INSERT INTO category (id, name) VALUES (0, '10MB SoFiA');
INSERT INTO category (id, name) VALUES (0, '100MB SoFiA');

# Stores info for each cubelet.
CREATE TABLE IF NOT EXISTS cubelet (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(64),
  category_id BIGINT UNSIGNED NOT NULL,
  ra FLOAT,
  `dec` FLOAT,
  freq FLOAT,

  PRIMARY KEY (id),
  FOREIGN KEY (category_id)
    REFERENCES category(id)
) ENGINE = InnoDB;

# Stores info for each parameter set.
CREATE TABLE IF NOT EXISTS parameters (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(64),
  text VARCHAR(4096),

  PRIMARY KEY (id)
) ENGINE = InnoDB;

# Stores each found source.
CREATE TABLE IF NOT EXISTS source (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  cubelet_id BIGINT UNSIGNED NOT NULL,
  parameters_id BIGINT UNSIGNED NOT NULL,

  ra FLOAT,
  `dec` FLOAT,
  freq FLOAT,
  w_20 FLOAT,
  w_50 FLOAT,
  w_freq FLOAT,
  f_int FLOAT,
  f_tot FLOAT,
  f_peak FLOAT,
  n_voxel FLOAT,
  n_chan FLOAT,
  n_spatpix FLOAT,
  # Can add more fields here if needed.

  PRIMARY KEY (id),
  FOREIGN KEY (cubelet_id)
    REFERENCES cubelet(id),
  FOREIGN KEY (parameters_id)
    REFERENCES parameters(id)
) ENGINE = InnoDB;


