#!/usr/bin/env python3
"""
Script to update all DogSet BVH files with Go2 skeleton proportions.
- Preserves ROOT Hips OFFSET (position in space)
- Replaces all other joint offsets with Go2 values
- Keeps all motion data unchanged
"""

import os
import re
import sys
from pathlib import Path


def parse_hierarchy_offsets(bvh_file):
    """
    Parse BVH file and extract offset values for each joint.
    Returns dict: {joint_name: (offset_x, offset_y, offset_z)}
    """
    offsets = {}
    current_joint = None
    
    with open(bvh_file, 'r') as f:
        for line in f:
            # Check for ROOT or JOINT
            root_match = re.match(r'\s*ROOT\s+(\w+)', line)
            joint_match = re.match(r'\s*JOINT\s+(\w+)', line)
            
            if root_match:
                current_joint = root_match.group(1)
            elif joint_match:
                current_joint = joint_match.group(1)
            
            # Check for OFFSET
            offset_match = re.match(r'\s*OFFSET\s+([\-\d\.e]+)\s+([\-\d\.e]+)\s+([\-\d\.e]+)', line)
            if offset_match and current_joint:
                x, y, z = map(float, offset_match.groups())
                offsets[current_joint] = (x, y, z)
                current_joint = None  # Reset after capturing offset
    
    return offsets


def update_bvh_file(input_file, output_file, go2_offsets, preserve_root_offset=True):
    """
    Update a BVH file with Go2 skeleton offsets.
    
    Args:
        input_file: Path to original BVH file
        output_file: Path to save updated BVH file
        go2_offsets: Dict of joint offsets from Go2 skeleton
        preserve_root_offset: If True, keeps original ROOT Hips OFFSET
    """
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    updated_lines = []
    current_joint = None
    in_hierarchy = True
    is_root = False
    
    for i, line in enumerate(lines):
        # Check if we've reached MOTION section
        if 'MOTION' in line:
            in_hierarchy = False
            updated_lines.append(line)
            continue
        
        # If not in hierarchy, just copy the line
        if not in_hierarchy:
            updated_lines.append(line)
            continue
        
        # Check for ROOT or JOINT
        root_match = re.match(r'(\s*)ROOT\s+(\w+)', line)
        joint_match = re.match(r'(\s*)JOINT\s+(\w+)', line)
        
        if root_match:
            current_joint = root_match.group(2)
            is_root = True
            updated_lines.append(line)
            continue
        elif joint_match:
            current_joint = joint_match.group(2)
            is_root = False
            updated_lines.append(line)
            continue
        
        # Check for OFFSET line
        offset_match = re.match(r'(\s*)OFFSET\s+([\-\d\.e]+)\s+([\-\d\.e]+)\s+([\-\d\.e]+)', line)
        if offset_match and current_joint:
            indent = offset_match.group(1)
            
            # If ROOT and we want to preserve it, keep original
            if is_root and preserve_root_offset:
                updated_lines.append(line)
            else:
                # Replace with Go2 offset
                if current_joint in go2_offsets:
                    new_offset = go2_offsets[current_joint]
                    new_line = f"{indent}OFFSET {new_offset[0]} {new_offset[1]} {new_offset[2]}\n"
                    updated_lines.append(new_line)
                else:
                    # If joint not found in Go2 (shouldn't happen), keep original
                    print(f"Warning: Joint '{current_joint}' not found in Go2 skeleton, keeping original offset")
                    updated_lines.append(line)
            
            current_joint = None  # Reset after processing offset
            is_root = False
            continue
        
        # For all other lines, just copy
        updated_lines.append(line)
    
    # Write updated file
    with open(output_file, 'w') as f:
        f.writelines(updated_lines)


def main():
    # Paths
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
    
    # Parse Go2 offsets
    print(f"Reading Go2 skeleton from: {go2_file}")
    go2_offsets = parse_hierarchy_offsets(go2_file)
    
    print(f"\nGo2 skeleton offsets loaded:")
    for joint, offset in go2_offsets.items():
        print(f"  {joint}: {offset}")
    
    # Find all BVH files in DogSet
    bvh_files = list(dogset_dir.glob("*.bvh"))
    
    if not bvh_files:
        print(f"\nNo BVH files found in {dogset_dir}")
        sys.exit(1)
    
    print(f"\nFound {len(bvh_files)} BVH files to process")
    
    # Ask for confirmation
    response = input("\nThis will modify all BVH files in DogSet. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Aborted.")
        sys.exit(0)
    
    # Create backup directory
    backup_dir = dogset_dir / "backup_original_skeleton"
    backup_dir.mkdir(exist_ok=True)
    print(f"\nBackup directory: {backup_dir}")
    
    # Process each file
    success_count = 0
    for bvh_file in bvh_files:
        try:
            # Create backup
            backup_file = backup_dir / bvh_file.name
            if not backup_file.exists():
                import shutil
                shutil.copy2(bvh_file, backup_file)
                print(f"  Backed up: {bvh_file.name}")
            
            # Update file (overwrite original)
            update_bvh_file(bvh_file, bvh_file, go2_offsets, preserve_root_offset=True)
            print(f"  ✓ Updated: {bvh_file.name}")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ Error processing {bvh_file.name}: {e}")
    
    print(f"\n{'='*60}")
    print(f"Processing complete!")
    print(f"Successfully updated: {success_count}/{len(bvh_files)} files")
    print(f"Backups saved to: {backup_dir}")
    print(f"\nNext steps:")
    print(f"1. Update std_bvh/dog_std.bvh with Go2 skeleton")
    print(f"2. Run: python data_preprocess/Lafan1_and_dog/extract.py")
    print(f"3. Retrain the model or test with demos")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
