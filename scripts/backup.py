import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


BACKUPS_DIR = Path(__file__).resolve().parent.parent / "backups"
BACKUPS_DIR.mkdir(exist_ok=True)


def get_db_config():
    return {
        "host": os.getenv("DB_HOST", "db"),
        "name": os.getenv("DB_NAME", "group6_image_hosting_server_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "port": os.getenv("DB_PORT", "5432"),
    }


def create_backup():
    config = get_db_config()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    backup_file = BACKUPS_DIR / f"backup_{timestamp}.sql"

    env = os.environ.copy()
    env["PGPASSWORD"] = config["password"]

    command = [
        "pg_dump",
        "-h", config["host"],
        "-p", str(config["port"]),
        "-U", config["user"],
        "-d", config["name"],
        "-f", str(backup_file),
    ]

    try:
        subprocess.run(command, check=True, env=env)
        print(f"✅ Backup created: {backup_file.name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create backup: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ pg_dump not found. Make sure postgresql-client is installed.")
        sys.exit(1)


def list_backups():
    backup_files = sorted(BACKUPS_DIR.glob("*.sql"))

    if not backup_files:
        print("No backups found.")
        return

    print("Available backups:")
    for backup_file in backup_files:
        print(f"- {backup_file.name}")


def restore_backup(filename):
    config = get_db_config()
    backup_file = BACKUPS_DIR / filename

    if not backup_file.exists():
        print(f"❌ Backup file not found: {filename}")
        sys.exit(1)

    env = os.environ.copy()
    env["PGPASSWORD"] = config["password"]

    command = [
        "psql",
        "-h", config["host"],
        "-p", str(config["port"]),
        "-U", config["user"],
        "-d", config["name"],
        "-f", str(backup_file),
    ]

    try:
        subprocess.run(command, check=True, env=env)
        print(f"✅ Database restored from: {backup_file.name}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to restore backup: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ psql not found. Make sure postgresql-client is installed.")
        sys.exit(1)


def print_help():
    print("Usage:")
    print("  python backup.py create")
    print("  python backup.py list")
    print("  python backup.py restore <backup_file.sql>")


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "create":
        create_backup()
    elif command == "list":
        list_backups()
    elif command == "restore":
        if len(sys.argv) < 3:
            print("❌ Please provide backup file name.")
            print_help()
            sys.exit(1)
        restore_backup(sys.argv[2])
    else:
        print(f"❌ Unknown command: {command}")
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()