import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgresql://admin:password123@localhost:5432/mlb_engine',
});

export const query = (text: string, params?: any[]) => pool.query(text, params);
