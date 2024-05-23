CREATE TABLE RUTAS (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NOMBRE TEXT NOT NULL,
    RUTA TEXT
);

INSERT INTO RUTAS (NOMBRE, RUTA) VALUES ('DACXANALISTA', '');
INSERT INTO RUTAS (NOMBRE, RUTA) VALUES ('CELULARES', '');
INSERT INTO RUTAS (NOMBRE, RUTA) VALUES ('MODELO', '');
INSERT INTO RUTAS (NOMBRE, RUTA) VALUES ('ZFIR', '');
INSERT INTO RUTAS (NOMBRE, RUTA) VALUES ('BASES', '');
INSERT INTO RUTAS (NOMBRE, RUTA) VALUES ('CARGAS', '');

SELECT * FROM RUTAS;