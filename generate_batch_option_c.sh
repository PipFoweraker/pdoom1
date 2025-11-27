# !/bin/bash
# Option C: Generate variants for critical UI elements, singles for the rest
# Total estimated cost: ~$9-10

set -e  # Exit on error

echo "=========================================="
echo "OPTION C: Strategic Variant Generation"
echo "=========================================="
echo ""

# Set API key
export OPENAI_API_KEY="$(cat /c/Users/Pip/Documents/openai_api_key.txt)"

echo "Step 1/4: Main navigation icons (3 variants each)"
echo "Cost: 10 assets x 3 variants x \$0.08 = \$2.40"
echo ""
python tools/generate_images.py --file art_prompts/ui_icons.yaml --category main_navigation --variants 3 --yes --update-yaml

echo ""
echo "=========================================="
echo "Step 2/4: Normal button states (2 variants each)"
echo "Cost: 6 assets x 2 variants x \$0.08 = \$0.96"
echo ""
python tools/generate_images.py --file art_prompts/ui_icons.yaml --category buttons_normal --variants 2 --yes --update-yaml

echo ""
echo "=========================================="
echo "Step 3/4: Resource icons (2 variants each)"
echo "Cost: 10 assets x 2 variants x \$0.08 = \$1.60"
echo ""
python tools/generate_images.py --file art_prompts/ui_icons.yaml --category resources --variants 2 --yes --update-yaml

echo ""
echo "=========================================="
echo "Step 4/4: Everything else (single variant)"
echo "Cost: ~55 assets x 1 variant x \$0.08 = ~\$4.40"
echo ""
python tools/generate_images.py --file art_prompts/ui_icons.yaml --status pending --yes --update-yaml

echo ""
echo "=========================================="
echo "SUCCESS BATCH COMPLETE!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review generated images in art_generated/ui_icons/v1/"
echo "2. Pick your favorite variants"
echo "3. Promote approved assets to game:"
echo "   python tools/promote_assets.py --file art_prompts/ui_icons.yaml --status generated --dry-run"
echo ""
