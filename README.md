# 🚀 SmartUploader

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/PostgreSQL-15-336791?style=for-the-badge&logo=postgresql" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/Nginx-Reverse%20Proxy-009639?style=for-the-badge&logo=nginx" alt="Nginx">
  <img src="https://img.shields.io/badge/Frontend-Vanilla%20JS-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
</p>

<p align="center">
  <b>A full-stack image hosting web application for uploading, storing, managing, and sharing images.</b>
</p>

<p align="center">
  Built with Python, PostgreSQL, Docker, and Nginx as a learning project focused on backend, database, frontend, and DevOps practices.
</p>

---

## ✨ Overview

**SmartUploader** is a full-stack image hosting platform with a clean UI and a practical architecture.

It allows users to:

- 📤 upload images
- 🖼️ preview uploaded files
- 🔗 get direct image URLs
- 🗑️ delete images
- 🗄️ store metadata in PostgreSQL
- 🐳 run the full project with Docker Compose
- 💾 create and restore database backups

This project was built as a **portfolio-ready demonstration** of:

- backend development
- file handling
- database integration
- frontend interactivity
- containerized deployment

---

## 🌟 Features

- 📂 Image upload via file picker and drag & drop
- ✅ Frontend and backend validation
- 🆔 UUID-based physical filenames for safe storage
- 🏷️ Clean UI display names like `image01.jpg`
- 🗄️ PostgreSQL metadata storage
- 🖼️ Separate image gallery page
- 🗑️ Deletion of both the physical file and DB record
- 📋 Copy image URL to clipboard
- 🌐 Nginx reverse proxy + static file serving
- 🐳 Dockerized multi-service architecture
- 💾 Backup and restore script for PostgreSQL
- 📝 Logging of upload and delete actions to `logs/app.log`
- 📄 Paginated image gallery (10 images per page)
 
---

## 🛠️ Tech Stack

### Backend
- **Python**
- **http.server**
- **PostgreSQL**
- **psycopg2**

### Frontend
- **HTML**
- **CSS**
- **Vanilla JavaScript**

### Infrastructure
- **Docker**
- **Docker Compose**
- **Nginx**

---

## 🧠 How It Works

### 📤 Upload Flow

1. The user selects or drags an image file
2. The frontend validates size and type
3. The file is sent to the backend using `FormData`
4. The backend validates it again
5. A UUID filename is generated
6. The image is saved to the `images/` directory
7. Metadata is stored in PostgreSQL
8. The server returns:
   - stored filename
   - display name
   - relative URL
   - public URL

### 🖼️ Gallery Flow

The gallery page:

- requests paginated images from the backend
- renders image preview, display name, original filename, size, upload time, file type, and URL
- provides a delete button for each image
- supports pagination for large image collections

When deleting:

1. JavaScript sends a delete request to the backend
2. The backend deletes the physical file from storage
3. The backend deletes the corresponding database row
4. The gallery refreshes automatically

### 🏷️ Display Names

Real files are stored using UUID names such as:

`73daa22c-c383-4459-8cd3-37b998f978f4.jpg`

But the interface displays cleaner names like:

- `image01.jpg`
- `image02.jpg`
- `image03.png`

This keeps storage safe and unique while making the UI much more readable.

---

## 📁 Project Structure

~~~text
group6_image_hosting_server/
├── backups/
├── config/
│   ├── init.sql
│   └── nginx.conf
├── images/
├── scripts/
│   └── backup.py
├── src/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── img/
│   │   │   ├── Cat.png
│   │   │   ├── delete.png
│   │   │   ├── Eric.png
│   │   │   ├── Griz.png
│   │   │   ├── Group.png
│   │   │   ├── Nord.png
│   │   │   ├── upload-cloud.png
│   │   │   └── Zero.png
│   │   └── js/
│   │       ├── images.js
│   │       ├── index.js
│   │       └── upload.js
│   ├── templates/
│   │   ├── images.html
│   │   ├── index.html
│   │   └── upload.html
│   ├── app.py
│   ├── database.py
│   ├── file_handler.py
│   └── validators.py
├── .env
├── .env.example
├── .gitignore
├── compose.yaml
├── Dockerfile
├── README.md
└── requirements.txt
~~~

