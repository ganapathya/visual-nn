"""
Memory-optimized configuration for t3.micro (1GB RAM)
"""

import os

class T3MicroConfig:
    """Optimized configuration for AWS t3.micro instances."""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-in-production'
    DEBUG = False
    
    # Server settings optimized for t3.micro
    HOST = '127.0.0.1'  # Only bind to localhost (Nginx will proxy)
    PORT = 5001
    THREADED = False  # Disable threading to save memory
    
    # Memory optimizations
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB max upload
    
    # Gemini API settings
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_RATE_LIMIT = 5  # Requests per minute
    GEMINI_CACHE_SIZE = 20  # Cached responses
    
    # Image processing limits
    MAX_IMAGE_SIZE = 512  # Max image dimension for processing
    COMPRESSION_QUALITY = 70  # JPEG compression for Gemini
    
    # CORS settings
    CORS_ORIGINS = ['*']  # Allow all origins (Nginx handles security)
    
    @staticmethod
    def optimize_memory():
        """Apply memory optimizations."""
        import gc
        
        # Force garbage collection
        gc.collect()
        
        # Set environment variables for memory optimization
        os.environ['PYTHONOPTIMIZE'] = '1'
        os.environ['PYTHONHASHSEED'] = '0'
        
        # Disable some Python features to save memory
        try:
            import sys
            # Remove unused modules from sys.modules
            modules_to_remove = [mod for mod in sys.modules.keys() 
                               if 'test' in mod or 'debug' in mod]
            for mod in modules_to_remove:
                if mod in sys.modules:
                    del sys.modules[mod]
        except:
            pass
