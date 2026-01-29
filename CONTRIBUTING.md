# Contributing to TutorDraw

Thank you for your interest in contributing to TutorDraw! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you are expected to uphold our community standards:
- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Gracefully accept constructive criticism

## Getting Started

### Prerequisites
- Python 3.7 or higher
- Basic understanding of PyQt5
- Git installed on your system

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork the repository on GitHub
   # Clone your fork
   git clone https://github.com/yourusername/TutorDraw.git
   cd TutorDraw
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install development dependencies (if available)
   pip install pytest black flake8
   ```

3. **Verify Setup**
   ```bash
   python main.py
   ```

## Project Structure

```
TutorDraw/
├── src/                 # Main source code
│   ├── canvas.py       # Core canvas functionality
│   ├── toolbar.py      # Toolbar implementation
│   ├── themes.py       # Theme management
│   └── ...             # Other modules
├── tutorDraw/          # Alternative implementation
├── main.py            # Application entry point
├── README.md          # User documentation
└── CONTRIBUTING.md    # This file
```

## Development Guidelines

### Code Style
- Follow PEP 8 guidelines
- Use 4 spaces for indentation
- Keep lines under 88 characters
- Use descriptive variable and function names
- Add docstrings to public functions and classes

### Testing
- Test your changes thoroughly
- Ensure existing functionality isn't broken
- Run the application to verify UI changes

### Git Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**
   - Write clear, concise commit messages
   - Make small, focused commits
   - Reference related issues in commit messages

3. **Before Submitting**
   ```bash
   # Run tests if available
   # Check code style
   black src/
   flake8 src/
   ```

4. **Submit Pull Request**
   - Push to your fork
   - Create PR with clear description
   - Link to related issues

## Areas for Contribution

### Bug Fixes
- Check the issues tab for reported bugs
- Reproduce the issue locally
- Fix and test thoroughly
- Include steps to verify the fix

### New Features
Before implementing new features:
1. Check if similar functionality exists
2. Discuss the feature in an issue first
3. Consider impact on performance (especially for low-end PCs)
4. Ensure cross-platform compatibility

### Documentation
- Improve existing documentation
- Add examples and tutorials
- Fix typos and clarify confusing sections
- Update README with new features

### UI/UX Improvements
- Enhance toolbar design
- Improve accessibility
- Optimize for different screen sizes
- Maintain lightweight performance

## Specific Contribution Areas

### Core Functionality
- Drawing tool improvements
- Performance optimizations
- Cross-platform compatibility
- Memory usage optimization

### User Interface
- Theme enhancements
- Toolbar layout improvements
- Animation refinements
- Keyboard shortcut additions

### Features
- New drawing tools
- Export functionality
- Collaboration features
- Integration with other tools

## Testing Guidelines

### Manual Testing
- Test on different operating systems
- Verify keyboard shortcuts work
- Check toolbar hide/show functionality
- Test drawing tools thoroughly
- Verify theme switching

### Performance Testing
- Test on low-end hardware if possible
- Monitor memory usage
- Check startup time
- Verify smooth drawing experience

## Pull Request Process

1. **Before Submitting**
   - Ensure code follows style guidelines
   - Test thoroughly on multiple platforms
   - Update documentation if needed
   - Include screenshots for UI changes

2. **PR Description**
   - Clear title describing the change
   - Detailed description of changes
   - Steps to test the functionality
   - Reference related issues

3. **Review Process**
   - Maintainers will review your code
   - Address feedback promptly
   - Be open to suggestions
   - Make requested changes

## Communication

### Getting Help
- Check existing issues and documentation first
- Ask questions in issues for discussion
- Be specific about your problem or question

### Reporting Issues
When reporting bugs:
- Include steps to reproduce
- Mention your operating system
- Provide screenshots if relevant
- Include error messages

## Recognition

Contributors will be:
- Added to the contributors list
- Mentioned in release notes
- Given appropriate credit for their work

## License

By contributing to TutorDraw, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing:
1. Check existing documentation
2. Look through open issues
3. Open a new issue for discussion
4. Be patient - maintainers review contributions in their spare time

Thank you for contributing to TutorDraw!