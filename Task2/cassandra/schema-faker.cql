USE kafkapipeline;
CREATE TABLE IF NOT EXISTS kafkapipeline.fakerdata (
  name TEXT,
  address TEXT,
  year INT,
  phone_number TEXT,
  credit_card_number TEXT,
  company_name TEXT,
  city TEXT,
  job_name TEXT,
  user_agent TEXT,
  bank TEXT,
  PRIMARY KEY (name, address)
);