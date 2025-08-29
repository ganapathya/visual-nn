from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn.functional as F
import base64
import io
from PIL import Image
import numpy as np
import os
from config import config

# Initialize Flask app with configuration
app = Flask(__name__)
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Enable CORS for all routes
CORS(app, origins=app.config['CORS_ORIGINS'])

def base64_to_tensor(base64_string):
    """
    Takes a Base64-encoded image string, decodes it, and converts it into a PyTorch tensor.
    
    Args:
        base64_string (str): Base64-encoded image string
        
    Returns:
        torch.Tensor: PyTorch tensor with shape [1, 3, H, W]
    """
    # Decode base64 string
    image_data = base64.b64decode(base64_string)
    
    # Convert to PIL Image
    image = Image.open(io.BytesIO(image_data))
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to numpy array and normalize to [0, 1]
    image_array = np.array(image).astype(np.float32) / 255.0
    
    # Convert to PyTorch tensor and add batch and channel dimensions
    tensor = torch.from_numpy(image_array).permute(2, 0, 1).unsqueeze(0)
    
    return tensor

def tensor_to_base64(tensor):
    """
    Takes a PyTorch tensor, converts it back to a PIL image, and returns its Base64-encoded string.
    
    Args:
        tensor (torch.Tensor): PyTorch tensor with shape [1, 3, H, W] or [3, H, W]
        
    Returns:
        str: Base64-encoded image string
    """
    # Remove batch dimension if present
    if tensor.dim() == 4:
        tensor = tensor.squeeze(0)
    
    # Convert to numpy array and denormalize to [0, 255]
    image_array = (tensor.permute(1, 2, 0).numpy() * 255.0).astype(np.uint8)
    
    # Convert to PIL Image
    image = Image.fromarray(image_array)
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_data = buffer.getvalue()
    
    return base64.b64encode(image_data).decode('utf-8')

