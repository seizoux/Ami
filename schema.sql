CREATE TABLE public.antispam (
    guild_id character varying,
    toggle text
);


ALTER TABLE public.antispam OWNER TO postgres;

CREATE TABLE public.blacklist (
    user_id character varying NOT NULL,
    reason text
);


ALTER TABLE public.blacklist OWNER TO postgres;

CREATE TABLE public.items (
    user_id character varying,
    water_bottles bigint DEFAULT 0 NOT NULL,
    redrums bigint DEFAULT 0 NOT NULL,
    rifles bigint DEFAULT 0 NOT NULL,
    weed bigint DEFAULT 0 NOT NULL,
    fish_rods bigint DEFAULT 0 NOT NULL,
    computers bigint DEFAULT 0 NOT NULL,
    ami_flowers bigint DEFAULT 0 NOT NULL,
    common_chests bigint DEFAULT 0 NOT NULL,
    rare_chests bigint DEFAULT 0 NOT NULL,
    epic_chests bigint DEFAULT 0 NOT NULL
);


ALTER TABLE public.items OWNER TO postgres;

CREATE TABLE public.levels (
    guild_id character varying,
    user_id character varying,
    level bigint,
    xp bigint,
    level_bg text
);


ALTER TABLE public.levels OWNER TO postgres;

CREATE TABLE public.numbers (
    user_id character varying,
    hugs bigint DEFAULT 0 NOT NULL,
    slaps bigint DEFAULT 0 NOT NULL,
    kills bigint DEFAULT 0 NOT NULL,
    kisses bigint DEFAULT 0 NOT NULL,
    licks bigint DEFAULT 0 NOT NULL,
    punches bigint DEFAULT 0 NOT NULL,
    pats bigint DEFAULT 0 NOT NULL
);


ALTER TABLE public.numbers OWNER TO postgres;

CREATE TABLE public.premium (
    user_id character varying,
    sub_date text
);


ALTER TABLE public.premium OWNER TO postgres;

CREATE TABLE public.testers (
    id character varying NOT NULL
);


ALTER TABLE public.testers OWNER TO postgres;

CREATE TABLE public.users (
    user_id character varying,
    wallet bigint,
    bank bigint,
    tz character varying,
    pet_name text,
    pet_tag text,
    investments bigint DEFAULT 0 NOT NULL,
    total_earn bigint DEFAULT 0 NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

CREATE TABLE public.welcome (
    guild_id character varying NOT NULL,
    msg text,
    role_name character varying,
    role character varying,
    channel character varying,
    embed character varying,
    welc character varying
);


ALTER TABLE public.welcome OWNER TO postgres;
