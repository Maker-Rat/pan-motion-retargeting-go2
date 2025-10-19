# Go2 Skeleton Update Scripts

This directory contains scripts to update all DogSet BVH files with Go2 robot skeleton proportions.

## Overview

The scripts will:
- ✅ Preserve ROOT Hips OFFSET (spatial position of each motion)
- ✅ Replace all other joint offsets with Go2 values from `demo_dir/Dog/go2.bvh`
- ✅ Keep all motion data (rotations, frames) unchanged
- ✅ Create backups of original files

## Files

- **`test_skeleton_update.py`** - Test script to verify on a single file
- **`update_dog_skeleton_to_go2.py`** - Main script to update all DogSet files
- **`SKELETON_UPDATE_README.md`** - This file

## Usage

### Step 1: Test on a Single File

First, verify the script works correctly on one file:

```bash
python test_skeleton_update.py
```

This will:
1. Process the first BVH file in DogSet
2. Create `test_output_go2_skeleton.bvh`
3. Show a comparison of offsets
4. Verify all changes are correct

**Inspect the test output file** before proceeding!

### Step 2: Update All Files

Once satisfied with the test, update all files:

```bash
python update_dog_skeleton_to_go2.py
```

The script will:
1. Show which offsets will be applied
2. Ask for confirmation
3. Create backups in `data_preprocess/Lafan1_and_dog/DogSet/backup_original_skeleton/`
4. Update all BVH files in place

### Step 3: Update Standard Skeleton

Update the standard skeleton template used for output:

```bash
# Backup original
cp data_preprocess/Lafan1_and_dog/std_bvh/dog_std.bvh data_preprocess/Lafan1_and_dog/std_bvh/dog_std_original.bvh

# Copy Go2 hierarchy (you can manually copy just the HIERARCHY section)
cp demo_dir/Dog/go2.bvh data_preprocess/Lafan1_and_dog/std_bvh/dog_std.bvh
```

**Important:** The `dog_std.bvh` needs valid motion data (even if just 1 frame). You may want to copy only the HIERARCHY section and keep the existing MOTION section.

### Step 4: Regenerate Training Data

Re-run the preprocessing to create new training data with Go2 skeleton:

```bash
cd data_preprocess/Lafan1_and_dog
python extract.py
```

This will regenerate:
- `dogtrain.npz`
- `dogtest.npz`
- `dogstats.npz`

With Go2 skeleton offsets embedded.

### Step 5: Retrain (Optional but Recommended)

For best results, retrain the model:

```bash
python train_lafan1dog.py --save_dir ./trained_go2 --batch_size 32
```

Or use the pretrained model to test (quality may vary).

## What Gets Changed

### Preserved
- ✅ ROOT Hips OFFSET (e.g., `-10.0563 7.73376 -472.55`)
- ✅ All motion data (frames, rotations, positions)
- ✅ Joint hierarchy structure
- ✅ Joint names
- ✅ Frame timing

### Updated (to Go2 values)
- Spine OFFSET: `0 0 0` → `0 0 0` (unchanged)
- Spine1 OFFSET: `19 0 0` → `19.34 0 0`
- Neck OFFSET: `22.5 0.6 0` → `19.34 0 0`
- Head OFFSET: `14 0.0308777 0` → `0 0 0`
- LeftShoulder OFFSET: `19.8 3.7 4.3` → `19.34 0 14.2`
- LeftArm OFFSET: `8 0 0` → `0 0 0`
- LeftForeArm OFFSET: `15.2 0 0` → `21.3 0 0`
- LeftHand OFFSET: `17.8 0 0` → `21.3 0 0`
- End Site offsets: various → `0 0 0`
- (Similar updates for right side and legs)
- LeftUpLeg OFFSET: `5.98425 -7.666 4.78879` → `0 0 14.2`
- LeftLeg OFFSET: `16 0 0` → `21.3 0 0`
- LeftFoot OFFSET: `18 0 0` → `21.3 0 0`
- Tail and Tail1 offsets updated

## Verification

After running the scripts, verify:

1. **Check a file manually:**
   ```bash
   head -50 data_preprocess/Lafan1_and_dog/DogSet/D1_001_KAN01_001.bvh
   ```
   Confirm offsets match Go2 values

2. **Check backup exists:**
   ```bash
   ls data_preprocess/Lafan1_and_dog/DogSet/backup_original_skeleton/
   ```

3. **Compare motion data:**
   ```bash
   # Motion data should be identical
   diff <(tail -n +100 backup_original_skeleton/D1_001_KAN01_001.bvh) \
        <(tail -n +100 D1_001_KAN01_001.bvh)
   ```
   Should show no differences in motion frames.

## Rollback

If you need to restore original files:

```bash
cp data_preprocess/Lafan1_and_dog/DogSet/backup_original_skeleton/*.bvh \
   data_preprocess/Lafan1_and_dog/DogSet/
```

## Technical Details

### Why Preserve ROOT Hips OFFSET?

The ROOT Hips OFFSET contains the **spatial position** of the character in 3D space for that particular motion capture session. This varies per file and is not part of the skeleton structure - it's where the motion starts in the capture volume.

Example:
- File 1: `OFFSET -10.0563 7.73376 -472.55`
- File 2: `OFFSET 5.2 8.1 -380.3`

These are different starting positions, not skeleton proportions.

### Joint Offsets vs Motion Data

- **Joint OFFSET**: Static bone lengths (e.g., femur = 21.3cm)
- **Motion Data**: Dynamic rotations and root positions per frame

The scripts modify only the static bone lengths while preserving all motion.

## Troubleshooting

**Problem:** Script can't find go2.bvh
**Solution:** Ensure `demo_dir/Dog/go2.bvh` exists

**Problem:** No files found in DogSet
**Solution:** Download dog motion data from AI4Animation project first

**Problem:** Test output looks wrong
**Solution:** Check that go2.bvh has the same joint names and hierarchy as original dog files

**Problem:** After update, motions look distorted
**Solution:** 
1. Check that you updated dog_std.bvh
2. Regenerate training data with extract.py
3. Consider retraining the model

## Questions?

The scripts are designed to be safe:
- Creates backups automatically
- Test on single file first
- Shows what will change before proceeding
- Preserves all motion data

Review `test_output_go2_skeleton.bvh` carefully before batch processing!
