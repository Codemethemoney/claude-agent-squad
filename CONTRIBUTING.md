# 🤝 Contributing to Claude Agent Squad

Thank you for your interest in contributing to Claude Agent Squad! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Contributions](#making-contributions)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## 📜 Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Please read and adhere to it in all interactions within the project.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-agent-squad.git
   cd claude-agent-squad
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/Codemethemoney/claude-agent-squad.git
   ```

## 💻 Development Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## 🔧 Making Contributions

### Types of Contributions

- **Bug Fixes**: Fix issues in existing code
- **Features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code

### Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests and linting**:
   ```bash
   pytest
   black .
   flake8 .
   mypy .
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```
   
   Follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes
   - `refactor:` Code refactoring
   - `test:` Test additions/changes
   - `chore:` Maintenance tasks

## 📐 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting
- Maximum line length: 88 characters
- Use type hints where appropriate

### Code Quality

- Write self-documenting code
- Add docstrings to all functions, classes, and modules
- Keep functions small and focused
- Use meaningful variable names

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use pytest for testing
- Mock external dependencies

## 📚 Documentation

### Documentation Standards

- Update README.md for user-facing changes
- Add docstrings to all public APIs
- Include usage examples in docstrings
- Update CHANGELOG.md for all changes

## 📤 Submitting Changes

### Pull Request Process

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create Pull Request**:
   - Go to GitHub and create a PR from your branch
   - Fill out the PR template completely
   - Link any related issues

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Changelog is updated
- [ ] PR description is clear
- [ ] Related issues are linked

## 🎉 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

## ❓ Getting Help

- **Issues**: Open a GitHub issue
- **Discussions**: Use GitHub Discussions

## 🔗 Useful Links

- [Project Documentation](https://github.com/Codemethemoney/claude-agent-squad/wiki)
- [Issue Tracker](https://github.com/Codemethemoney/claude-agent-squad/issues)

Thank you for contributing to Claude Agent Squad! 🚀