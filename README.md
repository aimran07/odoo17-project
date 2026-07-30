
# 📂 Preparation

Before starting, ensure your three master scripts are saved in the root directory:

* `setup_env.sh`
* `install_deps.sh`
* `run.sh`

### 1️⃣ Open the Terminal

### 2️⃣ Grant Execution Permissions

```bash
chmod +x *.sh
```

---

# 🛠️ Step 1: Infrastructure Initialization

This step installs the PostgreSQL server, required system headers, and the Odoo source code.

### ▶ Run:

```bash
./setup_env.sh
```

### ✅ Status Check

Wait until you see:

```
✅ Infrastructure Ready!
```

---

# 🐍 Step 2: Python Environment & Dependencies

This step creates the virtual environment and installs the patched Odoo dependencies.

### 1️⃣ Activate the Virtual Environment

```bash
source odoo-venv/bin/activate
```

### 2️⃣ Install Dependencies

```bash
./install_deps.sh
```

### ✅ Status Check

Wait until you see:

```
🚀 Python Environment Ready!
```

---

# 🚀 Step 3: Launch Odoo

This step starts the database services and launches the Odoo web server.

### ▶ Run:

```bash
./run.sh
```

### ✅ Status Check

You should see:

```
HTTP service (werkzeug) running on localhost:8069
```

---

# 🌐 Step 4: Web Browser Configuration

1. Click **"Open in Browser"** from the Codespaces popup.
2. Complete the **Database Management** form using the following values:

| Field           | Value      |
| --------------- | ---------- |
| Master Password | `admin`    |
| Database Name   | `odoo` |
| Email (Login)   | `admin`    |
| Password        | `admin`    |

3. Click **Create Database**

⏳ This process may take up to 2 minutes.

---

# 🔄 Development Enhancements

This project includes additional development utilities to speed up customization and debugging.

---

## ♻️ Auto Reload + Debug Console

The Odoo server is configured to run in **development mode** with:

* ✅ **Auto-reload** enabled (Python & XML changes reload automatically)
* 🐞 **Debug console** enabled
* 🔎 Enhanced logging for faster troubleshooting

This means:

* No need to manually restart the server after code changes
* Faster development workflow
* Immediate feedback during module updates

If needed, you can verify debug mode is active by checking the server logs after startup.

---

## 📦 Custom Development Module

A custom module has been added to simplify development tasks.

### 🔧 Purpose

* Quick upgrades of custom modules
* Rapid reloading of installed modules
* Faster iteration during development

The module is automatically available after database creation.

---

## ⚡ Quick Upgrade Endpoint

A shortcut route has been added for fast module upgrades:

```
/q
```

### ▶ Usage

Open in your browser:

```
http://localhost:8069/q
```

### ✅ What It Does

* Automatically upgrades custom modules
* Reloads modified installed modules
* Avoids manual upgrade steps from the Apps menu
* Saves development time

⚠️ **Note:** This route is intended for development use only.
Do not enable in production environments.

---

## 🚀 Recommended Development Workflow

1. Start Odoo:

   ```bash
   ./run.sh
   ```

2. Make changes in your custom module.

3. Open:

   ```
   http://localhost:8069/q
   ```

4. Refresh your browser.

No manual restart required thanks to auto-reload 🎉

---
