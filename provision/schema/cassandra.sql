CREATE TABLE IF NOT EXISTS tuser_tuser (
    id bigint PRIMARY KEY,
    timestamp int,
    weight int,
    from_user text,
    to_user text
);

CREATE INDEX IF NOT EXISTS tuser_tuser_to_user ON tuser_tuser (to_user);
