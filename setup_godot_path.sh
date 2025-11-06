#!/bin/bash
# setup_godot_path.sh
# Add Godot to PATH for this session and future sessions

echo "Adding Godot to PATH..."

# Create alias for convenience (handles spaces in path)
if ! grep -q "alias godot=" ~/.bashrc; then
    echo '' >> ~/.bashrc
    echo '# Godot Engine' >> ~/.bashrc
    echo 'alias godot="/c/Program Files/Godot/Godot_v4.5.1-stable_win64.exe"' >> ~/.bashrc
    echo "Added godot alias to ~/.bashrc"
else
    echo "Godot alias already in ~/.bashrc"
fi

# Also create current session alias
alias godot="/c/Program Files/Godot/Godot_v4.5.1-stable_win64.exe"

echo ""
echo "Setup complete! Run: source ~/.bashrc"
echo "Then you can type: godot --editor godot/project.godot"
