
-- PostgreSQL database dump
SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
CREATE ROLE grafana_user WITH LOGIN SUPERUSER password 'RanDm108';
CREATE SCHEMA grafana_db;
ALTER SCHEMA grafana_db OWNER TO grafana_user;
