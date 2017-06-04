--
-- PostgreSQL database dump
--
CREATE ROLE ductdb WITH LOGIN SUPERUSER password 'Randm109';

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: db1; Type: SCHEMA; Schema: -; Owner: ductdb
--

CREATE SCHEMA db1;

CREATE ROLE grafana_user WITH LOGIN SUPERUSER password 'RanDm108';
CREATE SCHEMA grafana_db;
ALTER SCHEMA grafana_db OWNER TO grafana_user;


ALTER SCHEMA db1 OWNER TO ductdb;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = db1, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: dbtable; Type: TABLE; Schema: db1; Owner: ductdb; Tablespace: 
--

CREATE TABLE dbtable (
    dbname character varying,
    dbspec json,
    serverid uuid,
    dbid uuid NOT NULL,
    dbtype character varying
);


ALTER TABLE db1.dbtable OWNER TO ductdb;

--
-- Name: poolid_seq; Type: SEQUENCE; Schema: db1; Owner: ductdb
--

CREATE SEQUENCE poolid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 99999
    CACHE 1;


ALTER TABLE db1.poolid_seq OWNER TO ductdb;

--
-- Name: pooltable; Type: TABLE; Schema: db1; Owner: ductdb; Tablespace: 
--

CREATE TABLE pooltable (
    poolname character varying,
    pooltype character varying,
    poolid uuid NOT NULL
);


ALTER TABLE db1.pooltable OWNER TO ductdb;

--
-- Name: privatepool; Type: TABLE; Schema: db1; Owner: ductdb; Tablespace: 
--

CREATE TABLE privatepool (
    username character varying NOT NULL,
    password character varying,
    content character varying,
    targetserver character varying,
    clusternm character varying,
    poolid uuid NOT NULL,
    networknm character varying,
    storagenm character varying,
    datacenternm character varying
);


ALTER TABLE db1.privatepool OWNER TO ductdb;

--
-- Name: publicpool; Type: TABLE; Schema: db1; Owner: ductdb; Tablespace: 
--

CREATE TABLE publicpool (
    keypair character varying NOT NULL,
    securitygrp character varying,
    accesskey character varying,
    secretkey character varying,
    poolid uuid NOT NULL
);


ALTER TABLE db1.publicpool OWNER TO ductdb;

--
-- Name: servertable; Type: TABLE; Schema: db1; Owner: ductdb; Tablespace: 
--

CREATE TABLE servertable (
    servername character varying,
    mysql_role boolean,
    postgres_role boolean,
    oracle_role boolean,
    mssql_role boolean,
    spec json,
    serverid uuid NOT NULL,
    poolid uuid
);


ALTER TABLE db1.servertable OWNER TO ductdb;

--
-- Name: dbid_pk; Type: CONSTRAINT; Schema: db1; Owner: ductdb; Tablespace: 
--

ALTER TABLE ONLY dbtable
    ADD CONSTRAINT dbid_pk PRIMARY KEY (dbid);


--
-- Name: dbtable_dbname_key; Type: CONSTRAINT; Schema: db1; Owner: ductdb; Tablespace: 
--

ALTER TABLE ONLY dbtable
    ADD CONSTRAINT dbtable_dbname_key UNIQUE (dbname);


--
-- Name: poolid; Type: CONSTRAINT; Schema: db1; Owner: ductdb; Tablespace: 
--

ALTER TABLE ONLY pooltable
    ADD CONSTRAINT poolid PRIMARY KEY (poolid);


--
-- Name: poolname_uniq; Type: CONSTRAINT; Schema: db1; Owner: ductdb; Tablespace: 
--

ALTER TABLE ONLY pooltable
    ADD CONSTRAINT poolname_uniq UNIQUE (poolname);


--
-- Name: privatepool_pkey; Type: CONSTRAINT; Schema: db1; Owner: ductdb; Tablespace: 
--

ALTER TABLE ONLY privatepool
    ADD CONSTRAINT privatepool_pkey PRIMARY KEY (poolid);


--
-- Name: publicpool_pkey; Type: CONSTRAINT; Schema: db1; Owner: ductdb; Tablespace: 
--

ALTER TABLE ONLY publicpool
    ADD CONSTRAINT publicpool_pkey PRIMARY KEY (poolid);


--
-- Name: serverid; Type: CONSTRAINT; Schema: db1; Owner: ductdb; Tablespace: 
--

ALTER TABLE ONLY servertable
    ADD CONSTRAINT serverid PRIMARY KEY (serverid);


--
-- Name: servername_uniq; Type: CONSTRAINT; Schema: db1; Owner: ductdb; Tablespace: 
--

ALTER TABLE ONLY servertable
    ADD CONSTRAINT servername_uniq UNIQUE (servername);


--
-- Name: poolid; Type: FK CONSTRAINT; Schema: db1; Owner: ductdb
--

ALTER TABLE ONLY publicpool
    ADD CONSTRAINT poolid FOREIGN KEY (poolid) REFERENCES pooltable(poolid);


--
-- Name: poolid; Type: FK CONSTRAINT; Schema: db1; Owner: ductdb
--

ALTER TABLE ONLY privatepool
    ADD CONSTRAINT poolid FOREIGN KEY (poolid) REFERENCES pooltable(poolid);


--
-- Name: serverid_fk; Type: FK CONSTRAINT; Schema: db1; Owner: ductdb
--

ALTER TABLE ONLY dbtable
    ADD CONSTRAINT serverid_fk FOREIGN KEY (serverid) REFERENCES servertable(serverid);


--
-- Name: db1; Type: ACL; Schema: -; Owner: ductdb
--

REVOKE ALL ON SCHEMA db1 FROM PUBLIC;
REVOKE ALL ON SCHEMA db1 FROM ductdb;
GRANT ALL ON SCHEMA db1 TO ductdb;


--
-- Name: pooltable.poolname; Type: ACL; Schema: db1; Owner: ductdb
--

REVOKE ALL(poolname) ON TABLE pooltable FROM PUBLIC;
REVOKE ALL(poolname) ON TABLE pooltable FROM ductdb;
GRANT ALL(poolname) ON TABLE pooltable TO ductdb;


--
-- PostgreSQL database dump complete
--

