--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: backups; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE backups (
    id integer NOT NULL,
    scan_id integer,
    "timestamp" integer,
    ref_count bigint,
    glacier_id text
);


ALTER TABLE public.backups OWNER TO pacsocial;

--
-- Name: backups_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE backups_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.backups_id_seq OWNER TO pacsocial;

--
-- Name: backups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE backups_id_seq OWNED BY backups.id;


--
-- Name: cron_score; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE cron_score (
    id integer NOT NULL,
    tweet_id bigint
);


ALTER TABLE public.cron_score OWNER TO pacsocial;

--
-- Name: cron_score_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE cron_score_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.cron_score_id_seq OWNER TO pacsocial;

--
-- Name: cron_score_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE cron_score_id_seq OWNED BY cron_score.id;


--
-- Name: point; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE point (
    id integer NOT NULL,
    type character(15),
    entity_ref bigint,
    bot_id character varying(32),
    team_id integer
);


ALTER TABLE public.point OWNER TO pacsocial;

--
-- Name: point_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE point_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.point_id_seq OWNER TO pacsocial;

--
-- Name: point_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE point_id_seq OWNED BY point.id;


--
-- Name: scan; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE scan (
    id integer NOT NULL,
    type character varying(50),
    start integer,
    "end" integer,
    ref_start character(32),
    ref_end character(32)
);


ALTER TABLE public.scan OWNER TO pacsocial;

--
-- Name: COLUMN scan.ref_start; Type: COMMENT; Schema: public; Owner: pacsocial
--

COMMENT ON COLUMN scan.ref_start IS 'non-inclusive';


--
-- Name: COLUMN scan.ref_end; Type: COMMENT; Schema: public; Owner: pacsocial
--

COMMENT ON COLUMN scan.ref_end IS 'inclusive';


--
-- Name: scan_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE scan_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.scan_id_seq OWNER TO pacsocial;

--
-- Name: scan_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE scan_id_seq OWNED BY scan.id;


--
-- Name: targets; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE targets (
    twitter_id character varying(32)
);


ALTER TABLE public.targets OWNER TO pacsocial;

--
-- Name: team; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE team (
    id integer NOT NULL,
    name character varying(32)
);


ALTER TABLE public.team OWNER TO pacsocial;

--
-- Name: team_bot; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE team_bot (
    team_id integer,
    twitter_id character varying(32),
    screen_name character varying(32),
    type integer DEFAULT 0,
    kill_date integer
);


ALTER TABLE public.team_bot OWNER TO pacsocial;

--
-- Name: COLUMN team_bot.type; Type: COMMENT; Schema: public; Owner: pacsocial
--

COMMENT ON COLUMN team_bot.type IS '0 = scorer, 1 = helper';


--
-- Name: team_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE team_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.team_id_seq OWNER TO pacsocial;

--
-- Name: team_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE team_id_seq OWNED BY team.id;


--
-- Name: team_link; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE team_link (
    team_id integer,
    link text
);


ALTER TABLE public.team_link OWNER TO pacsocial;

--
-- Name: tuser; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE tuser (
    user_id character varying(32) NOT NULL,
    screen_name character varying(32),
    full_name character varying(32),
    bio text,
    followers integer DEFAULT 0 NOT NULL,
    total_tweets integer DEFAULT 0 NOT NULL,
    "timestamp" integer,
    following integer,
    id integer NOT NULL,
    interesting boolean DEFAULT false,
    location text,
    website text,
    profile_image_url text,
    profile_banner_url text,
    protected boolean
);


ALTER TABLE public.tuser OWNER TO pacsocial;

--
-- Name: tuser_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE tuser_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.tuser_id_seq OWNER TO pacsocial;

--
-- Name: tuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE tuser_id_seq OWNED BY tuser.id;


--
-- Name: tuser_tuser; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE tuser_tuser (
    "timestamp" integer,
    from_user character varying(32),
    to_user character varying(32),
    weight smallint,
    id integer NOT NULL,
    bot boolean
);


ALTER TABLE public.tuser_tuser OWNER TO pacsocial;

--
-- Name: tuser_tuser_bot; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE tuser_tuser_bot (
    id integer NOT NULL,
    from_user character varying(32),
    to_user character varying(32),
    "timestamp" integer
);


ALTER TABLE public.tuser_tuser_bot OWNER TO pacsocial;

--
-- Name: tuser_tuser_bot_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE tuser_tuser_bot_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.tuser_tuser_bot_id_seq OWNER TO pacsocial;

--
-- Name: tuser_tuser_bot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE tuser_tuser_bot_id_seq OWNED BY tuser_tuser_bot.id;


--
-- Name: tuser_tuser_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE tuser_tuser_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.tuser_tuser_id_seq OWNER TO pacsocial;

--
-- Name: tuser_tuser_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE tuser_tuser_id_seq OWNED BY tuser_tuser.id;


--
-- Name: tweet; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE tweet (
    tweet_id bigint,
    user_id character varying(32),
    text character varying(256),
    "timestamp" integer,
    interesting boolean DEFAULT true,
    id integer NOT NULL
);


ALTER TABLE public.tweet OWNER TO pacsocial;

--
-- Name: tweet_entity; Type: TABLE; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE TABLE tweet_entity (
    tweet_id bigint,
    type character varying(20),
    text text,
    id integer NOT NULL
);


ALTER TABLE public.tweet_entity OWNER TO pacsocial;

--
-- Name: tweet_entity_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE tweet_entity_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.tweet_entity_id_seq OWNER TO pacsocial;

