from flask import Flask, request, jsonify, g
from flask_cors import CORS
import google.generativeai as genai
import base64
import io
import json
import hashlib
import time
from functools import lru_cache, wraps
from PIL import Image
import numpy as np
from scipy import ndimage
import psutil
import os
from config import config

# Initialize Flask app with configuration
app = Flask(__name__)
config_name = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[config_name])

# Enable CORS for all routes
CORS(app, origins=app.config['CORS_ORIGINS'])

# Configure Gemini AI
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')  # Lightweight model

# Memory and performance monitoring
def monitor_memory():
    """Monitor and manage memory usage for t3.micro"""
    memory_percent = psutil.virtual_memory().percent
    if memory_percent > 80:  # Approaching limit
        return True
    return False

@app.before_request
def check_resources():
    """Prevent memory overflow and set AI availability"""
    g.ai_enabled = not monitor_memory()
    if not g.ai_enabled:
        print("⚠️ High memory usage, AI features temporarily disabled")

# Caching system for Gemini responses
class GeminiCache:
    def __init__(self, max_size=50):
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}
    
    def get_image_hash(self, image_data):
        """Create hash for similar images"""
        return hashlib.md5(image_data.encode() if isinstance(image_data, str) else image_data).hexdigest()[:8]
    
    def get(self, key):
        """Get cached result"""
        if key in self.cache:
            self.access_times[key] = time.time()
            return self.cache[key]
        return None
    
    def set(self, key, value):
        """Store result with LRU eviction"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = value
        self.access_times[key] = time.time()

# Initialize cache
gemini_cache = GeminiCache()

# Rate limiting for API calls
class APIRateLimit:
    def __init__(self, max_calls_per_minute=10):
        self.max_calls = max_calls_per_minute
        self.calls = []
    
    def can_make_call(self):
        now = time.time()
        # Remove calls older than 1 minute
        self.calls = [call_time for call_time in self.calls if now - call_time < 60]
        
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False

rate_limiter = APIRateLimit()

def base64_to_array(base64_string):
    """
    Convert Base64-encoded image to numpy array.
    
    Args:
        base64_string (str): Base64-encoded image string
        
    Returns:
        np.ndarray: Image array with shape [H, W, 3], normalized to [0, 1]
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
    
    return image_array

def array_to_base64(image_array):
    """
    Convert numpy array to Base64-encoded image string.
    
    Args:
        image_array (np.ndarray): Image array with shape [H, W, 3], values in [0, 1]
        
    Returns:
        str: Base64-encoded image string
    """
    # Denormalize to [0, 255] and convert to uint8
    image_array = np.clip(image_array * 255.0, 0, 255).astype(np.uint8)
    
    # Convert to PIL Image
    image = Image.fromarray(image_array)
    
    # Convert to base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    image_data = buffer.getvalue()
    
    return base64.b64encode(image_data).decode('utf-8')

def get_kernel(kernel_type, kernel_size=3):
    """
    Returns a numpy array representing a kernel based on the kernel type.
    
    Args:
        kernel_type (str): Type of kernel to generate
        kernel_size (int): Size of the kernel (default: 3)
        
    Returns:
        np.ndarray: kernel array
    """
    if kernel_type == 'sharpen' or kernel_type == 'default':
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=np.float32)
    
    elif kernel_type == 'blur':
        kernel = np.ones((3, 3), dtype=np.float32) / 9
    
    elif kernel_type == 'sobel_x':
        kernel = np.array([
            [-1, 0, 1],
            [-2, 0, 2],
            [-1, 0, 1]
        ], dtype=np.float32)
    
    elif kernel_type == 'sobel_y':
        kernel = np.array([
            [-1, -2, -1],
            [0, 0, 0],
            [1, 2, 1]
        ], dtype=np.float32)
    
    elif kernel_type == 'gaussian':
        kernel = np.array([
            [1/16, 2/16, 1/16],
            [2/16, 4/16, 2/16],
            [1/16, 2/16, 1/16]
        ], dtype=np.float32)
    
    elif kernel_type == 'laplacian':
        kernel = np.array([
            [0, -1, 0],
            [-1, 4, -1],
            [0, -1, 0]
        ], dtype=np.float32)
    
    elif kernel_type == 'emboss':
        kernel = np.array([
            [-2, -1, 0],
            [-1, 1, 1],
            [0, 1, 2]
        ], dtype=np.float32)
    
    elif kernel_type == 'edge_enhance':
        kernel = np.array([
            [0, 0, 0],
            [-1, 1, 0],
            [0, 0, 0]
        ], dtype=np.float32)
    
    elif kernel_type == 'identity':
        kernel = np.array([
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0]
        ], dtype=np.float32)
    
    else:
        # Default to sharpen kernel
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=np.float32)
    
    return kernel

