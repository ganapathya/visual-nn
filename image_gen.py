from PIL import Image, ImageDraw
import base64
import io

def create_tiny_test_image(size=16):
    """Create a tiny test image for t3.micro testing"""
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple pattern
    margin = size // 4
    draw.rectangle([margin, margin, size-margin, size-margin], fill='black')
    draw.line([0, 0, size-1, size-1], fill='red', width=1)
    draw.line([0, size-1, size-1, 0], fill='blue', width=1)
    
    # Save as PNG
    filename = f'tiny_test_{size}x{size}.png'
    img.save(filename)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    print(f'Created {filename}')
    print(f'Base64 length: {len(img_base64)}')
    print(f'Image size: {size}x{size} pixels')
    
    return filename, img_base64

# Create different sizes
for size in [16, 32, 64]:
    create_tiny_test_image(size)

print('\nUse these tiny images for testing on t3.micro!')