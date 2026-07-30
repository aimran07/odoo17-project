#!/bin/bash
echo "🐘 Starting Database Services..."
sudo service postgresql start
sleep 2

# Create Odoo DB role if it doesn't exist
psql -h 127.0.0.1 -U postgres -c "CREATE USER odoo WITH PASSWORD 'odoo' SUPERUSER;" 2>/dev/null || \
psql -h 127.0.0.1 -U postgres -c "ALTER USER odoo WITH PASSWORD 'odoo' SUPERUSER;"

echo "🌐 Clearing Port 8069..."
OS_PID=$(lsof -t -i:8069)
[ ! -z "$OS_PID" ] && kill -9 $OS_PID

echo "🚀 Launching Odoo 17..."
echo "------------------------------------------------"
echo "MASTER PASSWORD: admin"
echo "URL: https://${CODESPACE_NAME}-8069.app.github.dev"
echo "------------------------------------------------"

./odoo-venv/bin/python odoo/odoo-bin -c odoo.conf "$@"
