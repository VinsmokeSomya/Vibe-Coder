# Espada - AI-Powered Code Generation Tool

A powerful and flexible AI code generation tool that helps developers create, modify, and improve code using advanced language models. Espada streamlines the development process by leveraging AI to generate high-quality, maintainable code based on natural language descriptions.

## 🌟 Features

- **Interactive CLI Interface**: 
  - User-friendly command-line interface for code generation
  - Real-time feedback and progress indicators
  - Customizable output formatting
  
- **Multiple Model Support**: 
  - Works with various AI models including GPT-4, Claude
  - Flexible model switching for different tasks
  - Optimized prompts for each model type
  
- **File Selection**: 
  - Smart file selection system with glob pattern support
  - Intelligent context gathering from related files
  - Customizable file inclusion/exclusion patterns
  
- **Learning System**: 
  - Built-in learning capabilities to improve code generation over time
  - Feedback incorporation for better results
  - Historical pattern recognition
  
- **Project Management**: 
  - Efficient project organization and metadata management
  - Version control integration
  - Project templates and scaffolding

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher (3.12 recommended)
- Poetry for dependency management
- OpenAI API key or Anthropic API key
- Git version 2.25 or higher
- 4GB RAM minimum (8GB recommended)
- Internet connection for API access

### Installation

1. Clone the repository:
```bash
git clone https://github.com/VinsmokeSomya/Vibe-Coder.git
cd Vibe-Coder
```

2. Install dependencies using Poetry:
```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -
```

```bash
# Install project dependencies
poetry install
```

```bash
# Verify installation
poetry run python -c "import espada; print(espada.__version__)"
```

3. Set up your environment variables:
```bash
# Create environment file
cp .env.template .env
```

```bash
# Edit .env with your configuration
OPENAI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here  # Optional
MODEL_NAME=gpt-4
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Usage

1. Create a new project:
```bash
# Basic project creation
poetry run espada projects/your-project
```

2. Run with specific model:
```bash
# Using GPT-4
poetry run espada projects/your-project --model gpt-4
```

```bash
# Using Claude
poetry run espada projects/your-project --model claude-2
```

## 📁 Project Structure

```
espada/
├── applications/        # Application-specific code
│   ├── cli/           # CLI implementation
│   └── api/           # API endpoints
├── core/              # Core functionality
│   ├── models/        # AI model integrations
│   ├── generators/    # Code generation logic
│   └── utils/         # Utility functions
├── memory/            # Memory management
│   ├── cache/         # Caching system
│   └── history/       # Historical data
├── execution/         # Code execution environment
│   ├── runners/       # Code runners
│   └── sandbox/       # Isolated execution
└── templates/         # Project templates
```

## 🔧 Configuration

The project can be configured through:

### Environment Variables (.env)
- `OPENAI_API_KEY`: Your OpenAI API key
- `MODEL_NAME`: Default model to use
- `DEBUG_MODE`: Enable debug logging
- `LOG_LEVEL`: Logging verbosity



### Command Line Arguments
- `--model`: Override model selection
- `--temperature`: Adjust generation temperature
- `--max-tokens`: Set token limit
- `--debug`: Enable debug mode

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and development process.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models and API
- Anthropic for Claude models
- The open-source community
- All contributors and maintainers

## 📫 Contact & Support

- GitHub Issues: [Report a bug](https://github.com/VinsmokeSomya/Vibe-Coder/issues)
- Documentation: [Coming soon...]()


## 🚀 Future Plans

- Enhanced model support
- Web interface
- Cloud deployment options
- Collaborative features
- Advanced code analysis