def apply_convolution(image_array, kernel, stride=1, padding=1):
    """Apply convolution using scipy.ndimage"""
    # Add padding if needed
    if padding > 0:
        image_array = np.pad(image_array, ((padding, padding), (padding, padding), (0, 0)), mode='edge')
    
    # Apply convolution to each channel
    result_channels = []
    for c in range(image_array.shape[2]):
        convolved = ndimage.convolve(image_array[:, :, c], kernel, mode='constant')
        # Apply stride by sub-sampling
        if stride > 1:
            convolved = convolved[::stride, ::stride]
        result_channels.append(convolved)
    
    # Stack channels back together
    result = np.stack(result_channels, axis=2)
    return result

def apply_pooling(image_array, pool_type='max', kernel_size=2, stride=None, padding=0):
    """Apply max or average pooling"""
    if stride is None:
        stride = kernel_size
    
    h, w, c = image_array.shape
    
    # Add padding if needed
    if padding > 0:
        image_array = np.pad(image_array, ((padding, padding), (padding, padding), (0, 0)), mode='edge')
        h, w = image_array.shape[:2]
    
    # Calculate output dimensions
    out_h = (h - kernel_size) // stride + 1
    out_w = (w - kernel_size) // stride + 1
    
    result = np.zeros((out_h, out_w, c), dtype=np.float32)
    
    for i in range(out_h):
        for j in range(out_w):
            h_start, h_end = i * stride, i * stride + kernel_size
            w_start, w_end = j * stride, j * stride + kernel_size
            
            pool_region = image_array[h_start:h_end, w_start:w_end, :]
            
            if pool_type == 'max':
                result[i, j, :] = np.max(pool_region, axis=(0, 1))
            elif pool_type == 'avg':
                result[i, j, :] = np.mean(pool_region, axis=(0, 1))
    
    return result

def optimize_image_for_gemini(image_base64, max_size=128):
    """Optimize image for Gemini API to reduce bandwidth"""
    image_data = base64.b64decode(image_base64)
    image = Image.open(io.BytesIO(image_data))
    
    # Resize to small size for analysis
    image = image.resize((max_size, max_size))
    image = image.convert('RGB')
    
    # Compress for API
    buffer = io.BytesIO()
    image.save(buffer, format='JPEG', quality=60)
    optimized_data = buffer.getvalue()
    
    return base64.b64encode(optimized_data).decode('utf-8')

@lru_cache(maxsize=20)
def get_template_suggestions(image_hash):
    """Fallback template-based suggestions"""
    templates = {
        'default': {
            'image_type': 'general',
            'quality_assessment': 'Standard image quality',
            'suggested_layers': [
                {'type': 'conv', 'kernel': 'gaussian', 'kernel_size': 3, 'reasoning': 'Smooth noise and artifacts'},
                {'type': 'conv', 'kernel': 'sharpen', 'kernel_size': 3, 'reasoning': 'Enhance important features'}
            ],
            'expected_outcome': 'Improved image clarity with reduced noise'
        }
    }
    return templates['default']

@app.route('/', methods=['GET'])
def index():
    """Serve the main UI."""
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except FileNotFoundError:
        return "index.html not found. Please ensure it's in the same directory as app.py"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to confirm the server is running."""
    return "Visual-NN Lightweight Server with Gemini AI is running! 🧠✨"

@app.route('/test-ai', methods=['GET'])
def test_ai():
    """Test if Gemini AI is working."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({
            'status': 'error',
            'message': 'GEMINI_API_KEY not found in environment variables',
            'ai_enabled': False
        })
    
    try:
        # Simple test prompt
        response = model.generate_content("Say 'AI is working!' in one sentence.")
        return jsonify({
            'status': 'success',
            'message': 'Gemini AI is working correctly!',
            'response': response.text,
            'ai_enabled': True
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Gemini API error: {str(e)}',
            'ai_enabled': False
        })

