# 🧠 Visual Neural Network

An interactive web application for visualizing and understanding how Convolutional Neural Networks (CNNs) process images. This educational tool demonstrates CNN operations through real-time layer processing, multiple visualization modes, and comprehensive explanations.

![Visual Neural Network Demo](demo.png)

## ✨ Features

### 🧠 **AI-Powered Architecture Designer**

- **Smart layer suggestions** powered by Google Gemini AI
- **Content-aware recommendations** based on image analysis
- **Real-time AI explanations** for each layer's effect
- **Intelligent tutoring** with personalized guidance

### 🎯 **Interactive CNN Visualization**

- **Real-time layer processing** with immediate visual feedback
- **Multiple layer types**: Conv2D, Max/Average Pooling, ReLU, Batch Normalization, Dropout
- **Advanced kernels**: Sharpen, Blur, Gaussian, Sobel, Laplacian, Emboss, Edge Enhancement
- **Live parameter preview** showing effects before adding layers

### 📊 **Multiple Visualization Modes**

- **🖼️ Basic View**: Standard layer output visualization
- **🗺️ Feature Maps**: Individual RGB channel separation and analysis
- **📊 Statistics**: Activation statistics (mean, std deviation, sparsity)
- **🔍 Comparison**: Side-by-side layer transformations

### 🎓 **Educational Features**

- **Interactive tutorial** explaining CNN concepts
- **Layer-by-layer explanations** with mathematical formulas
- **Kernel visualizations** with color-coded values
- **Receptive field calculations** and tracking
- **Hover tooltips** with pixel-level information

### 🔧 **Technical Capabilities**

