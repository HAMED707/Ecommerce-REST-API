#!/bin/bash
DB_NAME="ecommerce_db"
DB_USER="ecommerce_user"
DB_PASS="HAMED"

# Step 1: Create DB and user
sudo -u postgres psql -v ON_ERROR_STOP=1 <<EOF
CREATE DATABASE "$DB_NAME";
CREATE USER "$DB_USER" WITH PASSWORD '$DB_PASS';
ALTER ROLE "$DB_USER" SET client_encoding TO 'utf8';
ALTER ROLE "$DB_USER" SET default_transaction_isolation TO 'read committed';
ALTER ROLE "$DB_USER" SET timezone TO 'UTC';
EOF

# Step 2: Connect to DB and set permissions
sudo -u postgres psql -d "$DB_NAME" -v ON_ERROR_STOP=1 <<EOF
GRANT USAGE ON SCHEMA public TO "$DB_USER";
GRANT CREATE ON SCHEMA public TO "$DB_USER";
ALTER DATABASE "$DB_NAME" OWNER TO "$DB_USER";
EOF

echo "✅ Database and user created with proper permissions."