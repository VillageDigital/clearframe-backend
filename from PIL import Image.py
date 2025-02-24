from PIL import Image

def center_image_on_background(input_path, output_path, bg_size=(1080, 1080), bg_color=(255, 255, 255)):
    # Open the image
    img = Image.open(input_path).convert("RGBA")

    # Resize image while keeping aspect ratio
    img.thumbnail(bg_size, Image.LANCZOS)

    # Create new white background
    background = Image.new("RGBA", bg_size, bg_color)

    # Calculate position to center the image
    x_offset = (bg_size[0] - img.width) // 2
    y_offset = (bg_size[1] - img.height) // 2

    # Paste the image onto the background
    background.paste(img, (x_offset, y_offset), img)

    # Save as PNG (supports transparency)
    background.save(output_path, format="PNG")

    print(f"✅ Processed and saved: {output_path}")

# Example usage
center_image_on_background("C:\\Users\\Merri\\Documents\\Clearframe-backend\\input.jpg", 
                           "C:\\Users\\Merri\\Documents\\Clearframe-backend\\output.png")


