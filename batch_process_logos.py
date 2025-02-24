import os
from PIL import Image

def center_images_in_folder(input_folder, output_folder, bg_size=(1080, 1080), bg_color=(255, 255, 255)):
    """Processes all images in a folder, centering them on a white background."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('png', 'jpg', 'jpeg', 'webp')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".png")
            
            try:
                img = Image.open(input_path).convert("RGBA")
                img.thumbnail(bg_size, Image.LANCZOS)
                
                background = Image.new("RGBA", bg_size, bg_color)
                x_offset = (bg_size[0] - img.width) // 2
                y_offset = (bg_size[1] - img.height) // 2
                
                background.paste(img, (x_offset, y_offset), img)
                background.save(output_path, format="PNG")
                
                print(f"✅ Processed: {filename} → {output_path}")
            except Exception as e:
                print(f"❌ Failed to process {filename}: {e}")

# Run the batch processing
input_folder = "logos"  # Folder where unprocessed logos are stored
output_folder = "processed_logos"  # Folder where processed logos will be saved
center_images_in_folder(input_folder, output_folder)