- **Lightweight NumPy/SciPy backend** optimized for t3.micro deployment
- **Google Gemini AI integration** for intelligent suggestions
- **Real-time image processing** via Flask API
- **Responsive web interface** built with Tailwind CSS
- **Memory-optimized operations** for low-resource environments
- **Support for custom parameters** (stride, padding, kernel types)

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- `uv` package manager (recommended) or `pip`
- Google Gemini API key (get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Quick Setup

```bash
# Clone and setup
git clone https://github.com/your-username/visual-nn.git
cd visual-nn

# Run the automated setup
./setup_lightweight.sh

# Set your Gemini API key
export GEMINI_API_KEY="your_api_key_here"

# Start the server
python app.py
```

Open `http://localhost:5001` to start using Visual Neural Network with AI!

### Manual Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/visual-nn.git
   cd visual-nn
   ```

2. **Install dependencies**

   ```bash
   # Using uv (recommended)
   uv pip install -r requirements.txt

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Configure environment**

   ```bash
   # Copy environment template
   cp env.example .env

   # Edit .env and add your GEMINI_API_KEY
   # Or export directly:
   export GEMINI_API_KEY="your_api_key_here"
   ```

4. **Start the Flask server**

   ```bash
   python app.py
   ```

   The server will start on `http://localhost:5001`

5. **Open the application**
   - Open `index.html` in your web browser
   - Or visit the served HTML if you set up a web server

## 📖 How to Use

### 1. Upload an Image

- Click "Choose File" to upload any image (PNG, JPG, etc.)
- The image will be displayed and converted for processing

### 2. Build Your CNN Architecture

- Select layer type from the dropdown
- Configure parameters (kernel type, stride, padding, etc.)
- Preview the layer effect in real-time
- Click "Add Layer" to add it to your architecture

### 3. Explore Results

- **Basic View**: See processed images for each layer
- **Feature Maps**: Analyze individual color channels
- **Statistics**: View activation distributions and metrics
- **Comparison**: Compare before/after transformations

### 4. Learn CNN Concepts

- Click "Show CNN Tutorial" for guided learning
- Hover over outputs for detailed pixel information
- Experiment with different kernel types and parameters

## 🧪 Example Workflows

### Edge Detection Pipeline

```
1. Upload an image with clear edges
2. Add Conv2D → Sobel X kernel
3. Add Conv2D → Sobel Y kernel
4. Add ReLU activation
5. Switch to Comparison tab to see edge detection progress
```

### Feature Enhancement

```
1. Upload a slightly blurry image
2. Add Conv2D → Gaussian Blur
3. Add Conv2D → Sharpen kernel
4. Add Max Pooling (2x2)
5. View Feature Maps to see channel responses
```

## 🏗️ Architecture

### Backend (`app.py`)

- **Flask web server** handling API requests
- **PyTorch operations** for authentic CNN processing
- **Image processing utilities** for base64 conversion
- **Multiple kernel implementations** with mathematical accuracy

### Frontend (`index.html`)

- **Single-page application** with Tailwind CSS styling
- **Real-time parameter updates** and visual previews
- **Multiple visualization tabs** for different analysis modes
- **Educational tooltips and explanations**

### Key Components

```
visual-nn/
├── app.py              # Flask backend with CNN operations
├── index.html          # Complete frontend application
├── requirements.txt    # Python dependencies
└── README.md          # This documentation
```

## 🎯 Supported Layer Types

| Layer Type      | Purpose                   | Parameters                   |
| --------------- | ------------------------- | ---------------------------- |
| **Conv2D**      | Feature detection         | Kernel type, stride, padding |
| **Max Pooling** | Downsampling (max values) | Kernel size, stride, padding |
| **Avg Pooling** | Downsampling (averaging)  | Kernel size, stride, padding |
| **ReLU**        | Non-linear activation     | None                         |
| **Batch Norm**  | Activation normalization  | None                         |
| **Dropout**     | Regularization            | Dropout rate                 |

## 🔧 Available Kernels

| Kernel Type      | Effect                    | Use Case            |
| ---------------- | ------------------------- | ------------------- |
| **Sharpen**      | Edge enhancement          | Detail improvement  |
| **Blur**         | Smoothing                 | Noise reduction     |
| **Gaussian**     | Weighted smoothing        | Advanced blurring   |
| **Sobel X**      | Vertical edge detection   | Feature extraction  |
| **Sobel Y**      | Horizontal edge detection | Feature extraction  |
| **Laplacian**    | Edge enhancement          | Boundary detection  |
| **Emboss**       | 3D-like effects           | Artistic processing |
| **Edge Enhance** | Directional edges         | Feature sharpening  |
| **Identity**     | No change                 | Testing/comparison  |

## 🧠 Educational Value

This tool is designed for:

- **Students** learning computer vision and deep learning with AI guidance
- **Educators** teaching CNN concepts with intelligent tutoring assistance
- **Researchers** prototyping architectures with AI-powered suggestions
- **Developers** understanding layer-by-layer transformations with explanations
- **Anyone curious** about how neural networks and AI work together

### 🤖 AI Features in Detail

- **Smart Architecture Designer**: Gemini AI analyzes your uploaded image and suggests optimal layer sequences
- **Content-Aware Recommendations**: Different suggestions for portraits, landscapes, text, and abstract images
- **Real-time Explanations**: AI explains what each layer does to your specific image
- **Intelligent Tutoring**: Personalized guidance based on your current architecture
- **Fallback Support**: Works perfectly even without AI - degrades gracefully to manual mode

## 🛠️ Development

### Running in Development Mode

```bash
# Start Flask with auto-reload
python app.py

# The server runs on port 5001 with debug mode enabled
# File changes automatically restart the server
```

### Adding New Features

1. **New layer types**: Add to `app.py` processing logic and `index.html` UI
2. **New kernels**: Define in `get_kernel()` function and update frontend options
3. **New visualizations**: Add new tabs in the frontend visualization system

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly with different images and layer combinations
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyTorch** for the neural network operations
- **Flask** for the web framework
- **Tailwind CSS** for the beautiful styling
- **OpenAI** for development assistance

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-username/visual-nn/issues) page
2. Create a new issue with detailed description
3. Include browser version, Python version, and error messages

## 🔮 Future Enhancements

- [ ] Live convolution animation showing kernel sliding
- [ ] Custom kernel designer with interactive grid
- [ ] 3D visualization of multi-channel feature maps
- [ ] Educational quizzes and challenges
- [ ] Export functionality for results and architectures
- [ ] Mobile app version
- [ ] Integration with popular ML frameworks

---

**Built with ❤️ for the machine learning community**

_Star ⭐ this repo if you found it helpful!_