def get_kernel(kernel_type, kernel_size=3):
    """
    Returns a PyTorch tensor representing a kernel based on the kernel type and size.
    
    Args:
        kernel_type (str): Type of kernel to generate
        kernel_size (int): Size of the kernel (default: 3)
        
    Returns:
        torch.Tensor: kernel tensor
    """
    if kernel_type == 'sharpen' or kernel_type == 'default':
        kernel = torch.tensor([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=torch.float32)
    
    elif kernel_type == 'blur':
        kernel = torch.tensor([
            [1/9, 1/9, 1/9],
            [1/9, 1/9, 1/9],
            [1/9, 1/9, 1/9]
        ], dtype=torch.float32)
    
    elif kernel_type == 'sobel_x':
        kernel = torch.tensor([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ], dtype=torch.float32)
    
    elif kernel_type == 'sobel_y':
        kernel = torch.tensor([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]
        ], dtype=torch.float32)
    
    elif kernel_type == 'gaussian':
        # Gaussian blur kernel
        kernel = torch.tensor([
            [1/16, 2/16, 1/16],
            [2/16, 4/16, 2/16],
            [1/16, 2/16, 1/16]
        ], dtype=torch.float32)
    
    elif kernel_type == 'laplacian':
        # Laplacian edge detection
        kernel = torch.tensor([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ], dtype=torch.float32)
    
    elif kernel_type == 'emboss':
        # Emboss effect
        kernel = torch.tensor([
            [-2, -1, 0],
            [-1, 1, 1],
            [0, 1, 2]
        ], dtype=torch.float32)
    
    elif kernel_type == 'edge_enhance':
        # Edge enhancement
        kernel = torch.tensor([
            [0, 0, 0],
            [-1, 1, 0],
            [0, 0, 0]
        ], dtype=torch.float32)
    
    elif kernel_type == 'identity':
        # Identity kernel (no change)
        kernel = torch.tensor([
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ], dtype=torch.float32)
    
    else:
        # Default to sharpen kernel for unknown types
        kernel = torch.tensor([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=torch.float32)
    
    return kernel

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint to confirm the server is running."""
    return "Server is running."

@app.route('/process-layers', methods=['POST'])
def process_layers():
    """
    POST endpoint for processing image layers.
    Expects JSON with 'image_base64' (string) and 'layers' (array).
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        image_base64 = data.get('image_base64')
        layers = data.get('layers', [])
        
        if not image_base64:
            return jsonify({'error': 'No image_base64 data provided'}), 400
        
        if not layers:
            return jsonify({'error': 'No layers array provided'}), 400
        
        # Decode the input image using base64_to_tensor()
        current_tensor = base64_to_tensor(image_base64)
        
        # Initialize empty list to store output for each layer
        results = []
        
        # Initialize receptive_field and jump to 1
        receptive_field = 1
        jump = 1
        
        # Iterate through the layers array
        for layer_idx, layer in enumerate(layers):
            layer_type = layer.get('type')
            
            if layer_type == 'conv':
                # Get convolution parameters
                kernel_type = layer.get('kernel_type', 'default')
                stride = layer.get('stride', 1)
                padding = layer.get('padding', 1)
                
                # Get the kernel tensor
                kernel = get_kernel(kernel_type)
                kernel_size = kernel.shape[0]  # Should be 3 for 3x3 kernels
                
                # Reshape kernel for 2D convolution: [out_channels, in_channels, height, width]
                kernel_2d = kernel.unsqueeze(0).unsqueeze(0)  # [1, 1, 3, 3]
                
                # Apply convolution to each channel separately
                processed_channels = []
                for i in range(current_tensor.shape[1]):  # Number of channels
                    channel = current_tensor[:, i:i+1, :, :]  # [1, 1, H, W]
                    processed_channel = F.conv2d(channel, kernel_2d, stride=stride, padding=padding)
                    processed_channels.append(processed_channel)
                
                # Combine channels back
                current_tensor = torch.cat(processed_channels, dim=1)
                
                # Calculate new receptive field and jump
                receptive_field = receptive_field + (kernel_size - 1) * jump
                jump = jump * stride
                
            elif layer_type == 'maxpool':
                # Get max pooling parameters
                kernel_size = layer.get('kernel_size', 2)
                stride = layer.get('stride', kernel_size)  # Default stride equals kernel_size
                padding = layer.get('padding', 0)
                
                # Apply max pooling
                current_tensor = F.max_pool2d(current_tensor, 
                                            kernel_size=kernel_size, 
                                            stride=stride, 
                                            padding=padding)
                
                # Calculate new receptive field and jump
                receptive_field = receptive_field + (kernel_size - 1) * jump
                jump = jump * stride
                
            elif layer_type == 'avgpool':
                # Get average pooling parameters
                kernel_size = layer.get('kernel_size', 2)
                stride = layer.get('stride', kernel_size)  # Default stride equals kernel_size
                padding = layer.get('padding', 0)
                
                # Apply average pooling
                current_tensor = F.avg_pool2d(current_tensor, 
                                            kernel_size=kernel_size, 
                                            stride=stride, 
                                            padding=padding)
                
                # Calculate new receptive field and jump
                receptive_field = receptive_field + (kernel_size - 1) * jump
                jump = jump * stride
                
            elif layer_type == 'relu':
                # Apply ReLU activation (clamp negative values to 0)
                current_tensor = F.relu(current_tensor)
                # ReLU doesn't change spatial dimensions or receptive field
                
            elif layer_type == 'batchnorm':
                # Simple batch normalization (normalize each channel)
                # Note: This is a simplified version for demonstration
                mean = current_tensor.mean(dim=[2, 3], keepdim=True)
                std = current_tensor.std(dim=[2, 3], keepdim=True) + 1e-8
                current_tensor = (current_tensor - mean) / std
                # Batch norm doesn't change spatial dimensions or receptive field
                
            elif layer_type == 'dropout':
                # Apply dropout during inference (for demonstration)
                dropout_rate = layer.get('dropout_rate', 0.1)
                if dropout_rate > 0:
                    # Create a mask for demonstration (not true dropout)
                    mask = torch.rand_like(current_tensor) > dropout_rate
                    current_tensor = current_tensor * mask.float()
                # Dropout doesn't change spatial dimensions or receptive field
            
            else:
                return jsonify({'error': f'Unknown layer type: {layer_type}'}), 400
            
            # Clip values to [0, 1] range
            current_tensor = torch.clamp(current_tensor, 0, 1)
            
            # Get output dimensions
            output_shape = list(current_tensor.shape)
            
            # Convert tensor to base64
            base64_image = tensor_to_base64(current_tensor)
            
            # Append result for this layer
            results.append({
                'layer_index': layer_idx,
                'layer_type': layer_type,
                'base64_image': base64_image,
                'output_shape': output_shape,
                'receptive_field': receptive_field,
                'jump': jump
            })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )
