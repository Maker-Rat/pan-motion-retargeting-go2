#!/usr/bin/env python3
"""
Test script to verify skeleton update on a single BVH file.
This will create a test output file so you can inspect it before batch processing.
"""

import os
import sys
from pathlib import Path
from update_dog_skeleton_to_go2 import parse_hierarchy_offsets, update_bvh_file


def main():
    script_dir = Path(__file__).parent
    go2_file = script_dir / "demo_dir" / "Dog" / "go2.bvh"
    dogset_dir = script_dir / "data_preprocess" / "Lafan1_and_dog" / "DogSet"
    
    # Check if paths exist
    if not go2_file.exists():
        print(f"Error: Go2 skeleton file not found at {go2_file}")
        sys.exit(1)
    
    if not dogset_dir.exists():
        print(f"Error: DogSet directory not found at {dogset_dir}")
        sys.exit(1)
    
    # Find first BVH file to test
    bvh_files = list(dogset_dir.glob("*.bvh"))
    if not bvh_files:
        print(f"No BVH files found in {dogset_dir}")
        sys.exit(1)
    
    test_file = bvh_files[0]
    output_file = script_dir / "test_output_go2_skeleton.bvh"
    
    print(f"Go2 skeleton: {go2_file}")
    print(f"Test input: {test_file}")
    print(f"Test output: {output_file}")
    print()
    
    # Parse Go2 offsets
    go2_offsets = parse_hierarchy_offsets(go2_file)
    
    # Parse original offsets
    original_offsets = parse_hierarchy_offsets(test_file)
    
    print("Offset comparison:")
    print("-" * 80)
    print(f"{'Joint':<20} {'Original Offset':<30} {'Go2 Offset':<30}")
    print("-" * 80)
    
    for joint in sorted(go2_offsets.keys()):
        orig = original_offsets.get(joint, (None, None, None))
        go2 = go2_offsets[joint]
        
        if joint == 'Hips':
            print(f"{joint:<20} {str(orig):<30} {str(go2):<30} [PRESERVED]")
        else:
            print(f"{joint:<20} {str(orig):<30} {str(go2):<30}")
    
    print("-" * 80)
    print()
    
    # Perform update
    print(f"Creating test output file...")
    update_bvh_file(test_file, output_file, go2_offsets, preserve_root_offset=True)
    print(f"✓ Test file created: {output_file}")
    print()
    
    # Verify the output
    print("Verifying output file...")
    output_offsets = parse_hierarchy_offsets(output_file)
    
    errors = []
    # Check that Hips offset is preserved
    if output_offsets['Hips'] == original_offsets['Hips']:
        print("  ✓ ROOT Hips OFFSET preserved")
    else:
        errors.append(f"  ✗ ROOT Hips OFFSET changed! {original_offsets['Hips']} -> {output_offsets['Hips']}")
    
    # Check that other offsets match Go2
    for joint in go2_offsets.keys():
        if joint == 'Hips':
            continue
        if joint in output_offsets:
            if output_offsets[joint] == go2_offsets[joint]:
                print(f"  ✓ {joint} updated correctly")
            else:
                errors.append(f"  ✗ {joint} mismatch: expected {go2_offsets[joint]}, got {output_offsets[joint]}")
        else:
            errors.append(f"  ✗ {joint} not found in output")
    
    print()
    if errors:
        print("ERRORS FOUND:")
        for error in errors:
            print(error)
        sys.exit(1)
    else:
        print("="*80)
        print("✓ ALL CHECKS PASSED!")
        print("="*80)
        print()
        print("Next steps:")
        print(f"1. Inspect the test output file: {output_file}")
        print(f"2. If satisfied, run: python update_dog_skeleton_to_go2.py")
        print()


if __name__ == "__main__":
    main()
