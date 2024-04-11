--
-- PostgreSQL database dump
--

-- Dumped from database version 15.6
-- Dumped by pg_dump version 15.4

-- Started on 2024-04-11 13:58:48

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 4469 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 246 (class 1255 OID 16645)
-- Name: check_admin_is_member(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.check_admin_is_member() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    is_member BOOLEAN;
BEGIN
    SELECT EXISTS (
        SELECT 1 FROM rso_members
        WHERE id = NEW.admin AND rso_id = NEW.id
    ) INTO is_member;

    IF NOT is_member and NEW.admin IS NOT NULL THEN
        RAISE EXCEPTION 'Admin is not a member of the RSO';
    END IF;

    RETURN NEW;
END;
$$;


ALTER FUNCTION public.check_admin_is_member() OWNER TO postgres;

--
-- TOC entry 245 (class 1255 OID 16641)
-- Name: delete_rso_members(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.delete_rso_members() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	DELETE FROM rso_members
	WHERE rso_id=OLD.id;
	RETURN OLD;
END;$$;


ALTER FUNCTION public.delete_rso_members() OWNER TO postgres;

--
-- TOC entry 243 (class 1255 OID 16632)
-- Name: update_active_status(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_active_status() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
	IF TG_OP = 'INSERT' 
	OR NEW.member_count IS DISTINCT FROM OLD.member_count 
	OR NEW.admin IS NULL
	OR NEW.admin IS DISTINCT FROM OLD.admin
	THEN
		IF NEW.member_count < 5 
		OR NEW.member_count IS NULL 
		OR NEW.admin IS NULL THEN
			NEW.active = FALSE;
		ELSE
			NEW.active = TRUE;
		END IF;
	END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_active_status() OWNER TO postgres;

--
-- TOC entry 241 (class 1255 OID 16601)
-- Name: update_average_rating(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_average_rating() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  UPDATE events
  SET average_rating = (
    SELECT AVG(rating)
    FROM ratings
    WHERE event_id = NEW.event_id
  )
  WHERE id = NEW.event_id;

  RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_average_rating() OWNER TO postgres;

--
-- TOC entry 249 (class 1255 OID 16656)
-- Name: update_comment_author_info(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_comment_author_info() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
    UPDATE comments SET author_first_name = NEW.first_name,
    author_last_name = NEW.last_name, author_email = NEW.email
    WHERE author_id = NEW.id;

    RETURN NEW;
END;$$;


ALTER FUNCTION public.update_comment_author_info() OWNER TO postgres;

--
-- TOC entry 248 (class 1255 OID 16654)
-- Name: update_comment_author_name_and_email(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_comment_author_name_and_email() RETURNS trigger
    LANGUAGE plpgsql
    AS $$DECLARE
    user_record RECORD;

BEGIN
    SELECT first_name, last_name, email
    INTO user_record
    FROM users U
    WHERE U.id = NEW.author_id;

    IF user_record IS NULL THEN
        RAISE EXCEPTION 'User with ID % not found', NEW.author_id;
    END IF;

    NEW.author_first_name := user_record.first_name;
    NEW.author_last_name := user_record.last_name;
    NEW.author_email := user_record.email;

    RETURN NEW;
END;$$;


ALTER FUNCTION public.update_comment_author_name_and_email() OWNER TO postgres;

--
-- TOC entry 251 (class 1255 OID 16666)
-- Name: update_event_rso_name(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_event_rso_name() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
    UPDATE events E
    SET rso_name = (SELECT R.name FROM rso R WHERE E.rso = R.id)
    WHERE EXISTS (SELECT 1 FROM rso R WHERE E.rso = R.id);
    RETURN NEW;
END;$$;


ALTER FUNCTION public.update_event_rso_name() OWNER TO postgres;

--
-- TOC entry 252 (class 1255 OID 16673)
-- Name: update_events_university_name(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_events_university_name() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	NEW.university_name := 
	(SELECT name FROM universities WHERE id = NEW.university);
	RETURN NEW;
END;$$;


ALTER FUNCTION public.update_events_university_name() OWNER TO postgres;

--
-- TOC entry 242 (class 1255 OID 16620)
-- Name: update_member_count(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_member_count() RETURNS trigger
    LANGUAGE plpgsql
    AS $$DECLARE
    members_count INTEGER;
    current_rso_id INTEGER;
BEGIN
    IF TG_OP = 'DELETE' THEN
        current_rso_id = OLD.rso_id;
    ELSE
        current_rso_id = NEW.rso_id;
    END IF;

    SELECT COUNT(*)
    INTO members_count
    FROM rso_members
    WHERE rso_id = current_rso_id;

    UPDATE rso SET member_count = members_count WHERE id = current_rso_id;

    RETURN NEW;
END;$$;


ALTER FUNCTION public.update_member_count() OWNER TO postgres;

--
-- TOC entry 244 (class 1255 OID 16635)
-- Name: update_member_count_rso(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_member_count_rso() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    members_count INTEGER;
BEGIN
	IF TG_OP = 'INSERT' OR NEW.member_count IS DISTINCT FROM OLD.member_count THEN
		SELECT COUNT(*)
		INTO members_count
		FROM rso_members AS A, rso AS B
		WHERE A.rso_id = B.id AND B.id = NEW.id;

		UPDATE rso SET member_count = members_count WHERE id = NEW.id;
	END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_member_count_rso() OWNER TO postgres;

--
-- TOC entry 250 (class 1255 OID 16659)
-- Name: update_university_name(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_university_name() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE events SET university_name = NEW.name
	WHERE university=NEW.id;
	RETURN NEW;
END;$$;


ALTER FUNCTION public.update_university_name() OWNER TO postgres;

--
-- TOC entry 247 (class 1255 OID 16648)
-- Name: vacate_admin_position(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.vacate_admin_position() RETURNS trigger
    LANGUAGE plpgsql
    AS $$BEGIN
	UPDATE rso SET admin=NULL
	WHERE id=OLD.rso_id and admin=OLD.id;
	RETURN OLD;
END;$$;


ALTER FUNCTION public.vacate_admin_position() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 226 (class 1259 OID 16566)
-- Name: comments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.comments (
    id integer NOT NULL,
    event_id integer NOT NULL,
    author_id integer NOT NULL,
    created_time timestamp with time zone,
    edit_time timestamp with time zone,
    comment text,
    author_first_name text,
    author_last_name text,
    author_email text
);


ALTER TABLE public.comments OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 16565)
-- Name: comments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.comments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.comments_id_seq OWNER TO postgres;

--
-- TOC entry 4470 (class 0 OID 0)
-- Dependencies: 225
-- Name: comments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.comments_id_seq OWNED BY public.comments.id;


--
-- TOC entry 222 (class 1259 OID 16514)
-- Name: events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.events (
    id integer NOT NULL,
    university integer NOT NULL,
    author_id integer NOT NULL,
    rso integer,
    approved boolean,
    name text NOT NULL,
    category text NOT NULL,
    description text,
    location text,
    phone text,
    email text,
    "time" timestamp with time zone,
    average_rating double precision,
    university_name text,
    rso_name text
);


ALTER TABLE public.events OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 16450)
-- Name: events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.events_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.events_id_seq OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16513)
-- Name: events_id_seq1; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.events_id_seq1
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.events_id_seq1 OWNER TO postgres;

--
-- TOC entry 4471 (class 0 OID 0)
-- Dependencies: 221
-- Name: events_id_seq1; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.events_id_seq1 OWNED BY public.events.id;


--
-- TOC entry 224 (class 1259 OID 16539)
-- Name: pending_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pending_events (
    id integer NOT NULL,
    university integer NOT NULL,
    author_id integer NOT NULL,
    approved boolean,
    name text NOT NULL,
    category text NOT NULL,
    description text,
    location text,
    phone text,
    email text,
    "time" timestamp with time zone
);


ALTER TABLE public.pending_events OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16538)
-- Name: pending_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.pending_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pending_events_id_seq OWNER TO postgres;

--
-- TOC entry 4472 (class 0 OID 0)
-- Dependencies: 223
-- Name: pending_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.pending_events_id_seq OWNED BY public.pending_events.id;


--
-- TOC entry 228 (class 1259 OID 16585)
-- Name: ratings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ratings (
    id integer NOT NULL,
    author_id integer NOT NULL,
    event_id integer NOT NULL,
    rating integer
);


ALTER TABLE public.ratings OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16584)
-- Name: ratings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ratings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ratings_id_seq OWNER TO postgres;

--
-- TOC entry 4473 (class 0 OID 0)
-- Dependencies: 227
-- Name: ratings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ratings_id_seq OWNED BY public.ratings.id;


--
-- TOC entry 220 (class 1259 OID 16495)
-- Name: rso; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rso (
    id integer NOT NULL,
    name text NOT NULL,
    university integer NOT NULL,
    admin integer,
    active boolean,
    member_count integer
);


ALTER TABLE public.rso OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16494)
-- Name: rso_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rso_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rso_id_seq OWNER TO postgres;

--
-- TOC entry 4474 (class 0 OID 0)
-- Dependencies: 219
-- Name: rso_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rso_id_seq OWNED BY public.rso.id;


--
-- TOC entry 229 (class 1259 OID 16605)
-- Name: rso_members; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rso_members (
    id integer NOT NULL,
    rso_id integer NOT NULL
);


ALTER TABLE public.rso_members OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16477)
-- Name: universities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.universities (
    id integer NOT NULL,
    super_admin integer,
    name text,
    location text,
    description text,
    student_population integer,
    email_domain text
);


ALTER TABLE public.universities OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 16476)
-- Name: universities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.universities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.universities_id_seq OWNER TO postgres;

--
-- TOC entry 4475 (class 0 OID 0)
-- Dependencies: 217
-- Name: universities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.universities_id_seq OWNED BY public.universities.id;


--
-- TOC entry 216 (class 1259 OID 16455)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email text,
    password text,
    role text,
    first_name text,
    last_name text,
    university_id integer NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 16454)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 4476 (class 0 OID 0)
-- Dependencies: 215
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 4258 (class 2604 OID 16569)
-- Name: comments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments ALTER COLUMN id SET DEFAULT nextval('public.comments_id_seq'::regclass);


--
-- TOC entry 4256 (class 2604 OID 16517)
-- Name: events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events ALTER COLUMN id SET DEFAULT nextval('public.events_id_seq1'::regclass);


--
-- TOC entry 4257 (class 2604 OID 16542)
-- Name: pending_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pending_events ALTER COLUMN id SET DEFAULT nextval('public.pending_events_id_seq'::regclass);


--
-- TOC entry 4259 (class 2604 OID 16588)
-- Name: ratings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings ALTER COLUMN id SET DEFAULT nextval('public.ratings_id_seq'::regclass);


--
-- TOC entry 4255 (class 2604 OID 16498)
-- Name: rso id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rso ALTER COLUMN id SET DEFAULT nextval('public.rso_id_seq'::regclass);


--
-- TOC entry 4254 (class 2604 OID 16480)
-- Name: universities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universities ALTER COLUMN id SET DEFAULT nextval('public.universities_id_seq'::regclass);


--
-- TOC entry 4253 (class 2604 OID 16458)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4287 (class 2606 OID 16573)
-- Name: comments comments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (id);


--
-- TOC entry 4281 (class 2606 OID 16521)
-- Name: events events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (id);


--
-- TOC entry 4293 (class 2606 OID 16644)
-- Name: rso_members no_duplicate_members; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rso_members
    ADD CONSTRAINT no_duplicate_members UNIQUE (id, rso_id);


--
-- TOC entry 4283 (class 2606 OID 16653)
-- Name: events no_event_overlap; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT no_event_overlap UNIQUE (location, "time");


--
-- TOC entry 4285 (class 2606 OID 16546)
-- Name: pending_events pending_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pending_events
    ADD CONSTRAINT pending_events_pkey PRIMARY KEY (id);


--
-- TOC entry 4289 (class 2606 OID 16590)
-- Name: ratings ratings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_pkey PRIMARY KEY (id);


--
-- TOC entry 4277 (class 2606 OID 16502)
-- Name: rso rso_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rso
    ADD CONSTRAINT rso_pkey PRIMARY KEY (id);


--
-- TOC entry 4261 (class 2606 OID 16464)
-- Name: users unique_email; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT unique_email UNIQUE (email);


--
-- TOC entry 4265 (class 2606 OID 16558)
-- Name: universities unique_email_domain; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT unique_email_domain UNIQUE (email_domain);


--
-- TOC entry 4267 (class 2606 OID 16562)
-- Name: universities unique_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT unique_name UNIQUE (name);


--
-- TOC entry 4279 (class 2606 OID 16564)
-- Name: rso unique_name_university_combo; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rso
    ADD CONSTRAINT unique_name_university_combo UNIQUE (name, university);


--
-- TOC entry 4291 (class 2606 OID 16604)
-- Name: ratings unique_ratings; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT unique_ratings UNIQUE (author_id, event_id);


--
-- TOC entry 4269 (class 2606 OID 16560)
-- Name: universities unique_super_admin; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT unique_super_admin UNIQUE (super_admin);


--
-- TOC entry 4271 (class 2606 OID 16488)
-- Name: universities universities_location_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT universities_location_key UNIQUE (location);


--
-- TOC entry 4273 (class 2606 OID 16486)
-- Name: universities universities_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT universities_name_key UNIQUE (name);


--
-- TOC entry 4275 (class 2606 OID 16484)
-- Name: universities universities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universities
    ADD CONSTRAINT universities_pkey PRIMARY KEY (id);


--
-- TOC entry 4263 (class 2606 OID 16462)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 4311 (class 2620 OID 16646)
-- Name: rso check_admin_is_member_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER check_admin_is_member_trigger BEFORE INSERT OR UPDATE OF admin ON public.rso FOR EACH ROW EXECUTE FUNCTION public.check_admin_is_member();


--
-- TOC entry 4312 (class 2620 OID 16642)
-- Name: rso delete_rso_members_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER delete_rso_members_trigger AFTER DELETE ON public.rso FOR EACH ROW EXECUTE FUNCTION public.delete_rso_members();


--
-- TOC entry 4313 (class 2620 OID 16639)
-- Name: rso update_active_status_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_active_status_trigger BEFORE INSERT OR UPDATE ON public.rso FOR EACH ROW EXECUTE FUNCTION public.update_active_status();


--
-- TOC entry 4319 (class 2620 OID 16602)
-- Name: ratings update_average_rating_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_average_rating_trigger AFTER INSERT OR DELETE OR UPDATE ON public.ratings FOR EACH ROW EXECUTE FUNCTION public.update_average_rating();


--
-- TOC entry 4309 (class 2620 OID 16658)
-- Name: users update_comment_author_info_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_comment_author_info_trigger AFTER INSERT OR UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_comment_author_info();


--
-- TOC entry 4318 (class 2620 OID 16655)
-- Name: comments update_comment_author_name_and_email; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_comment_author_name_and_email BEFORE INSERT OR UPDATE ON public.comments FOR EACH ROW EXECUTE FUNCTION public.update_comment_author_name_and_email();


--
-- TOC entry 4314 (class 2620 OID 16669)
-- Name: rso update_event_rso_name_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_event_rso_name_trigger AFTER UPDATE ON public.rso FOR EACH ROW EXECUTE FUNCTION public.update_event_rso_name();


--
-- TOC entry 4316 (class 2620 OID 16670)
-- Name: events update_events_rso_name_trigger_on_insert_events; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_events_rso_name_trigger_on_insert_events AFTER INSERT ON public.events FOR EACH ROW EXECUTE FUNCTION public.update_event_rso_name();


--
-- TOC entry 4317 (class 2620 OID 16674)
-- Name: events update_events_university_name_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_events_university_name_trigger BEFORE INSERT ON public.events FOR EACH ROW EXECUTE FUNCTION public.update_events_university_name();


--
-- TOC entry 4315 (class 2620 OID 16637)
-- Name: rso update_member_count_rso_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_member_count_rso_trigger AFTER INSERT OR UPDATE OF member_count ON public.rso FOR EACH ROW EXECUTE FUNCTION public.update_member_count_rso();


--
-- TOC entry 4320 (class 2620 OID 16640)
-- Name: rso_members update_member_count_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_member_count_trigger AFTER INSERT OR DELETE OR UPDATE ON public.rso_members FOR EACH ROW EXECUTE FUNCTION public.update_member_count();


--
-- TOC entry 4310 (class 2620 OID 16660)
-- Name: universities update_university_name_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_university_name_trigger AFTER UPDATE ON public.universities FOR EACH ROW EXECUTE FUNCTION public.update_university_name();


--
-- TOC entry 4321 (class 2620 OID 16649)
-- Name: rso_members vacate_admin_position_on_delete_admin_member; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER vacate_admin_position_on_delete_admin_member AFTER DELETE ON public.rso_members FOR EACH ROW EXECUTE FUNCTION public.vacate_admin_position();


--
-- TOC entry 4303 (class 2606 OID 16579)
-- Name: comments comments_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- TOC entry 4304 (class 2606 OID 16574)
-- Name: comments comments_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- TOC entry 4298 (class 2606 OID 16527)
-- Name: events events_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- TOC entry 4299 (class 2606 OID 16532)
-- Name: events events_rso_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_rso_fkey FOREIGN KEY (rso) REFERENCES public.rso(id);


--
-- TOC entry 4300 (class 2606 OID 16522)
-- Name: events events_university_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_university_fkey FOREIGN KEY (university) REFERENCES public.universities(id);


--
-- TOC entry 4294 (class 2606 OID 16661)
-- Name: users fk_university_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_university_id FOREIGN KEY (university_id) REFERENCES public.universities(id);


--
-- TOC entry 4301 (class 2606 OID 16552)
-- Name: pending_events pending_events_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pending_events
    ADD CONSTRAINT pending_events_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- TOC entry 4302 (class 2606 OID 16547)
-- Name: pending_events pending_events_university_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.pending_events
    ADD CONSTRAINT pending_events_university_fkey FOREIGN KEY (university) REFERENCES public.universities(id);


--
-- TOC entry 4305 (class 2606 OID 16591)
-- Name: ratings ratings_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id);


--
-- TOC entry 4306 (class 2606 OID 16596)
-- Name: ratings ratings_event_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ratings
    ADD CONSTRAINT ratings_event_id_fkey FOREIGN KEY (event_id) REFERENCES public.events(id);


--
-- TOC entry 4296 (class 2606 OID 16508)
-- Name: rso rso_admin_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rso
    ADD CONSTRAINT rso_admin_fkey FOREIGN KEY (admin) REFERENCES public.users(id);


--
-- TOC entry 4307 (class 2606 OID 16610)
-- Name: rso_members rso_members_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rso_members
    ADD CONSTRAINT rso_members_id_fkey FOREIGN KEY (id) REFERENCES public.users(id);


--
-- TOC entry 4308 (class 2606 OID 16615)
-- Name: rso_members rso_members_rso_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rso_members
    ADD CONSTRAINT rso_members_rso_id_fkey FOREIGN KEY (rso_id) REFERENCES public.rso(id);


--
-- TOC entry 4297 (class 2606 OID 16503)
-- Name: rso rso_university_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rso
    ADD CONSTRAINT rso_university_fkey FOREIGN KEY (university) REFERENCES public.universities(id);



-- Completed on 2024-04-11 13:58:53

--
-- PostgreSQL database dump complete
--

