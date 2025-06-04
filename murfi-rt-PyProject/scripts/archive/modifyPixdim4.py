import nibabel as nib
import os

def main():
    input_path = input("Enter the path to the NIfTI file (.nii or .nii.gz): ").strip()

    if not os.path.exists(input_path):
        print("File not found. Please check the path and try again.")
        return

    # Load the image
    img = nib.load(input_path)
    header = img.header

    # Modify pixdim4
    original_pixdim4 = header['pixdim'][4]
    header['pixdim'][4] = 0.0

    # Save new image
    base = os.path.basename(input_path)
    output_path = os.path.join(os.path.dirname(input_path), f"modified_{base}")
    nib.save(img, output_path)

    print(f"Modified NIfTI saved as: {output_path}")
    print(f"Changed pixdim4 from {original_pixdim4} to {header['pixdim'][4]}")

if __name__ == "__main__":
    main()

