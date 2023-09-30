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
)

