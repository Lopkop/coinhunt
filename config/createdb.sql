CREATE TABLE users (
    user_id integer UNIQUE
);

CREATE TABLE coin (
    coin_id integer UNIQUE
);

CREATE TABLE user_coins (
    user_id integer REFERENCES users(user_id) ON DELETE CASCADE,
    coin integer REFERENCES coin(coin_id) ON DELETE CASCADE,
    top integer DEFAULT 1,
    votes integer DEFAULT '-1'::integer
);