@app.route('/debug-routes', methods=['GET'])
def debug_routes():
    """Debug: Show all available routes."""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return jsonify({'routes': routes})

@app.route('/analyze-image-ai', methods=['POST'])
def analyze_image_ai():
    """NEW: AI analysis endpoint powered by Gemini"""
    print(f"🔍 analyze-image-ai called - Method: {request.method}")
    print(f"🔍 Content-Type: {request.content_type}")
    print(f"🔍 Headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        print(f"🔍 JSON data received: {data is not None}")
        
        if data is None:
            print("❌ No JSON data received")
            return jsonify({'error': 'No JSON data received'}), 400
            
        image_base64 = data.get('image_base64')
        print(f"🔍 Image data length: {len(image_base64) if image_base64 else 0}")
        
        if not image_base64:
            return jsonify({'error': 'No image_base64 provided'}), 400
        
        # Check if AI is available
        if not g.ai_enabled:
            return jsonify(get_template_suggestions('fallback'))
        
        # Get cached result if available
        image_hash = gemini_cache.get_image_hash(image_base64)
        cached_result = gemini_cache.get(image_hash)
        if cached_result:
            return jsonify(cached_result)
        
        # Check rate limit
        if not rate_limiter.can_make_call():
            return jsonify(get_template_suggestions(image_hash))
        
        # Optimize image for Gemini
        optimized_image_base64 = optimize_image_for_gemini(image_base64)
        optimized_image_data = base64.b64decode(optimized_image_base64)
        
        # Prepare prompt for Gemini
        prompt = """
        Analyze this image and suggest 2-4 CNN layers for enhancement.
        Consider the image content, quality, and potential improvements.
        
        Respond with JSON only (no extra text):
        {
            "image_type": "portrait/landscape/text/abstract/object",
            "quality_assessment": "brief description of image quality",
            "suggested_layers": [
                {
                    "type": "conv",
                    "kernel": "gaussian",
                    "kernel_size": 3,
                    "reasoning": "why this layer helps this specific image"
                }
            ],
            "expected_outcome": "what the final result should achieve for this image"
        }
        
        Available layer types: conv, maxpool, avgpool, relu, batchnorm, dropout
        Available kernels: sharpen, blur, gaussian, sobel_x, sobel_y, laplacian, emboss, edge_enhance, identity
        """
        
        # Call Gemini API
        response = model.generate_content([
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": optimized_image_data
            }
        ])
        
        # Parse JSON response
        try:
            # Extract JSON from response text
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:-3]
            elif response_text.startswith('```'):
                response_text = response_text[3:-3]
            
            result = json.loads(response_text)
            
            # Cache the result
            gemini_cache.set(image_hash, result)
            
            return jsonify(result)
            
        except json.JSONDecodeError:
            # Fallback to template if JSON parsing fails
            return jsonify(get_template_suggestions(image_hash))
        
    except Exception as e:
        print(f"Gemini API error: {str(e)}")
        # Fallback to template suggestions
        image_hash = gemini_cache.get_image_hash(image_base64) if image_base64 else 'error'
        return jsonify(get_template_suggestions(image_hash))

