# Espada - AI-Powered Code Generation Tool

A powerful and flexible AI code generation tool that helps developers create, modify, and improve code using advanced language models.

## 🌟 Features

- **Interactive CLI Interface**: User-friendly command-line interface for code generation
- **Multiple Model Support**: Works with various AI models including GPT-4, Claude, and vision models
- **File Selection**: Smart file selection system with glob pattern support
- **Learning System**: Built-in learning capabilities to improve code generation over time
- **Project Management**: Efficient project organization and metadata management
- **Vision Integration**: Support for image-based code generation and analysis
- **Extensible Architecture**: Modular design for easy extension and customization

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Poetry for dependency management
- OpenAI API key or Anthropic API key

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/espada.git
cd espada
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Usage

1. Create a new project:
```bash
poetry run python -m espada.applications.cli.main projects/your-project
```

2. Run with specific model:
```bash
poetry run python -m espada.applications.cli.main projects/your-project --model gpt-4
```

3. Use vision capabilities:
```bash
poetry run python -m espada.applications.cli.main projects/your-project --model gpt-4-vision-preview --image_directory images
```

## 📁 Project Structure

```
espada/
├── applications/        # Application-specific code
│   └── cli/           # CLI implementation
├── core/              # Core functionality
├── memory/            # Memory management
└── execution/         # Code execution environment
```

## 🔧 Configuration

The project can be configured through:
- Environment variables in `.env`
- Project-specific configuration files
- Command-line arguments

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- All contributors and maintainers

## 📫 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - email@example.com

Project Link: [https://github.com/yourusername/espada](https://github.com/yourusername/espada)
