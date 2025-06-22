#!/bin/zsh
# cleanup.zsh - Script to remove unneeded files from the Wordle Solver project
# Created for macOS 15.x

echo "🧹 Starting cleanup of Wordle Solver project..."

# Set the project root directory
PROJECT_ROOT="$(pwd)"
cd "$PROJECT_ROOT"

# Create backup directory
BACKUP_DIR="$PROJECT_ROOT/backup_$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup directory: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Backup original files before removing them
echo "💾 Backing up original files..."
mkdir -p "$BACKUP_DIR/src"

# Backup the original implementation files that will be replaced by the modular structure
cp -v "$PROJECT_ROOT/src/wordlist.py" "$BACKUP_DIR/src/" 2>/dev/null || true
cp -v "$PROJECT_ROOT/src/wordle_solver.py" "$BACKUP_DIR/src/" 2>/dev/null || true
cp -v "$PROJECT_ROOT/src/game_engine.py" "$BACKUP_DIR/src/" 2>/dev/null || true
cp -v "$PROJECT_ROOT/src/user_interface.py" "$BACKUP_DIR/src/" 2>/dev/null || true
cp -v "$PROJECT_ROOT/src/hint_system.py" "$BACKUP_DIR/src/" 2>/dev/null || true

# Remove outdated/redundant files now that we have a modular structure
echo "\n🗑️  Removing outdated files..."

# Files replaced by modular implementations
if [ -f "$PROJECT_ROOT/src/wordlist.py" ]; then
    echo "Removing src/wordlist.py (replaced by modules/backend/word_manager.py)"
    rm -v "$PROJECT_ROOT/src/wordlist.py"
fi

if [ -f "$PROJECT_ROOT/src/wordle_solver.py" ]; then
    echo "Removing src/wordle_solver.py (replaced by modules/backend/solver.py)"
    rm -v "$PROJECT_ROOT/src/wordle_solver.py"
fi

if [ -f "$PROJECT_ROOT/src/game_engine.py" ]; then
    echo "Removing src/game_engine.py (replaced by modules/backend/game_engine.py)"
    rm -v "$PROJECT_ROOT/src/game_engine.py"
fi

if [ -f "$PROJECT_ROOT/src/user_interface.py" ]; then
    echo "Removing src/user_interface.py (replaced by modules/frontend/cli_interface.py)"
    rm -v "$PROJECT_ROOT/src/user_interface.py"
fi

if [ -f "$PROJECT_ROOT/src/hint_system.py" ]; then
    echo "Removing src/hint_system.py (functionality moved to modules/backend/game_engine.py)"
    rm -v "$PROJECT_ROOT/src/hint_system.py"
fi

# Remove macOS specific metadata files
echo "\n🧹 Removing macOS metadata files..."
find "$PROJECT_ROOT" -name ".DS_Store" -delete -print
find "$PROJECT_ROOT" -name "._*" -delete -print

# Remove Python cache files
echo "\n🧹 Removing Python cache files..."
find "$PROJECT_ROOT" -name "__pycache__" -type d -exec rm -rf {} +  2>/dev/null || true
find "$PROJECT_ROOT" -name "*.pyc" -delete -print
find "$PROJECT_ROOT" -name "*.pyo" -delete -print

# Remove Jupyter notebook checkpoints
echo "\n🧹 Removing Jupyter notebook checkpoints..."
find "$PROJECT_ROOT" -name ".ipynb_checkpoints" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove empty Jupyter notebooks
if [ -f "$PROJECT_ROOT/wordle_solver.ipynb" ]; then
    # Check if the notebook is empty or near-empty
    if [ $(grep -c "cell" "$PROJECT_ROOT/wordle_solver.ipynb") -lt 3 ]; then
        echo "Removing empty notebook: wordle_solver.ipynb"
        rm -v "$PROJECT_ROOT/wordle_solver.ipynb"
    fi
fi

echo "\n✅ Cleanup completed!"
echo "Original files are backed up in: $BACKUP_DIR"
echo "\nThe project now has a clean modular structure with:"
echo "- Backend modules (word_manager, solver, game_engine, stats_manager)"
echo "- Frontend modules (cli_interface)"
echo "- Tests (test_word_manager, test_solver, simple_test)"
