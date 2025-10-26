#!/usr/bin/env python3
"""
Script to scale all numerical values in a BVH file by a specific factor.

This script scales:
- OFFSET values in the HIERARCHY section
- Position values in the MOTION section (Xposition, Yposition, Zposition)
- Rotation values are NOT scaled (they remain unchanged)
- Frame Time (optional - disabled by default)

Usage:
    python scale_bvh.py input.bvh output.bvh --scale 2.0
    python scale_bvh.py input.bvh output.bvh --scale 0.5 --scale-time
"""

import argparse
import re
import sys
from pathlib import Path


def scale_bvh_file(input_path, output_path, scale_factor, scale_time=False):
    """
    Scale positional values in a BVH file (not rotations).
    
    Args:
        input_path: Path to input BVH file
        output_path: Path to output BVH file
        scale_factor: Factor to scale positional values by
        scale_time: Whether to scale the Frame Time value (default: False)
    """
    try:
        with open(input_path, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file '{input_path}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    output_lines = []
    in_motion_section = False
    motion_data_started = False
    
    # Parse channel information to know which values are positions
    channel_info = []
    
    for line in lines:
        stripped = line.strip()
        
        # Parse CHANNELS to identify position vs rotation channels
        if not in_motion_section and "CHANNELS" in stripped:
            match = re.match(r'.*CHANNELS\s+\d+\s+(.*)', stripped)
            if match:
                channels = match.group(1).split()
                for ch in channels:
                    # Position channels should be scaled, rotation channels should not
                    is_position = 'position' in ch.lower()
                    channel_info.append(is_position)
        
        # Check if we've entered the MOTION section
        if stripped == "MOTION":
            in_motion_section = True
            output_lines.append(line)
            continue
        
        # Handle MOTION section metadata
        if in_motion_section and not motion_data_started:
            if stripped.startswith("Frames:"):
                # Don't scale frame count
                output_lines.append(line)
                continue
            elif stripped.startswith("Frame Time:"):
                if scale_time:
                    # Scale the frame time
                    match = re.match(r'(Frame Time:\s*)([0-9.eE+-]+)', stripped)
                    if match:
                        prefix = match.group(1)
                        value = float(match.group(2))
                        scaled_value = value * scale_factor
                        indent = line[:len(line) - len(line.lstrip())]
                        output_lines.append(f"{indent}{prefix}{scaled_value:.6f}\n")
                    else:
                        output_lines.append(line)
                else:
                    output_lines.append(line)
                motion_data_started = True
                continue
        
        # Handle HIERARCHY section - scale OFFSET values
        if not in_motion_section and "OFFSET" in stripped:
            match = re.match(r'(\s*OFFSET\s+)([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)', line)
            if match:
                prefix = match.group(1)
                x = float(match.group(2)) * scale_factor
                y = float(match.group(3)) * scale_factor
                z = float(match.group(4)) * scale_factor
                indent = line[:len(line) - len(line.lstrip())]
                output_lines.append(f"{indent}OFFSET {x:.6f} {y:.6f} {z:.6f}\n")
                continue
        
        # Handle MOTION section - scale only positional values in motion data
        if motion_data_started:
            # This line contains motion data
            values = stripped.split()
            if values and all_are_numbers(values):
                scaled_values = []
                for i, v in enumerate(values):
                    float_val = float(v)
                    # Scale only if this channel is a position channel
                    if i < len(channel_info) and channel_info[i]:
                        scaled_values.append(float_val * scale_factor)
                    else:
                        scaled_values.append(float_val)
                
                # Format with consistent spacing
                formatted_values = ' '.join(f'{v:.6f}' for v in scaled_values)
                output_lines.append(formatted_values + '\n')
                continue
        
        # For all other lines, keep them as-is
        output_lines.append(line)
    
    # Write output file
    try:
        with open(output_path, 'w') as f:
            f.writelines(output_lines)
        print(f"Successfully scaled BVH file by factor {scale_factor}")
        print(f"Input:  {input_path}")
        print(f"Output: {output_path}")
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


def all_are_numbers(values):
    """Check if all values in a list can be converted to float."""
    try:
        for v in values:
            float(v)
        return True
    except ValueError:
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Scale all numerical values in a BVH file by a specific factor.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scale all positional values by 2.0
  python scale_bvh.py input.bvh output.bvh --scale 2.0
  
  # Scale by 0.5 (reduce by half)
  python scale_bvh.py input.bvh output.bvh --scale 0.5
  
  # Scale by 10 and also scale Frame Time
  python scale_bvh.py input.bvh output.bvh --scale 10 --scale-time
        """
    )
    
    parser.add_argument('input', type=str, help='Input BVH file path')
    parser.add_argument('output', type=str, help='Output BVH file path')
    parser.add_argument('--scale', '-s', type=float, required=True,
                        help='Scale factor (e.g., 2.0 to double, 0.5 to halve)')
    parser.add_argument('--scale-time', action='store_true',
                        help='Also scale the Frame Time value (default: False)')
    
    args = parser.parse_args()
    
    # Validate scale factor
    if args.scale <= 0:
        print("Error: Scale factor must be positive.", file=sys.stderr)
        sys.exit(1)
    
    # Check if input file exists
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    # Warn if output file already exists
    if Path(args.output).exists():
        response = input(f"Warning: Output file '{args.output}' already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Scale the BVH file
    scale_bvh_file(
        args.input, 
        args.output, 
        args.scale,
        scale_time=args.scale_time
    )


if __name__ == '__main__':
    main()
