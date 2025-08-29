# Contributing to Visual Neural Network

We love your input! We want to make contributing to Visual Neural Network as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## 🚀 Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

1. Fork the repo and create your branch from `main`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## 🐛 Report bugs using GitHub's [issue tracker](https://github.com/your-username/visual-nn/issues)

We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/your-username/visual-nn/issues/new).

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give sample code if you can
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check if the feature has already been requested in [issues](https://github.com/your-username/visual-nn/issues)
2. Describe the feature clearly and provide context on why it would be useful
3. Include mockups or examples if possible
4. Consider the scope - is it a small enhancement or a major feature?

## 🛠️ Development Setup

### Prerequisites

- Python 3.7+
- `uv` package manager (recommended) or `pip`
- A modern web browser for testing

### Setup Steps

1. **Fork and clone the repository**

   ```bash
   git clone https://github.com/your-username/visual-nn.git
   cd visual-nn
   ```

2. **Install dependencies**

   ```bash
   uv pip install -r requirements.txt
   ```

3. **Start the development server**

   ```bash
   python app.py
   ```

4. **Test your changes**
   - Open `index.html` in your browser
   - Test with various images and layer combinations
   - Verify all visualization modes work correctly

## 📝 Code Style

### Python (Backend)

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and modular

### JavaScript (Frontend)

- Use consistent indentation (2 spaces)
- Use meaningful variable names
- Add comments for complex logic
- Follow modern ES6+ practices

### HTML/CSS

- Use semantic HTML elements
- Maintain Tailwind CSS class consistency
- Ensure responsive design works on all screen sizes

## 🧪 Testing Guidelines

### Manual Testing Checklist

- [ ] Upload different image formats (PNG, JPG, etc.)
- [ ] Test all layer types with various parameters
- [ ] Verify all visualization tabs work correctly
- [ ] Test responsive design on different screen sizes
- [ ] Check browser console for errors
- [ ] Test with both small and large images

### Before Submitting

- [ ] Code runs without errors
- [ ] All existing functionality still works
- [ ] New features are properly documented
- [ ] Code follows style guidelines

## 🔄 Pull Request Process

1. **Create a descriptive PR title**

   - Good: "Add custom kernel designer with interactive grid"
   - Bad: "Update frontend"

2. **Write a clear description**

   - What changes were made?
   - Why were they made?
   - How do they work?
   - Any breaking changes?

3. **Link related issues**

   - Use "Fixes #123" or "Closes #123" to auto-close issues

4. **Request review**
   - Tag relevant maintainers
   - Be responsive to feedback

### PR Template

```markdown
## Description

Brief description of changes

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?

Describe the tests you ran to verify your changes

## Screenshots (if applicable)

Add screenshots to help explain your changes

## Checklist

- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] My changes generate no new warnings
- [ ] I have tested this with multiple browsers and screen sizes
```

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

### 🚀 High Priority

- **Performance optimization** for large images
- **Mobile responsiveness** improvements
- **Accessibility** enhancements (ARIA labels, keyboard navigation)
- **Error handling** and user feedback

### 🎨 Frontend Enhancements

- **Live convolution animation** showing kernel sliding
- **Custom kernel designer** with interactive grid
- **3D visualization** of multi-channel feature maps
- **Dark mode** theme support

### 🧠 Educational Features

- **Interactive tutorials** for CNN concepts
- **Guided walkthroughs** for common use cases
- **Quiz system** for testing understanding
- **Video explanations** integration

### 🔧 Technical Improvements

- **Unit tests** for backend functions
- **Integration tests** for API endpoints
- **Docker** containerization
- **CI/CD** pipeline setup

## 📚 Resources

### Understanding CNNs

- [Deep Learning Specialization](https://www.coursera.org/specializations/deep-learning)
- [CS231n: Convolutional Neural Networks](http://cs231n.github.io/)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)

### Web Development

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [MDN Web Docs](https://developer.mozilla.org/)

## ❓ Questions?

Don't hesitate to ask questions! You can:

1. Open an issue with the "question" label
2. Start a discussion in the repository
3. Reach out to maintainers directly

## 🙏 Recognition

Contributors will be recognized in:

- The README.md contributors section
- Release notes for significant contributions
- Special thanks in documentation

Thank you for contributing to Visual Neural Network! 🎉
