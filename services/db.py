import psycopg2
import os
import dotenv

password = os.getenv("DB_PASSWORD")

conn = psycopg2.connect(f"postgresql://neondb_owner:{password}@ep-wispy-rice-ajl2bvhc-pooler.c-3.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require")