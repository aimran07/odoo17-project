#!/bin/bash
set -e
WORKING_DIR=$(pwd)
PYTHON_VER="3.10.13"

echo "🧹 1. Cleaning up problematic repositories..."
sudo rm -f /etc/apt/sources.list.d/yarn.list
sudo apt-key del 62D54FD4003F6525 2>/dev/null || true

echo "📦 2. Installing System Dependencies (Postgres, LDAP, SASL)..."
sudo apt-get update -y
sudo apt-get install -y postgresql postgresql-contrib libldap2-dev libsasl2-dev libpq-dev python3-dev build-essential wkhtmltopdf

echo "🐘 3. Configuring PostgreSQL Security (Trust Mode)..."
sudo service postgresql start
# This bypasses the 'sudo password' requirement for local DB connections
sudo sed -i 's/scram-sha-256/trust/g' /etc/postgresql/*/main/pg_hba.conf
sudo sed -i 's/md5/trust/g' /etc/postgresql/*/main/pg_hba.conf
sudo service postgresql restart

echo "📂 4. Initializing Python $PYTHON_VER..."
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
if ! command -v pyenv &> /dev/null; then
    curl https://pyenv.run | bash
    eval "$(pyenv init -)"
fi
pyenv install $PYTHON_VER -s
pyenv local $PYTHON_VER

if [ ! -d "odoo" ]; then
    git clone https://www.github.com/odoo/odoo --depth 1 --branch 17.0 odoo
fi

if [ ! -d "odoo-venv" ]; then
    $(pyenv root)/versions/$PYTHON_VER/bin/python -m venv odoo-venv
fi

if [ ! -f "odoo.conf" ]; then
    cat <<EOF > odoo.conf
[options]
admin_passwd = admin
db_host = 127.0.0.1
db_user = odoo
db_password = odoo
db_port = 5432
addons_path = $WORKING_DIR/odoo/addons,$WORKING_DIR/custom_addons
EOF
fi

mkdir -p custom_addons
echo "✅ Infrastructure Ready!"
