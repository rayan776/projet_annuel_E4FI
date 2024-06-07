-- mysql -p -h localhost -u root esiee < path/to/test.sql

DROP TABLE IF EXISTS tokens;
DROP TABLE IF EXISTS reviewrating;
DROP TABLE IF EXISTS blocking;
DROP TABLE IF EXISTS review;
DROP TABLE IF EXISTS announce;
DROP TABLE IF EXISTS category;
DROP TABLE IF EXISTS privateMessages;
DROP TABLE IF EXISTS users;

CREATE TABLE users(
	idUser int PRIMARY KEY AUTO_INCREMENT,
	username varchar(50) NOT NULL,
	firstname varchar(50) NOT NULL,
	lastname varchar(50) NOT NULL,
	password varchar(500) NOT NULL,
	privilegeLevel int NOT NULL,
	dateRegister TIMESTAMP NOT NULL,
	secretQuestion varchar(200) NOT NULL,
	secretAnswer TEXT NOT NULL
);

CREATE TABLE tokens(
	token varchar(500) PRIMARY KEY,
	idUser int,
	expiration_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	CONSTRAINT fk_tokens FOREIGN KEY (idUser) REFERENCES users (idUser)
);

DELIMITER //

CREATE TRIGGER setTokenTime
BEFORE INSERT ON tokens
FOR EACH ROW
BEGIN
    SET NEW.expiration_date = DATE_ADD(NOW(), INTERVAL 10 MINUTE);
END//

DELIMITER ;

CREATE TABLE category(
	idCat int PRIMARY KEY AUTO_INCREMENT,
	catName varchar(100) NOT NULL
);

CREATE TABLE privateMessages(
	idMsg int PRIMARY KEY AUTO_INCREMENT,
	title varchar(100) NOT NULL,
	content TEXT NOT NULL,
	dateMsg TIMESTAMP NOT NULL,
	idFrom int,
	idTo int,
	opened int NOT NULL DEFAULT 0,
	CONSTRAINT fk_prv_from FOREIGN KEY (idFrom) REFERENCES users (idUser),
	CONSTRAINT fk_prv_to FOREIGN KEY (idTo) REFERENCES users (idUser)
);


CREATE TABLE announce(
	idAnnounce int PRIMARY KEY AUTO_INCREMENT,
	typeAnnounce int NOT NULL,
	dateAnnounce TIMESTAMP NOT NULL,
	intitule varchar(200) NOT NULL,
	description TEXT,
	latitude float,
	longitude float,
	localisation TEXT NOT NULL,
	valid int,
	idCat int,
	idUser int,
	CONSTRAINT fk_announce_cat FOREIGN KEY (idCat) REFERENCES category (idCat),
	CONSTRAINT fk_announce_user FOREIGN KEY (idUser) REFERENCES users (idUser)
);

CREATE TABLE review(
	idReview int PRIMARY KEY AUTO_INCREMENT,
	idUser int NOT NULL,
	score int NOT NULL,
	content TEXT,
	dateReview TIMESTAMP NOT NULL,
	idAnnounce int,
	CONSTRAINT fk_review_announce FOREIGN KEY (idAnnounce) REFERENCES announce (idAnnounce),
	CONSTRAINT fk_review_user FOREIGN KEY (idUser) REFERENCES users (idUser)
);

CREATE TABLE reviewRating(
	idReviewRating int PRIMARY KEY AUTO_INCREMENT,
	idReview int NOT NULL,
	rating int NOT NULL,
	idUser int NOT NULL,
	CONSTRAINT fk_reviewrating_idReview FOREIGN KEY (idReview) REFERENCES review (idReview),
	CONSTRAINT fk_reviewrating_idUser FOREIGN KEY (idUser) REFERENCES users (idUser),
	CONSTRAINT chk_reviewrating CHECK (rating IN (-1, 1))
);

CREATE TABLE blocking(
	idUserBlocking int,
	idUserBlocked int,
	CONSTRAINT pk_blocking PRIMARY KEY (idUserBlocking, idUserBlocked),
	CONSTRAINT fk_blocking1 FOREIGN KEY (idUserBlocking) REFERENCES users (idUser),
	CONSTRAINT fk_blocking2 FOREIGN KEY (idUserBlocked) REFERENCES users (idUser)
);

CREATE INDEX index_announce
ON announce (latitude, longitude);

SET NAMES utf8;
INSERT INTO category (catName) VALUES ('Transport');
INSERT INTO category (catName) VALUES ('Automobile');
INSERT INTO category (catName) VALUES ('Bâtiment et travaux publics');
INSERT INTO category (catName) VALUES ('Nettoyage');
INSERT INTO category (catName) VALUES ('Voyages');
INSERT INTO category (catName) VALUES ('Alimentation');