#!/usr/bin/env bash
set -e

cd ./silan-personal-website
# Install Python package (fallback to non-editable if needed)
python3 -m pip install -e . || python3 -m pip install . || true

cd ../api-test-portfolio
# Ensure backend working dir and permissions
mkdir -p .silan
# Ensure backend binary path is a file, not a directory
if [ -d .silan/backend ]; then rm -rf .silan/backend; fi
# If a binary already exists, ensure it is executable
if [ -f .silan/backend ]; then chmod 755 .silan/backend; fi
chmod -R u+rwX .silan

# Ensure backend binary is installed (non-interactive via repo CLI)
printf "y\n" | python3 ../silan-personal-website/silan/silan.py backend install || true

# Stop any existing backend; ignore failure (use repo CLI)
python3 ../silan-personal-website/silan/silan.py backend stop || true
# Also kill by PID file if present
if [ -f .silan/backend.pid ]; then
  PID=$(cat .silan/backend.pid || true)
  if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
    kill -9 "$PID" || true
  fi
fi

# Free port 8888 if occupied
if lsof -ti:8888 >/dev/null 2>&1; then
  kill -9 $(lsof -ti:8888) || true
fi

# Wait until port 8888 is fully released (max ~5s)
for i in {1..10}; do
  if ! lsof -ti:8888 >/dev/null 2>&1; then break; fi
  sleep 0.5
done

# Start backend as daemon via repo CLI and wait until it binds
python3 ../silan-personal-website/silan/silan.py backend start --daemon || true
for i in {1..30}; do
  if lsof -ti:8888 >/dev/null 2>&1; then break; fi
  sleep 0.5
done

cd ../frontend
# Ensure frontend deps then start dev server
npm install
npm run dev