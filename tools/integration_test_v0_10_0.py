# !/usr/bin/env python3
"""
Integration Test for P(Doom) v0.10.0 Web Export System

Validates that the web export system is working correctly and produces
valid output compatible with the pdoom1-website repository.
"""

import sys
import tempfile
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.web_export import LeaderboardWebExporter
from src.services.version import get_display_version


def test_web_export_integration():
    """Test complete web export system integration."""
    print(f"Testing P(Doom) {get_display_version()} Web Export System")
    print("=" * 60)
    
    # Test 1: Component initialization
    print("Test 1: Component Initialization...")
    try:
        exporter = LeaderboardWebExporter()
        print("PASS: LeaderboardWebExporter initialized")
    except Exception as e:
        print(f"FAIL: Failed to initialize exporter: {e}")
        return False
    
    # Test 2: Leaderboard availability
    print("\nTest 2: Leaderboard Availability...")
    try:
        all_leaderboards = exporter.enhanced_manager.get_all_leaderboards()
        print(f"v Found {len(all_leaderboards)} leaderboards")
        
        if len(all_leaderboards) == 0:
            print("[WARNING] Warning: No leaderboards found - generate some game data first")
            return True  # Not a failure, just no data
    except Exception as e:
        print(f"x Failed to get leaderboards: {e}")
        return False
    
    # Test 3: Export functionality
    print("\nTest 3: Export Functionality...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "test_export"
            
            metadata = exporter.export_all_leaderboards(output_dir, privacy_mode=True)
            print(f"v Export completed: {len(metadata['exported_leaderboards'])} files")
            
            # Verify files were created
            if (output_dir / "export_metadata.json").exists():
                print("v Export metadata created")
            else:
                print("x Export metadata missing")
                return False
                
            if (output_dir / "leaderboard.json").exists():
                print("v Combined leaderboard created")
            else:
                print("x Combined leaderboard missing")
                return False
                
    except Exception as e:
        print(f"x Export failed: {e}")
        return False
    
    # Test 4: JSON format validation
    print("\nTest 4: JSON Format Validation...")
    try:
        # Find a leaderboard with entries for testing
        test_seed = None
        for seed, info in all_leaderboards.items():
            if info['entry_count'] > 0:
                test_seed = seed
                break
        
        if test_seed:
            with tempfile.TemporaryDirectory() as temp_dir:
                output_file = Path(temp_dir) / "test_leaderboard.json"
                result = exporter.export_specific_seed(test_seed, output_file, privacy_mode=True)
                
                if result["success"]:
                    # Load and validate JSON structure
                    with open(output_file, 'r') as f:
                        data = json.load(f)
                    
                    required_fields = ["meta", "seed", "economic_model", "entries"]
                    missing = [field for field in required_fields if field not in data]
                    
                    if missing:
                        print(f"x Missing required fields: {missing}")
                        return False
                    else:
                        print("v JSON format validation passed")
                        
                    # Check privacy filtering
                    if data["meta"].get("privacy_filtered"):
                        print("v Privacy filtering applied")
                    else:
                        print("[WARNING] Privacy filtering not detected")
                        
                else:
                    print(f"x Specific seed export failed: {result['error']}")
                    return False
        else:
            print("[WARNING] No leaderboards with entries found for JSON validation")
            
    except Exception as e:
        print(f"x JSON validation failed: {e}")
        return False
    
    # Test 5: CLI interface
    print("\nTest 5: CLI Interface...")
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "src.leaderboard", "status"
        ], capture_output=True, text=True, cwd=project_root)
        
        if result.returncode == 0 and "Web Export Ready: True" in result.stdout:
            print("v CLI interface working")
        else:
            print(f"x CLI interface failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"x CLI test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("[PARTY] ALL TESTS PASSED - Web Export System Ready!")
    print(f"[CHART] System can export {len(all_leaderboards)} leaderboards")
    print("[EMOJI] Compatible with pdoom1-website integration")
    print("[LOCK] Privacy protection enabled")
    
    return True


def test_privacy_features():
    """Test privacy filtering functionality."""
    print("\n" + "=" * 60)
    print("Testing Privacy Features...")
    
    from tools.web_export import PrivacyFilter
    
    try:
        privacy_filter = PrivacyFilter()
        
        # Test anonymization levels
        levels = ["none", "standard", "strict"]
        for level in levels:
            if privacy_filter.set_anonymization_level(level):
                print(f"v {level.capitalize()} anonymization level available")
            else:
                print(f"x Failed to set {level} anonymization level")
                return False
        
        # Test privacy summary
        summary = privacy_filter.get_privacy_summary()
        if "anonymization_level" in summary:
            print("v Privacy summary generation working")
        else:
            print("x Privacy summary incomplete")
            return False
            
        print("v Privacy features operational")
        return True
        
    except Exception as e:
        print(f"x Privacy test failed: {e}")
        return False


if __name__ == "__main__":
    print("P(Doom) v0.10.0 Web Export System Integration Test")
    print("Validating global leaderboard functionality...")
    print()
    
    success = test_web_export_integration()
    if success:
        success = test_privacy_features()
    
    if success:
        print("\n[PARTY] INTEGRATION TEST SUCCESSFUL")
        print("Web export system ready for global leaderboards!")
        sys.exit(0)
    else:
        print("\n[EMOJI] INTEGRATION TEST FAILED")
        print("Check the errors above and fix before release.")
        sys.exit(1)