#!/usr/bin/env python3
"""
Quick visual comparison between original and Go2-updated BVH file.
Shows the hierarchy section side-by-side.
"""

import sys
from pathlib import Path


def extract_hierarchy(bvh_file):
    """Extract just the HIERARCHY section from a BVH file."""
    hierarchy_lines = []
    in_hierarchy = False
    
    with open(bvh_file, 'r') as f:
        for line in f:
            if 'HIERARCHY' in line or in_hierarchy:
                in_hierarchy = True
                hierarchy_lines.append(line.rstrip())
                
            if 'MOTION' in line:
                break
    
    return hierarchy_lines


def main():
    script_dir = Path(__file__).parent
    
    # Files to compare
    test_output = script_dir / "test_output_go2_skeleton.bvh"
    dogset_dir = script_dir / "data_preprocess" / "Lafan1_and_dog" / "DogSet"
    
    if not test_output.exists():
        print("Error: test_output_go2_skeleton.bvh not found.")
        print("Run: python test_skeleton_update.py first")
        sys.exit(1)
    
    # Get first BVH file as original
    bvh_files = list(dogset_dir.glob("*.bvh"))
    if not bvh_files:
        print("Error: No BVH files found in DogSet")
        sys.exit(1)
    
    original = bvh_files[0]
    
    print("Comparing HIERARCHY sections:")
    print(f"  Original: {original.name}")
    print(f"  Updated:  test_output_go2_skeleton.bvh")
    print()
    print("="*100)
    
    original_hier = extract_hierarchy(original)
    updated_hier = extract_hierarchy(test_output)
    
    # Find lines with differences
    differences = []
    for i, (orig_line, upd_line) in enumerate(zip(original_hier, updated_hier)):
        if orig_line != upd_line:
            differences.append(i)
    
    print(f"\nFound {len(differences)} lines with differences (offsets updated to Go2 values)")
    print("\nShowing differences:")
    print("-"*100)
    
    for i in differences:
        print(f"\n[Line {i}]")
        print(f"  ORIGINAL: {original_hier[i]}")
        print(f"  GO2:      {updated_hier[i]}")
    
    print("\n" + "="*100)
    print("\nFull HIERARCHY section of updated file:")
    print("-"*100)
    for line in updated_hier:
        print(line)
    

if __name__ == "__main__":
    main()
