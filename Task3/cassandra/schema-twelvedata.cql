USE kafkapipeline;
CREATE TABLE IF NOT EXISTS kafkapipeline.twelvedata (
  datetime TIMESTAMP,
  macd float,
  macd_hist float,
  macd_signal float,
  PRIMARY KEY (datetime)
);