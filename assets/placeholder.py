from PIL import Image, ImageDraw

def create_placeholder_icon(name, size=(100, 100)):
    # Create a new image with a white background
    image = Image.new('RGB', size, 'white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simple icon (just a rectangle for placeholder)
    draw.rectangle([10, 10, size[0]-10, size[1]-10], outline='black')
    
    # Save the image
    image.save(f'{name}.png')

# Create placeholder icons for all needed images
icons = ['dashboard', 'income', 'expense', 'loans', 'reports', 'settings']
for icon in icons:
    create_placeholder_icon(icon)
