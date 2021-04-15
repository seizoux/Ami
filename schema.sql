CREATE TABLE IF NOT EXISTS blacklist (
    user_id character varying NOT NULL,
    reason text
);
CREATE TABLE IF NOT EXISTS items (
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
CREATE TABLE IF NOT EXISTS levels (
    guild_id character varying,
    user_id character varying,
    level bigint,
    xp bigint,
    level_bg text
);
CREATE TABLE IF NOT EXISTS numbers (
    user_id character varying,
    hugs bigint DEFAULT 0 NOT NULL,
    slaps bigint DEFAULT 0 NOT NULL,
    kills bigint DEFAULT 0 NOT NULL,
    kisses bigint DEFAULT 0 NOT NULL,
    licks bigint DEFAULT 0 NOT NULL
);

CREATE TABLE IF NOT EXISTS premium (
    user_id character varying,
    sub_date text
);
CREATE TABLE IF NOT EXISTS testers (
    id character varying NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    user_id character varying,
    wallet bigint,
    bank bigint,
    tz character varying,
    pet_name text,
    pet_tag text,
    investments bigint DEFAULT 0 NOT NULL,
    total_earn bigint DEFAULT 0 NOT NULL
);
CREATE TABLE IF NOT EXISTS welcome (
    guild_id character varying NOT NULL,
    msg text,
    role_name character varying,
    role character varying,
    channel character varying,
    embed character varying,
    welc character varying
);
