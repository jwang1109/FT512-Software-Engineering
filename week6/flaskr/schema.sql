DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;
DROP TABLE IF EXISTS stock_data;


CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE stock_data (
   stock_symbol      VARCHAR(5)    NOT NULL,  
   closing_date      DATE          NOT NULL,
   open_price        DECIMAL(16,6) NOT NULL,
   high_price        DECIMAL(16,6) NOT NULL,
   low_price         DECIMAL(16,6) NOT NULL,
   close_price       DECIMAL(16,6) NOT NULL,
   adj_close_price   DECIMAL(16,6) NOT NULL,
   volume            BIGINT        NOT NULL,
   PRIMARY KEY (stock_symbol, closing_date)
);




