CREATE DATABASE barDB;
CREATE USER 'admin'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON barDB.* TO 'admin'@'localhost';
FLUSH PRIVILEGES;
USE barDB;
CREATE TABLE beverages(id int NOT NULL AUTO_INCREMENT, Name varchar(255), Img_URL varchar(255), PRIMARY KEY (id));
CREATE TABLE user(id int NOT NULL AUTO_INCREMENT, name varchar(255),gruppe int,  pass varchar(255), PRIMARY KEY (id));
CREATE TABLE bar_verbrauch(barID int, drinkID int, Stand int);