---

## 🗄️ Database Schema

The project stores image metadata in a PostgreSQL table called `images`.

### Stored fields

- `filename` — actual UUID filename
- `display_name` — user-facing image name
- `original_name` — original uploaded filename
- `size` — file size in bytes
- `file_type` — MIME type
- `upload_time` — upload timestamp

This design separates **real storage names** from **UI-friendly names**.

---

## 🌍 Application Pages

### 🏠 Landing Page
A simple homepage introducing the project and redirecting users to the upload workflow.

### 📤 Upload Page
Users can:

- drag and drop files
- browse images manually
- upload files
- copy generated links

### 🖼️ Images Page
Users can:

- preview uploaded images
- view display names and original filenames
- see file size, upload time, and MIME type
- open direct image URLs
- delete images
- navigate through paginated results

---

## 💾 Backup & Restore

The project includes a PostgreSQL backup utility inside:

`scripts/backup.py`

### Available commands

~~~bash
python scripts/backup.py create
python scripts/backup.py list
python scripts/backup.py restore <backup_file.sql>
~~~

### What it does

- `create` → creates a new `.sql` backup inside `backups/`
- `list` → shows all available backups
- `restore` → restores the database from a selected backup file

---

## 🚀 Getting Started

### 1. Clone the repository

~~~bash
git clone https://github.com/glom4oblom/group6_image_hosting_server.git
cd group6_image_hosting_server
~~~

### 2. Create `.env`

~~~env
# Database Configuration
DB_HOST=db
DB_NAME=group6_image_hosting_server_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432

# Server Configuration
PORT=8000

# PostgreSQL Docker Configuration
POSTGRES_DB=group6_image_hosting_server_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
~~~

### 3. Run the project with Docker Compose

~~~bash
docker compose up --build
~~~

### 4. Open the app

- 🌐 Through Nginx: `http://localhost:8080`
- ⚙️ Python app directly: `http://localhost:8000`

---

## 🔒 Validation Rules

Supported formats:

- JPG
- JPEG
- PNG
- GIF

Maximum size:

- **5 MB**

Validation is implemented on both:

- frontend
- backend

---

## 📝 Logging

The application writes runtime logs to:

`logs/app.log`

Logged events include:

- successful uploads
- successful deletions
- server-side errors

## 🐳 Docker Architecture

The project uses 3 services:

### `db`
- PostgreSQL database
- initialized with `config/init.sql`

### `app`
- Python backend server
- handles uploads, API logic, and database operations

### `nginx`
- reverse proxy
- serves static assets
- serves uploaded images directly

This architecture makes the project much closer to a real production-like setup than a basic single-script application.

---

## 📚 What I Practiced in This Project

- Building a full-stack web application
- Designing backend endpoints in Python
- Handling file uploads safely
- Validating files on both client and server
- Working with PostgreSQL
- Separating storage logic from UI logic
- Deleting both files and database records
- Using Docker Compose for multi-service apps
- Configuring Nginx for proxying and static delivery
- Writing backup / restore automation for PostgreSQL

---

## 🔮 Possible Improvements

- 👤 User authentication
- 🔍 Search and filtering
- 🖼️ Thumbnail generation
- ☁️ Cloud storage integration
- 🧪 Unit and integration tests
- ⚙️ CI/CD pipeline
- 📊 Admin dashboard

---


## 👨‍💻 Author

**Dmytro Kulinich**  
📌 Python Backend / Full-Stack Developer  
🔗 GitHub: [glom4oblom](https://github.com/glom4oblom)

---

## ⭐ Final Note

This project was created as a **portfolio full-stack application** to demonstrate practical skills in:

- backend development
- database design
- file storage logic
- frontend interaction
- Docker-based deployment

If you like this project, feel free to ⭐ the repository.

<p align="center">
  <b>Thanks for visiting this project 💙</b>
</p>
