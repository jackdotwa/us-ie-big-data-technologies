#!/bin/bash
echo "🚀 Building and running the student's assignment..."

# The --force-recreate flag ensures a clean start every time
# The --build flag ensures the student's latest code is used
docker-compose up --build --force-recreate

echo "✅ Assignment finished. Tearing down the environment..."
docker-compose down

