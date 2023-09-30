DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS assets;
DROP TABLE IF EXISTS assets_overview;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS users_assets;

CREATE TABLE users (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT        NOT NULL,
    role     TEXT DEFAULT 'user',
    email TEXT
);


-- Accounts Table
CREATE TABLE accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  balance REAL NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Stock Data Table
CREATE TABLE assets (
  symbol TEXT,
  date DATE,
  open REAL,
  high REAL,
  low REAL,
  close REAL,
  volume INTEGER,
  adjusted_close REAL,
  PRIMARY KEY (symbol, date)
);

CREATE TABLE assets_overview(
  symbol TEXT,
  name TEXT,
  description TEXT,
  PRIMARY KEY (symbol)
);


-- Transactions Table
CREATE TABLE transactions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  symbol TEXT NOT NULL,
  type VARCHAR(8) NOT NULL,
  stockPriceDate DATE NOT NULL,
  timestmp DATETIME NOT NULL,
  pricePerShare REAL NOT NULL,
  shares INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Users Assets Table. Provide associations between portfolios and assets
CREATE TABLE users_assets (
  user_id INTEGER NOT NULL,
  symbol TEXT NOT NULL,
  shares INTEGER NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (symbol) REFERENCES assets(symbol)
);


INSERT INTO users (id, username, password,role)
VALUES (1, 'admin', 'pbkdf2:sha256:260000$1swnDpjVMQrscugQ$50bbfd6a0b60812e81ca6e523943efe14cf37c205d4a432a67848c75ff1ad040','admin');
