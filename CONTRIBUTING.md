# Contributing to Ottawa City Services RAG Chatbot

Thank you for your interest in contributing to the Ottawa City Services RAG Chatbot! 🎉

## 🚀 Quick Start for Contributors

### Prerequisites
- Python 3.8+
- Git
- Virtual environment tool (venv/conda)

### Setup Development Environment

```bash
# 1. Fork and clone the repository
git clone https://github.com/yourusername/ottawa-rag-chatbot.git
cd ottawa-rag-chatbot

# 2. Create virtual environment
python -m venv ottawa-py311-env
source ottawa-py311-env/bin/activate  # On Windows: ottawa-py311-env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Set up pre-commit hooks
pre-commit install

# 5. Create .env file
cp .env.example .env
# Add your GROQ_API_KEY
```

## 📋 Ways to Contribute

### 🐛 Bug Reports
- Use the GitHub issue tracker
- Include system information (OS, Python version)
- Provide steps to reproduce
- Include error messages and logs

### 🌟 Feature Requests
- Check existing issues first
- Explain the use case and benefit
- Provide examples if possible

### 💻 Code Contributions
- Fork the repository
- Create a feature branch: `git checkout -b feature/amazing-feature`
- Make your changes
- Add tests for new functionality
- Ensure all tests pass: `pytest`
- Follow code style guidelines
- Commit with clear messages
- Push and create a Pull Request

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_rag_pipeline.py -v
```

### Writing Tests
- Place tests in the `tests/` directory
- Use descriptive test names
- Follow the existing test patterns
- Include both unit and integration tests

## 📝 Code Style

### Python Style Guide
- Follow PEP 8
- Use Black for formatting: `black src/ tests/`
- Use flake8 for linting: `flake8 src/ tests/`
- Maximum line length: 88 characters

### Documentation
- Write clear docstrings for all functions and classes
- Update README.md for significant changes
- Include inline comments for complex logic

## 🗂️ Project Structure

```
ottawa-rag-chatbot/
├── src/                    # Core implementation
│   ├── scraper.py         # Web scraping
│   ├── data_processor.py  # Text processing
│   ├── rag_pipeline.py    # RAG implementation
│   ├── vector_store.py    # Vector database
│   └── chatbot.py         # Main orchestrator
├── tests/                 # Test suite
├── data/                  # Datasets
├── deployment/            # Deployment configs
├── notebooks/             # Development notebooks
└── docs/                  # Documentation
```

## 🎯 Contribution Areas

### High Priority
- 🌍 **French Language Support** for bilingual Ottawa services
- 📱 **Mobile Optimization** for Gradio interface
- 🔄 **Real-time Updates** with scheduled re-scraping
- ⚡ **Performance Optimization** for faster responses

### Medium Priority
- 🧪 **Test Coverage** expansion
- 📚 **Documentation** improvements
- 🐛 **Bug Fixes** and stability improvements
- 🎨 **UI/UX** enhancements

### Low Priority
- 🌟 **New Features** and integrations
- 🏙️ **Multi-city Support** (Toronto, Vancouver, etc.)
- 📊 **Analytics Dashboard**
- 🎤 **Voice Interface**

## 📋 Pull Request Process

### Before Submitting
1. **Update your fork**: `git pull upstream main`
2. **Run tests**: `pytest`
3. **Check code style**: `black . && flake8`
4. **Update documentation** if needed
5. **Write/update tests** for new features

### PR Guidelines
- **Clear title** describing the change
- **Detailed description** of what and why
- **Link related issues** using `Closes #123`
- **Include screenshots** for UI changes
- **Request review** from maintainers

### Review Process
- Maintainers will review within 48 hours
- Address feedback promptly
- Squash commits before merging
- Thank reviewers for their time

## 🌟 Recognition

Contributors will be:
- Listed in the Contributors section
- Mentioned in release notes
- Given credit in documentation
- Invited to join the core team (for regular contributors)

## 📞 Communication

### Getting Help
- 💬 **GitHub Discussions** for questions
- 🐛 **GitHub Issues** for bugs
- 📧 **Email** for sensitive matters

### Community Guidelines
- Be respectful and inclusive
- Help other contributors
- Give constructive feedback
- Celebrate successes together

## 🏷️ Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements to docs
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority-high` - Urgent fixes
- `priority-low` - Nice to have

## 🚀 Release Process

### Versioning
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

### Release Checklist
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag the release

## 📝 Development Notes

### Working with Data
- Never commit large datasets to Git
- Use `.gitignore` for local data files
- Provide sample data for testing
- Document data sources clearly

### Environment Variables
- Use `.env.example` as template
- Never commit API keys
- Document all required variables
- Use default values where possible

### Docker Development
```bash
# Build development image
docker build -t ottawa-rag-dev .

# Run with live reload
docker-compose -f docker-compose.dev.yml up
```

## 🎉 Thank You!

Every contribution, no matter how small, makes this project better for Ottawa residents and the open source community. We appreciate your time and effort! 

**Happy Coding!** 🚀

---

*For questions about contributing, please open a GitHub issue or start a discussion.*
