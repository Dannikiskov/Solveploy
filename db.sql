--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3 (Debian 16.3-1.pgdg120+1)
-- Dumped by pg_dump version 16.3 (Debian 16.3-1.pgdg120+1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: maxsat_feature_vectors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.maxsat_feature_vectors (
    id integer NOT NULL,
    features character varying(2047)
);


ALTER TABLE public.maxsat_feature_vectors OWNER TO postgres;

--
-- Name: maxsat_feature_vectors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.maxsat_feature_vectors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.maxsat_feature_vectors_id_seq OWNER TO postgres;

--
-- Name: maxsat_feature_vectors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.maxsat_feature_vectors_id_seq OWNED BY public.maxsat_feature_vectors.id;


--
-- Name: maxsat_solver_featvec_time; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.maxsat_solver_featvec_time (
    id integer NOT NULL,
    solver_id integer,
    feature_vec_id integer,
    execution_time double precision NOT NULL
);


ALTER TABLE public.maxsat_solver_featvec_time OWNER TO postgres;

--
-- Name: maxsat_solver_featvec_time_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.maxsat_solver_featvec_time_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.maxsat_solver_featvec_time_id_seq OWNER TO postgres;

--
-- Name: maxsat_solver_featvec_time_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.maxsat_solver_featvec_time_id_seq OWNED BY public.maxsat_solver_featvec_time.id;


--
-- Name: maxsat_solvers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.maxsat_solvers (
    id integer NOT NULL,
    name character varying(255)
);


ALTER TABLE public.maxsat_solvers OWNER TO postgres;

--
-- Name: maxsat_solvers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.maxsat_solvers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.maxsat_solvers_id_seq OWNER TO postgres;

--
-- Name: maxsat_solvers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.maxsat_solvers_id_seq OWNED BY public.maxsat_solvers.id;


--
-- Name: mzn_feature_vectors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mzn_feature_vectors (
    id integer NOT NULL,
    features double precision[]
);


ALTER TABLE public.mzn_feature_vectors OWNER TO postgres;

--
-- Name: mzn_feature_vectors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mzn_feature_vectors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mzn_feature_vectors_id_seq OWNER TO postgres;

--
-- Name: mzn_feature_vectors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mzn_feature_vectors_id_seq OWNED BY public.mzn_feature_vectors.id;


--
-- Name: mzn_solver_featvec_time; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mzn_solver_featvec_time (
    id integer NOT NULL,
    solver_id integer,
    feature_vec_id integer,
    opt_value character varying(2047),
    opt_goal character varying(2047),
    execution_time double precision NOT NULL,
    status character varying(2047),
    result character varying(2047)
);


ALTER TABLE public.mzn_solver_featvec_time OWNER TO postgres;

--
-- Name: mzn_solver_featvec_time_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mzn_solver_featvec_time_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mzn_solver_featvec_time_id_seq OWNER TO postgres;

--
-- Name: mzn_solver_featvec_time_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mzn_solver_featvec_time_id_seq OWNED BY public.mzn_solver_featvec_time.id;


--
-- Name: mzn_solvers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mzn_solvers (
    id integer NOT NULL,
    name character varying(255)
);


ALTER TABLE public.mzn_solvers OWNER TO postgres;

--
-- Name: mzn_solvers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mzn_solvers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mzn_solvers_id_seq OWNER TO postgres;

--
-- Name: mzn_solvers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mzn_solvers_id_seq OWNED BY public.mzn_solvers.id;


--
-- Name: sat_feature_vectors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sat_feature_vectors (
    id integer NOT NULL,
    features double precision[]
);


ALTER TABLE public.sat_feature_vectors OWNER TO postgres;

--
-- Name: sat_feature_vectors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sat_feature_vectors_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sat_feature_vectors_id_seq OWNER TO postgres;

--
-- Name: sat_feature_vectors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sat_feature_vectors_id_seq OWNED BY public.sat_feature_vectors.id;


--
-- Name: sat_solver_featvec_time; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sat_solver_featvec_time (
    id integer NOT NULL,
    solver_id integer,
    feature_vec_id integer,
    execution_time double precision NOT NULL,
    status character varying(2047)
);


ALTER TABLE public.sat_solver_featvec_time OWNER TO postgres;

--
-- Name: sat_solver_featvec_time_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sat_solver_featvec_time_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sat_solver_featvec_time_id_seq OWNER TO postgres;

--
-- Name: sat_solver_featvec_time_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sat_solver_featvec_time_id_seq OWNED BY public.sat_solver_featvec_time.id;


--
-- Name: sat_solvers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sat_solvers (
    id integer NOT NULL,
    name character varying(255)
);


ALTER TABLE public.sat_solvers OWNER TO postgres;

--
-- Name: sat_solvers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sat_solvers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.sat_solvers_id_seq OWNER TO postgres;

--
-- Name: sat_solvers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sat_solvers_id_seq OWNED BY public.sat_solvers.id;


--
-- Name: maxsat_feature_vectors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_feature_vectors ALTER COLUMN id SET DEFAULT nextval('public.maxsat_feature_vectors_id_seq'::regclass);


--
-- Name: maxsat_solver_featvec_time id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_solver_featvec_time ALTER COLUMN id SET DEFAULT nextval('public.maxsat_solver_featvec_time_id_seq'::regclass);


--
-- Name: maxsat_solvers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_solvers ALTER COLUMN id SET DEFAULT nextval('public.maxsat_solvers_id_seq'::regclass);


--
-- Name: mzn_feature_vectors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_feature_vectors ALTER COLUMN id SET DEFAULT nextval('public.mzn_feature_vectors_id_seq'::regclass);


--
-- Name: mzn_solver_featvec_time id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_solver_featvec_time ALTER COLUMN id SET DEFAULT nextval('public.mzn_solver_featvec_time_id_seq'::regclass);


--
-- Name: mzn_solvers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_solvers ALTER COLUMN id SET DEFAULT nextval('public.mzn_solvers_id_seq'::regclass);


--
-- Name: sat_feature_vectors id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_feature_vectors ALTER COLUMN id SET DEFAULT nextval('public.sat_feature_vectors_id_seq'::regclass);


--
-- Name: sat_solver_featvec_time id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_solver_featvec_time ALTER COLUMN id SET DEFAULT nextval('public.sat_solver_featvec_time_id_seq'::regclass);


--
-- Name: sat_solvers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_solvers ALTER COLUMN id SET DEFAULT nextval('public.sat_solvers_id_seq'::regclass);


--
-- Data for Name: maxsat_feature_vectors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.maxsat_feature_vectors (id, features) FROM stdin;
\.


--
-- Data for Name: maxsat_solver_featvec_time; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.maxsat_solver_featvec_time (id, solver_id, feature_vec_id, execution_time) FROM stdin;
\.


--
-- Data for Name: maxsat_solvers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.maxsat_solvers (id, name) FROM stdin;
\.


--
-- Data for Name: mzn_feature_vectors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mzn_feature_vectors (id, features) FROM stdin;
1	{2,3.16993,1.58496,0,0,0,0,0,0,0,0,0,0,9,14.98,2,3.16993,1.58496,2,3.16993,1.58496,9,0,1.28571,27,28.5293,14.2647,0,0,0,0,0,9,7,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,2.57143,3,0.942857,0.388889,0,0,0,1.84237,0,1.37878,0,9.07682,11.0947,5,3,1.5,0,3,0.6,0,2,7,0.285714,0.777778,18,21,6.6}
2	{2,4,2,0,0,0,0,0,0,0,0,0,0,36,72,2,4,2,2,4,2,36,0,9,108,144,72,0,0,0,0,0,36,4,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,18,4,0.222222,0,0,0,0,0,0,0,0,16.6797,8,18,4,0.222222,0,4,0.222222,4,2,4,1.5,0.111111,72,16,0.888889}
\.


--
-- Data for Name: mzn_solver_featvec_time; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mzn_solver_featvec_time (id, solver_id, feature_vec_id, opt_value, opt_goal, execution_time, status, result) FROM stdin;
1	1	1		satisfy	85.42180061340332	SATISFIED	\N
2	1	2	\N	satisfy	81.03299140930176	SATISFIED	\N
\.


--
-- Data for Name: mzn_solvers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mzn_solvers (id, name) FROM stdin;
1	chuffed
\.


--
-- Data for Name: sat_feature_vectors; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sat_feature_vectors (id, features) FROM stdin;
1	{91,20,4.55,0.21978021978021978,0.15,0.14332598935174987,0.10989010989010989,0.18681318681318682,1.9172155185650603,0.15,0,0.15,0.15,0,0.17692307692307693,0.08074534161490683,0.14285714285714285,0.1978021978021978,0.5091575091575091,0.5769766231874367,0.33333333333333326,1,0.5769287655548124,0.24090644649468176,0.735875937868339,0,0.5,2.362727307541353,0.17727725725280277,0,1,1,0.5384615384615384,0.08076923076923077,0.2518844704976002,0.04395604395604396,0.12087912087912088,1.8294606949926697}
2	{91,20,4.55,0.21978021978021978,0.15,0.22133152146550614,0.06593406593406594,0.1978021978021978,2.1377932496938294,0.15,0,0.15,0.15,0,0.16483516483516483,0.1505545305418162,0.08791208791208792,0.1978021978021978,0.5384615384615384,0.5714285714285715,0.33333333333333326,1,0.6172417697303416,0.22631486160897923,0.6796788429798255,0,0.5,2.484366839973802,0.15382142328753035,0,1,1,0.5384615384615384,0.08076923076923077,0.25912921026858377,0.03296703296703297,0.14285714285714285,1.6908312588806806}
3	{91,20,4.55,0.21978021978021978,0.15,0.22011573901206766,0.0989010989010989,0.2087912087912088,1.9468389992053852,0.15,0,0.15,0.15,0,0.15824175824175823,0.13608276348795437,0.13186813186813187,0.1978021978021978,0.49450549450549447,0.5772076959637973,0.33333333333333326,1,0.5530981571641704,0.22581841404209826,0.7235815981904998,0.05263157894736836,0.5714285714285714,2.6229962760857912,0.16339804893342547,0,1,1,0.5054945054945055,0.07582417582417583,0.3301677028954932,0.03296703296703297,0.12087912087912088,2.0558449546770494}
4	{91,20,4.55,0.21978021978021978,0.15,0.22493944495009582,0.08791208791208792,0.21978021978021978,2.1377932496938294,0.15,0,0.15,0.15,0,0.16373626373626374,0.1179758109479661,0.12087912087912088,0.1978021978021978,0.4652014652014652,0.5708525656816333,0.33333333333333326,1,0.49734048623153665,0.312676133635886,0.8040063565716554,0,1,2.857102837442002,0.2513935989915007,0,1,1,0.5604395604395604,0.08406593406593407,0.36572117211863475,0,0.14285714285714285,2.0820073618652772}
5	{91,20,4.55,0.21978021978021978,0.15,0.23882671520444015,0.0989010989010989,0.24175824175824176,2.207107967749824,0.15,0,0.15,0.15,0,0.16483516483516483,0.12110601416389968,0.12087912087912088,0.2087912087912088,0.4725274725274725,0.5734338607413001,0.33333333333333326,1,0.5123507024144506,0.17799337916984975,0.8090233637167388,0,0.5,2.1639556568820564,0.14400080233530074,0,1,1,0.4835164835164835,0.07252747252747253,0.3263736246748184,0.03296703296703297,0.10989010989010989,2.01615371726138}
\.


--
-- Data for Name: sat_solver_featvec_time; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sat_solver_featvec_time (id, solver_id, feature_vec_id, execution_time, status) FROM stdin;
1	1	1	6.985664367675781e-05	SATISFIED
2	1	2	0.00011277198791503906	SATISFIED
3	1	3	8.320808410644531e-05	SATISFIED
4	1	4	2.6464462280273438e-05	SATISFIED
5	1	5	4.410743713378906e-05	SATISFIED
6	2	2	0.00010633468627929688	SATISFIED
7	2	1	7.176399230957031e-05	SATISFIED
8	2	5	2.956390380859375e-05	SATISFIED
9	3	2	0.00040912628173828125	SATISFIED
10	2	4	3.647804260253906e-05	SATISFIED
11	2	3	4.792213439941406e-05	SATISFIED
12	3	4	3.933906555175781e-05	SATISFIED
13	3	1	3.6716461181640625e-05	SATISFIED
14	3	5	3.600120544433594e-05	SATISFIED
15	3	3	3.266334533691406e-05	SATISFIED
16	4	3	5.698204040527344e-05	SATISFIED
17	4	5	2.8848648071289062e-05	SATISFIED
18	4	4	2.6464462280273438e-05	SATISFIED
19	4	2	6.365776062011719e-05	SATISFIED
20	4	1	3.337860107421875e-05	SATISFIED
\.


--
-- Data for Name: sat_solvers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sat_solvers (id, name) FROM stdin;
1	cadical103
2	cadical153
3	gluecard41
4	glucose30
\.


--
-- Name: maxsat_feature_vectors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.maxsat_feature_vectors_id_seq', 1, false);


--
-- Name: maxsat_solver_featvec_time_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.maxsat_solver_featvec_time_id_seq', 1, false);


--
-- Name: maxsat_solvers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.maxsat_solvers_id_seq', 1, false);


--
-- Name: mzn_feature_vectors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mzn_feature_vectors_id_seq', 2, true);


--
-- Name: mzn_solver_featvec_time_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mzn_solver_featvec_time_id_seq', 2, true);


--
-- Name: mzn_solvers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mzn_solvers_id_seq', 1, true);


--
-- Name: sat_feature_vectors_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sat_feature_vectors_id_seq', 5, true);


--
-- Name: sat_solver_featvec_time_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sat_solver_featvec_time_id_seq', 20, true);


--
-- Name: sat_solvers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sat_solvers_id_seq', 4, true);


--
-- Name: maxsat_feature_vectors maxsat_feature_vectors_features_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_feature_vectors
    ADD CONSTRAINT maxsat_feature_vectors_features_key UNIQUE (features);


--
-- Name: maxsat_feature_vectors maxsat_feature_vectors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_feature_vectors
    ADD CONSTRAINT maxsat_feature_vectors_pkey PRIMARY KEY (id);


--
-- Name: maxsat_solver_featvec_time maxsat_solver_featvec_time_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_solver_featvec_time
    ADD CONSTRAINT maxsat_solver_featvec_time_pkey PRIMARY KEY (id);


--
-- Name: maxsat_solvers maxsat_solvers_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_solvers
    ADD CONSTRAINT maxsat_solvers_name_key UNIQUE (name);


--
-- Name: maxsat_solvers maxsat_solvers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_solvers
    ADD CONSTRAINT maxsat_solvers_pkey PRIMARY KEY (id);


--
-- Name: mzn_feature_vectors mzn_feature_vectors_features_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_feature_vectors
    ADD CONSTRAINT mzn_feature_vectors_features_key UNIQUE (features);


--
-- Name: mzn_feature_vectors mzn_feature_vectors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_feature_vectors
    ADD CONSTRAINT mzn_feature_vectors_pkey PRIMARY KEY (id);


--
-- Name: mzn_solver_featvec_time mzn_solver_featvec_time_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_solver_featvec_time
    ADD CONSTRAINT mzn_solver_featvec_time_pkey PRIMARY KEY (id);


--
-- Name: mzn_solvers mzn_solvers_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_solvers
    ADD CONSTRAINT mzn_solvers_name_key UNIQUE (name);


--
-- Name: mzn_solvers mzn_solvers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_solvers
    ADD CONSTRAINT mzn_solvers_pkey PRIMARY KEY (id);


--
-- Name: sat_feature_vectors sat_feature_vectors_features_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_feature_vectors
    ADD CONSTRAINT sat_feature_vectors_features_key UNIQUE (features);


--
-- Name: sat_feature_vectors sat_feature_vectors_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_feature_vectors
    ADD CONSTRAINT sat_feature_vectors_pkey PRIMARY KEY (id);


--
-- Name: sat_solver_featvec_time sat_solver_featvec_time_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_solver_featvec_time
    ADD CONSTRAINT sat_solver_featvec_time_pkey PRIMARY KEY (id);


--
-- Name: sat_solvers sat_solvers_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_solvers
    ADD CONSTRAINT sat_solvers_name_key UNIQUE (name);


--
-- Name: sat_solvers sat_solvers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_solvers
    ADD CONSTRAINT sat_solvers_pkey PRIMARY KEY (id);


--
-- Name: maxsat_solver_featvec_time maxsat_solver_featvec_time_feature_vec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_solver_featvec_time
    ADD CONSTRAINT maxsat_solver_featvec_time_feature_vec_id_fkey FOREIGN KEY (feature_vec_id) REFERENCES public.maxsat_feature_vectors(id);


--
-- Name: maxsat_solver_featvec_time maxsat_solver_featvec_time_solver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.maxsat_solver_featvec_time
    ADD CONSTRAINT maxsat_solver_featvec_time_solver_id_fkey FOREIGN KEY (solver_id) REFERENCES public.maxsat_solvers(id);


--
-- Name: mzn_solver_featvec_time mzn_solver_featvec_time_feature_vec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_solver_featvec_time
    ADD CONSTRAINT mzn_solver_featvec_time_feature_vec_id_fkey FOREIGN KEY (feature_vec_id) REFERENCES public.mzn_feature_vectors(id);


--
-- Name: mzn_solver_featvec_time mzn_solver_featvec_time_solver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mzn_solver_featvec_time
    ADD CONSTRAINT mzn_solver_featvec_time_solver_id_fkey FOREIGN KEY (solver_id) REFERENCES public.mzn_solvers(id);


--
-- Name: sat_solver_featvec_time sat_solver_featvec_time_feature_vec_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_solver_featvec_time
    ADD CONSTRAINT sat_solver_featvec_time_feature_vec_id_fkey FOREIGN KEY (feature_vec_id) REFERENCES public.sat_feature_vectors(id);


--
-- Name: sat_solver_featvec_time sat_solver_featvec_time_solver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sat_solver_featvec_time
    ADD CONSTRAINT sat_solver_featvec_time_solver_id_fkey FOREIGN KEY (solver_id) REFERENCES public.sat_solvers(id);


--
-- PostgreSQL database dump complete
--

