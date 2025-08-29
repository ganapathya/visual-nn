#!/usr/bin/env python3
"""
Demo script showcasing Visual Neural Network API usage.
This script demonstrates how to programmatically interact with the CNN visualization tool.
"""

import requests
import base64
import json
from PIL import Image, ImageDraw
import io

# API endpoint
API_BASE = "http://localhost:5001"

def create_demo_image():
    """Create a simple demo image for testing."""
    # Create a 128x128 image with some patterns
    img = Image.new('RGB', (128, 128), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw some shapes for interesting convolution results
    draw.rectangle([20, 20, 60, 60], fill='black')  # Square
    draw.ellipse([70, 20, 110, 60], fill='gray')    # Circle
    draw.line([20, 80, 110, 110], fill='black', width=3)  # Diagonal line
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    img_base64 = base64.b64encode(img_data).decode('utf-8')
    
    return img_base64

def test_health_check():
    """Test the health check endpoint."""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.text}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on port 5001")
        return False

def test_layer_processing():
    """Test the layer processing endpoint with a demo architecture."""
    print("🧠 Testing CNN layer processing...")
    
    # Create demo image
    img_base64 = create_demo_image()
    print("📸 Created demo image (128x128 with geometric shapes)")
    
    # Define a sample CNN architecture
    layers = [
        {
            "type": "conv",
            "kernel_type": "sobel_x",
            "stride": 1,
            "padding": 1,
            "out_channels": 3
        },
        {
            "type": "relu"
        },
        {
            "type": "maxpool",
            "kernel_size": 2,
            "stride": 2,
            "padding": 0,
            "out_channels": 3
        },
        {
            "type": "conv",
            "kernel_type": "sharpen",
            "stride": 1,
            "padding": 1,
            "out_channels": 3
        }
    ]
    
    # Prepare request data
    data = {
        "image_base64": img_base64,
        "layers": layers
    }
    
    print(f"🏗️  Testing architecture with {len(layers)} layers:")
    for i, layer in enumerate(layers):
        layer_info = f"Layer {i+1}: {layer['type']}"
        if layer['type'] == 'conv':
            layer_info += f" ({layer['kernel_type']} kernel)"
        elif layer['type'] == 'maxpool':
            layer_info += f" ({layer['kernel_size']}x{layer['kernel_size']})"
        print(f"   {layer_info}")
    
    try:
        # Send request
        response = requests.post(
            f"{API_BASE}/process-layers",
            json=data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Layer processing successful!")
                
                # Display results
                results = result.get('results', [])
                print(f"📊 Processed {len(results)} layers:")
                
                for i, layer_result in enumerate(results):
                    shape = layer_result.get('output_shape', [])
                    rf = layer_result.get('receptive_field', 0)
                    jump = layer_result.get('jump', 0)
                    layer_type = layer_result.get('layer_type', 'unknown')
                    
                    print(f"   Layer {i+1} ({layer_type}):")
                    print(f"     Shape: {shape}")
                    print(f"     Receptive Field: {rf}px")
                    print(f"     Jump: {jump}px")
                    print(f"     Image Data: {len(layer_result.get('base64_image', ''))} chars")
                
                return True
            else:
                print(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False

def test_different_kernels():
    """Test different kernel types."""
    print("🔧 Testing different kernel types...")
    
    img_base64 = create_demo_image()
    kernel_types = ['sharpen', 'blur', 'gaussian', 'sobel_x', 'sobel_y', 'laplacian', 'emboss']
    
    for kernel_type in kernel_types:
        print(f"🔍 Testing {kernel_type} kernel...")
        
        data = {
            "image_base64": img_base64,
            "layers": [{
                "type": "conv",
                "kernel_type": kernel_type,
                "stride": 1,
                "padding": 1,
                "out_channels": 3
            }]
        }
        
        try:
            response = requests.post(f"{API_BASE}/process-layers", json=data)
            if response.status_code == 200 and response.json().get('success'):
                result_shape = response.json()['results'][0]['output_shape']
                print(f"   ✅ {kernel_type}: Output shape {result_shape}")
            else:
                print(f"   ❌ {kernel_type}: Failed")
        except Exception as e:
            print(f"   ❌ {kernel_type}: Error - {e}")

def main():
    """Run all demo tests."""
    print("🧠 Visual Neural Network API Demo")
    print("=" * 50)
    print("This script tests the CNN visualization API with sample data.")
    print()
    
    # Test health check
    if not test_health_check():
        print("❌ Server is not responding. Please start the server first:")
        print("   python app.py")
        return
    
    print()
    
    # Test layer processing
    if test_layer_processing():
        print()
        
        # Test different kernels
        test_different_kernels()
        
        print()
        print("🎉 All tests completed successfully!")
        print()
        print("💡 Next steps:")
        print("   1. Open index.html in your browser")
        print("   2. Upload an image and experiment with layers")
        print("   3. Try different visualization modes")
        print("   4. Explore the educational features")
    else:
        print("❌ Layer processing test failed")

if __name__ == "__main__":
    main()
