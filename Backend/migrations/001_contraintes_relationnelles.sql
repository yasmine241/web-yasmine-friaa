-- ============================================================
-- SG SecureBank — Migration : ajout des contraintes relationnelles
-- et des index manquants sur la base Oracle XE existante.
--
-- À exécuter une seule fois (SQL Developer / SQL*Plus / sqlplus CLI),
-- après avoir vérifié qu'aucune ligne orpheline ne violerait les FK
-- (requêtes de contrôle fournies en bas du fichier).
-- ============================================================

-- 1. Clés étrangères ---------------------------------------------------

ALTER TABLE COMPTES
    ADD CONSTRAINT fk_comptes_client
    FOREIGN KEY (CLIENT_ID) REFERENCES CLIENTS(CLIENT_ID);

ALTER TABLE TRANSACTIONS
    ADD CONSTRAINT fk_transactions_compte
    FOREIGN KEY (COMPTE_ID) REFERENCES COMPTES(COMPTE_ID);

ALTER TABLE FRAUD
    ADD CONSTRAINT fk_fraud_transaction
    FOREIGN KEY (TRANSACTION_ID) REFERENCES TRANSACTIONS(TRANSACTION_ID);

-- 2. Contraintes d'unicité ---------------------------------------------

ALTER TABLE CLIENTS
    ADD CONSTRAINT uq_clients_email UNIQUE (EMAIL);

ALTER TABLE COMPTES
    ADD CONSTRAINT uq_comptes_numero UNIQUE (NUMERO_COMPTE);

-- 3. Index sur colonnes fréquemment filtrées / jointes ------------------
-- (les FK ci-dessus créent implicitement un index en Oracle seulement
--  si on le demande explicitement : on le fait ici)

CREATE INDEX idx_comptes_client_id        ON COMPTES(CLIENT_ID);
CREATE INDEX idx_transactions_compte_id   ON TRANSACTIONS(COMPTE_ID);
CREATE INDEX idx_transactions_statut      ON TRANSACTIONS(STATUT);
CREATE INDEX idx_transactions_date        ON TRANSACTIONS(DATE_TRANSACTION);
CREATE INDEX idx_fraud_transaction_id     ON FRAUD(TRANSACTION_ID);
CREATE INDEX idx_fraud_statut_analyse     ON FRAUD(STATUT_ANALYSE);
CREATE INDEX idx_fraud_date_detection     ON FRAUD(DATE_DETECTION);
CREATE INDEX idx_clients_statut           ON CLIENTS(STATUT);

-- ============================================================
-- Requêtes de contrôle à lancer AVANT la migration si l'ALTER
-- TABLE échoue avec ORA-02291 (contrainte violée par une ligne
-- existante) — cela signifie des données orphelines à nettoyer :
-- ============================================================
-- SELECT * FROM COMPTES      WHERE CLIENT_ID      NOT IN (SELECT CLIENT_ID FROM CLIENTS);
-- SELECT * FROM TRANSACTIONS WHERE COMPTE_ID       NOT IN (SELECT COMPTE_ID FROM COMPTES);
-- SELECT * FROM FRAUD        WHERE TRANSACTION_ID  NOT IN (SELECT TRANSACTION_ID FROM TRANSACTIONS);
