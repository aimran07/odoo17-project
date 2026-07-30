#!/bin/bash
if [[ "$VIRTUAL_ENV" != *"odoo-venv"* ]]; then
    echo "❌ ERROR: Activate venv first: source odoo-venv/bin/activate"
    exit 1
fi

echo "🆙 Updating Pip and Setuptools..."
pip install --upgrade pip setuptools==67.8.0 wheel

echo "🧹 Patching Odoo 17 requirements.txt..."
cat <<EOF > odoo/requirements.txt
Babel==2.10.3
chardet==4.0.0
cryptography==42.0.8
decorator==5.1.1
docutils==0.17
ebaysdk==2.1.5
freezegun==1.2.1
geoip2==2.9.0
gevent==23.9.1
greenlet==3.3.1
idna==3.6
Jinja2==3.1.2
libsass==0.22.0
lxml==5.2.1
lxml-html-clean==0.4.3
MarkupSafe==2.1.5
num2words==0.5.13
ofxparse==0.21
passlib==1.7.4
Pillow==10.2.0
polib==1.1.1
psutil==5.9.8
psycopg2-binary==2.9.11
pydot==1.4.2
pyopenssl==24.1.0
pyparsing==3.1.2
PyPDF2==2.12.1
python-dateutil==2.8.2
python-ldap==3.4.4
python-stdnum==1.19
pytz==2024.1
pyusb==1.2.1
qrcode==7.4.2
reportlab==4.1.0
requests==2.31.0
urllib3==1.26.15
vobject==0.9.6.1
Werkzeug==3.0.1
XlsxWriter==3.1.9
xlrd==2.0.1
xlwt==1.3.0
zeep==4.2.1
zope.event==5.0
zope.interface==6.2
rjsmin==1.2.0
inotify
EOF

pip install -r odoo/requirements.txt
echo "🚀 Python Environment Ready!"