@app.route('/process-layers', methods=['POST'])
def process_layers():
    """
    Enhanced POST endpoint for processing image layers with optional AI insights.
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        image_base64 = data.get('image_base64')
        layers = data.get('layers', [])
        request_ai_insights = data.get('ai_insights', False)
        
        if not image_base64:
            return jsonify({'error': 'No image_base64 data provided'}), 400
        
        if not layers:
            return jsonify({'error': 'No layers array provided'}), 400
        
        # Convert to numpy array
        current_array = base64_to_array(image_base64)
        
        # Initialize results
        results = []
        receptive_field = 1
        jump = 1
        
        # Process each layer
        for layer_idx, layer in enumerate(layers):
            layer_type = layer.get('type')
            input_shape = list(current_array.shape)
            
            if layer_type == 'conv':
                # Convolution layer
                kernel_type = layer.get('kernel_type', 'default')
                stride = layer.get('stride', 1)
                padding = layer.get('padding', 1)
                
                kernel = get_kernel(kernel_type)
                kernel_size = kernel.shape[0]
                
                # Apply convolution
                current_array = apply_convolution(current_array, kernel, stride, padding)
                
                # Update receptive field and jump
                receptive_field = receptive_field + (kernel_size - 1) * jump
                jump = jump * stride
                
            elif layer_type == 'maxpool':
                # Max pooling layer
                kernel_size = layer.get('kernel_size', 2)
                stride = layer.get('stride', kernel_size)
                padding = layer.get('padding', 0)
                
                current_array = apply_pooling(current_array, 'max', kernel_size, stride, padding)
                
                # Update receptive field and jump
                receptive_field = receptive_field + (kernel_size - 1) * jump
                jump = jump * stride
                
            elif layer_type == 'avgpool':
                # Average pooling layer
                kernel_size = layer.get('kernel_size', 2)
                stride = layer.get('stride', kernel_size)
                padding = layer.get('padding', 0)
                
                current_array = apply_pooling(current_array, 'avg', kernel_size, stride, padding)
                
                # Update receptive field and jump
                receptive_field = receptive_field + (kernel_size - 1) * jump
                jump = jump * stride
                
            elif layer_type == 'relu':
                # ReLU activation
                current_array = np.maximum(0, current_array)
                
            elif layer_type == 'batchnorm':
                # Simplified batch normalization
                mean = np.mean(current_array, axis=(0, 1), keepdims=True)
                std = np.std(current_array, axis=(0, 1), keepdims=True) + 1e-8
                current_array = (current_array - mean) / std
                
            elif layer_type == 'dropout':
                # Simplified dropout for demonstration
                dropout_rate = layer.get('dropout_rate', 0.1)
                if dropout_rate > 0:
                    mask = np.random.random(current_array.shape) > dropout_rate
                    current_array = current_array * mask
                    
            else:
                return jsonify({'error': f'Unknown layer type: {layer_type}'}), 400
            
            # Clip values to [0, 1]
            current_array = np.clip(current_array, 0, 1)
            
            # Get output shape
            output_shape = list(current_array.shape)
            
            # Convert back to base64
            base64_image = array_to_base64(current_array)
            
            # Prepare result
            result = {
                'layer_index': layer_idx,
                'layer_type': layer_type,
                'base64_image': base64_image,
                'input_shape': input_shape,
                'output_shape': output_shape,
                'receptive_field': receptive_field,
                'jump': jump
            }
            
            # Add AI insight if requested and available
            if request_ai_insights and g.ai_enabled:
                try:
                    insight_response = get_layer_insight_internal(layer_type, layer, input_shape, output_shape)
                    result['ai_insight'] = insight_response['insight']
                    result['technical_details'] = insight_response['technical_details']
                except:
                    result['ai_insight'] = f"This {layer_type} layer processes the image."
                    result['technical_details'] = f"{input_shape} → {output_shape}"
            
            results.append(result)
        
        return jsonify({
            'success': True,
            'results': results,
            'ai_enabled': g.ai_enabled
        })
        
    except Exception as e:
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500

def get_layer_insight_internal(layer_type, layer_params, input_shape, output_shape):
    """Internal function to get layer insights"""
    default_insights = {
        'conv': {
            'insight': 'Convolution layer detects features like edges, textures, or patterns in the image.',
            'technical_details': f'Applies kernel filters to extract features. {input_shape} → {output_shape}'
        },
        'maxpool': {
            'insight': 'Max pooling reduces image size while keeping the strongest features.',
            'technical_details': f'Downsamples by taking maximum values. {input_shape} → {output_shape}'
        },
        'avgpool': {
            'insight': 'Average pooling smooths the image while reducing its size.',
            'technical_details': f'Downsamples by averaging pixel values. {input_shape} → {output_shape}'
        },
        'relu': {
            'insight': 'ReLU activation removes negative values, adding non-linearity.',
            'technical_details': f'Sets negative pixels to zero. {input_shape} → {output_shape}'
        },
        'batchnorm': {
            'insight': 'Batch normalization stabilizes the image values for better processing.',
            'technical_details': f'Normalizes pixel values per channel. {input_shape} → {output_shape}'
        },
        'dropout': {
            'insight': 'Dropout randomly masks some pixels to prevent overfitting.',
            'technical_details': f'Random masking for regularization. {input_shape} → {output_shape}'
        }
    }
    
    return default_insights.get(layer_type, {
        'insight': f'{layer_type} layer processes the image data.',
        'technical_details': f'{input_shape} → {output_shape}'
    })

if __name__ == '__main__':
    app.run(
        debug=app.config['DEBUG'],
        host=app.config['HOST'],
        port=app.config['PORT']
    )
