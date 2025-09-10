# Build frontend and start the server
serve:
    cd frontend && npm run build
    cd backend && uv run python main.py --mode server

# Install dependencies for both frontend and backend
install:
    cd backend && uv sync
    cd frontend && npm install

# Development mode - start frontend dev server
dev-frontend:
    cd frontend && npm start

# Start backend in CLI mode
cli:
    cd backend && uv run python main.py --mode cli

# Clean build artifacts
clean:
    rm -rf frontend/build
    rm -rf backend/.venv

# Build frontend only
build-frontend:
    cd frontend && npm run build

# Start backend server only (assumes frontend is already built)
start-backend:
    cd backend && uv run python main.py --mode server