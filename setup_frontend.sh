#!/bin/bash

# Frontend Setup Script for Proposal Master
# This script ensures all frontend dependencies are properly installed

echo "🔧 Setting up Proposal Master Frontend"
echo "======================================"

cd "$(dirname "$0")/Frontend"

echo "📦 Installing dependencies..."
npm install

echo "🔍 Checking for missing TypeScript types..."

# Install missing TypeScript types if needed
npm install --save-dev @types/node @types/react @types/react-dom

echo "🔄 Updating TypeScript configuration..."

# Create or update tsconfig.json if needed
if [ ! -f "tsconfig.json" ]; then
    echo "📝 Creating TypeScript configuration..."
    cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
EOF
fi

echo "🌍 Creating environment file..."

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=Proposal Master
VITE_UPLOAD_MAX_SIZE=52428800
EOF
    echo "   ✅ Created .env file"
else
    echo "   ✅ .env file already exists"
fi

echo "🧹 Cleaning up any build artifacts..."
rm -rf dist node_modules/.vite

echo ""
echo "✅ Frontend setup complete!"
echo "   Run 'npm run dev' to start the development server"
echo "   Or use '../start_dev.sh' to start both frontend and backend"
