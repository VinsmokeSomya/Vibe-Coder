# Contributing to Vibe-Coder

First off, thank you for considering contributing to Vibe-Coder! It's people like you that make Vibe-Coder such a great tool.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:

- Be respectful and inclusive
- Use welcoming and inclusive language
- Be collaborative and supportive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

1. **Use a clear and descriptive title**
2. **Describe the exact steps to reproduce the problem**
3. **Provide specific examples** to demonstrate the steps
4. Include:
   - Your Python version (`python --version`)
   - Your OS and version
   - Package versions (`poetry show`)
   - Error messages and logs
   - Code samples that demonstrate the issue

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

1. **Use a clear and descriptive title**
2. **Provide a detailed description of the proposed enhancement**
3. **Explain why this enhancement would be useful**
4. **List any alternatives you've considered**
5. **Include mockups or examples** if applicable

### Pull Requests

1. **Fork the Repository**
   ```bash
   git clone https://github.com/VinsmokeSomya/Vibe-Coder.git
   cd Vibe-Coder
   git remote add upstream https://github.com/VinsmokeSomya/Vibe-Coder.git
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-number
   ```

3. **Make Your Changes**
   - Follow the coding style of the project
   - Write descriptive commit messages
   - Keep your changes focused and atomic
   - Add tests for new features
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Run tests
   poetry run pytest
   
   # Run linting
   poetry run flake8
   poetry run black .
   poetry run isort .
   ```

5. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a Pull Request**
   - Fill in the pull request template
   - Reference any relevant issues
   - Include screenshots or animated GIFs if relevant

## Development Setup

1. **Install Dependencies**
   ```bash
   poetry install
   ```

2. **Set Up Pre-commit Hooks**
   ```bash
   poetry run pre-commit install
   ```

3. **Create Environment File**
   ```bash
   cp .env.template .env
   # Edit .env with your settings
   ```

## Coding Guidelines

### Python Style Guide

- Follow PEP 8 guidelines
- Use type hints for function arguments and return values
- Keep functions focused and under 50 lines
- Write docstrings for all public functions and classes
- Use descriptive variable names

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests liberally after the first line

Example:
```
Add support for GPT-4 vision model

- Implement vision model integration
- Add image processing utilities
- Update documentation with vision examples

Fixes #123
```

### Documentation

- Update README.md if changing user-facing features
- Add docstrings to all new functions and classes
- Update HOW_TO_RUN.md for new features or changed behavior
- Include examples in docstrings

### Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Include integration tests for complex features
- Aim for high test coverage

## Project Structure

When adding new features, follow the existing project structure:

```
vibe-coder/
├── applications/     # Application-specific code
├── core/            # Core functionality
├── memory/          # Memory management
├── execution/       # Code execution
└── templates/       # Project templates
```

## Release Process

1. Version numbers follow semantic versioning (MAJOR.MINOR.PATCH)
2. Update CHANGELOG.md with changes
3. Create a new release on GitHub
4. Update documentation with new version

## Questions?

Feel free to ask for help! You can:

- Open an issue with your question
- Join our Discord community
- Contact the maintainers directly

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License. 