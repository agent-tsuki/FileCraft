<pre lang="markdown">

# 🧠 FileCraft – Smart File & Image Processor (FastAPI)

**FileCraft** is a modern, memory-efficient API built with **FastAPI** that helps you:

- 📄 Convert any uploaded file to **Base64** (with optional compression)
- 🖼️ Convert **images** from one format to another (e.g., JPG → PNG, WebP)
- 📦 Compress **files** and **images** using smart techniques  
  - 🖼️ Images: via **Pillow**
  - 📁 Files: via **zlib**
  - 🧩 Outputs with a custom `.wxct` extension

---

## 🚀 Features

✅ Stream-based (no file system dependency)  
✅ Removes metadata (EXIF, ICC, etc.) from images  
✅ Adjustable image quality (`JPEG`, `WebP`)  
✅ Compresses binary files using zlib  
✅ Docker & cloud-ready  
✅ Works entirely **in-memory** for speed & security

---

## 🛠️ Tech Stack

| Tool             | Purpose                 |
|------------------|-------------------------|
| 🐍 Python 3.12+  | Core language           |
| ⚡ FastAPI       | Web framework           |
| 🧪 Zlib          | Binary file compression |
| 🖼️ Pillow        | Image processing        |
| 🐳 Docker        | Deployment (optional)   |
| 🔥 Uvicorn       | ASGI server             |

---

## 📂 Project Structure

├── app
│   ├── dependencies.py
│   ├── helpers
│   │   ├── constants.py
│   │   ├── converter.py
│   │   ├── file_validator.py
│   │   ├── __init__.py
|   |
│   ├── __init__.py
│   ├── main.py
│   ├── models
│   │   └── __init__.py
|   |
│   └── router
│       ├── auth
│       │   └── __init__.py
|       |
│       ├── converters
│       │   ├── base64.py
│       │   ├── compression.py
│       │   ├── images.py
│       │   ├── __init__.py
|       |
│       ├── decoder
│       │   └── __init__.py
│       ├── __init__.py
|
├── config
│   ├── database.py
│   ├── __init__.py
│   └── settings
│       ├── base.py
│       ├── config.py
│       ├── __init__.py
|
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── pyproject.toml
├── README.md
└── requirements.txt

---

## ⚙️ Getting Started

### 🧪 1. Local Setup

```bash
git clone https://github.com/yourusername/filecraft.git
cd filecraft

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### ▶️ 2. Run App (Dev Mode)

```bash
uvicorn app.main:filecraft --reload --host 0.0.0.0 --port 8000
```
## or you can chose docker file
### 🐳 3. Run with Docker
```bash
docker build -t filecraft .
docker run -p 8000:8000 filecraft
```

### 👨‍💻 Author
Built with ❤️ and performance in mind by Shivam Pandey.
Optimized for speed, low memory usage, and a seamless developer experience.