--
-- Name: tweet_entity_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE tweet_entity_id_seq OWNED BY tweet_entity.id;


--
-- Name: tweet_id_seq; Type: SEQUENCE; Schema: public; Owner: pacsocial
--

CREATE SEQUENCE tweet_id_seq
START WITH 1
INCREMENT BY 1
NO MINVALUE
NO MAXVALUE
CACHE 1;


ALTER TABLE public.tweet_id_seq OWNER TO pacsocial;

--
-- Name: tweet_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: pacsocial
--

ALTER SEQUENCE tweet_id_seq OWNED BY tweet.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY backups ALTER COLUMN id SET DEFAULT nextval('backups_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY cron_score ALTER COLUMN id SET DEFAULT nextval('cron_score_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY point ALTER COLUMN id SET DEFAULT nextval('point_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY scan ALTER COLUMN id SET DEFAULT nextval('scan_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY team ALTER COLUMN id SET DEFAULT nextval('team_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY tuser ALTER COLUMN id SET DEFAULT nextval('tuser_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY tuser_tuser ALTER COLUMN id SET DEFAULT nextval('tuser_tuser_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY tuser_tuser_bot ALTER COLUMN id SET DEFAULT nextval('tuser_tuser_bot_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY tweet ALTER COLUMN id SET DEFAULT nextval('tweet_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: pacsocial
--

ALTER TABLE ONLY tweet_entity ALTER COLUMN id SET DEFAULT nextval('tweet_entity_id_seq'::regclass);


--
-- Name: scan_pkey; Type: CONSTRAINT; Schema: public; Owner: pacsocial; Tablespace: 
--

ALTER TABLE ONLY scan
ADD CONSTRAINT scan_pkey PRIMARY KEY (id);


--
-- Name: e (twitter_id);


--
-- Name: tuser_tuser_bot_touser; Type: INDEX; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE INDEX tuser_tuser_bot_touser ON tuser_tuser_bot USING btree (to_user, from_user);


--
-- Name: tweet_by_tweetid; Type: INDEX; Schema: public; Owner: pacsocial; Tablespace: 
--

CREATE INDEX tweet_by_tweetid ON tweet USING btree (tweet_id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- Name: backups; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE backups FROM PUBLIC;
REVOKE ALL ON TABLE backups FROM pacsocial;
GRANT ALL ON TABLE backups TO pacsocial;
GRANT SELECT ON TABLE backups TO dashboard;


--
-- Name: point; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE point FROM PUBLIC;
REVOKE ALL ON TABLE point FROM pacsocial;
GRANT ALL ON TABLE point TO pacsocial;
GRANT SELECT ON TABLE point TO dashboard;


--
-- Name: scan; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE scan FROM PUBLIC;
REVOKE ALL ON TABLE scan FROM pacsocial;
GRANT ALL ON TABLE scan TO pacsocial;
GRANT SELECT ON TABLE scan TO dashboard;


--
-- Name: targets; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE targets FROM PUBLIC;
REVOKE ALL ON TABLE targets FROM pacsocial;
GRANT ALL ON TABLE targets TO pacsocial;
GRANT SELECT ON TABLE targets TO dashboard;


--
-- Name: team; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE team FROM PUBLIC;
REVOKE ALL ON TABLE team FROM pacsocial;
GRANT ALL ON TABLE team TO pacsocial;
GRANT SELECT ON TABLE team TO dashboard;


--
-- Name: team_bot; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE team_bot FROM PUBLIC;
REVOKE ALL ON TABLE team_bot FROM pacsocial;
GRANT ALL ON TABLE team_bot TO pacsocial;
GRANT SELECT ON TABLE team_bot TO dashboard;


--
-- Name: team_link; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE team_link FROM PUBLIC;
REVOKE ALL ON TABLE team_link FROM pacsocial;
GRANT ALL ON TABLE team_link TO pacsocial;
GRANT SELECT ON TABLE team_link TO dashboard;


--
-- Name: tuser; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE tuser FROM PUBLIC;
REVOKE ALL ON TABLE tuser FROM pacsocial;
GRANT ALL ON TABLE tuser TO pacsocial;
GRANT SELECT ON TABLE tuser TO dashboard;


--
-- Name: tuser_tuser; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE tuser_tuser FROM PUBLIC;
REVOKE ALL ON TABLE tuser_tuser FROM pacsocial;
GRANT ALL ON TABLE tuser_tuser TO pacsocial;
GRANT SELECT ON TABLE tuser_tuser TO dashboard;


--
-- Name: tuser_tuser_bot; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE tuser_tuser_bot FROM PUBLIC;
REVOKE ALL ON TABLE tuser_tuser_bot FROM pacsocial;
GRANT ALL ON TABLE tuser_tuser_bot TO pacsocial;
GRANT SELECT ON TABLE tuser_tuser_bot TO dashboard;


--
-- Name: tweet; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE tweet FROM PUBLIC;
REVOKE ALL ON TABLE tweet FROM pacsocial;
GRANT ALL ON TABLE tweet TO pacsocial;
GRANT SELECT ON TABLE tweet TO dashboard;


--
-- Name: tweet_entity; Type: ACL; Schema: public; Owner: pacsocial
--

REVOKE ALL ON TABLE tweet_entity FROM PUBLIC;
REVOKE ALL ON TABLE tweet_entity FROM pacsocial;
GRANT ALL ON TABLE tweet_entity TO pacsocial;
GRANT SELECT ON TABLE tweet_entity TO dashboard;


--
-- PostgreSQL database dump complete
--

