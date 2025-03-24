# How to Run Espada Project

This comprehensive guide will walk you through the process of setting up and running the Espada project step by step.

## Prerequisites

1. Python 3.10 or higher installed on your system
   - Check your Python version: `python --version`
   - Download Python from: https://www.python.org/downloads/
2. Git installed on your system
   - Check Git version: `git --version`
   - Download Git from: https://git-scm.com/downloads
3. OpenAI API key (get it from https://platform.openai.com/account/api-keys)
4. A text editor of your choice (VS Code recommended)

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/gpt-engineer-org/espada.git

# Navigate to the project directory
cd espada

# Verify you're in the correct directory
pwd  # Should show the path to espada directory
```

## Step 2: Install Poetry

Poetry is the dependency management tool used in this project. Install it using pip:

```bash
# For Windows:
python -m pip install poetry

# For Unix/MacOS:
curl -sSL https://install.python-poetry.org | python3 -
```

Verify the installation:
```bash
poetry --version
```

## Step 3: Install Project Dependencies

Using Poetry, install all the project dependencies:

```bash
# Install dependencies
poetry install

# Verify virtual environment
poetry env info
```

## Step 4: Set Up Environment Variables

1. Create a `.env` file in the project root directory:
```bash
cp .env.template .env
```

2. Edit the `.env` file and add your configuration:
```ini
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4  # or gpt-3.5-turbo
DEBUG_MODE=false
LOG_LEVEL=INFO
```

Replace `your_api_key_here` with your actual OpenAI API key from https://platform.openai.com/account/api-keys

## Step 5: Create a Test Project

1. Create a new directory for your project:
```bash
mkdir -p projects/my-project
```

2. Create a `prompt` file in your project directory:
```bash
# For Windows PowerShell:
New-Item -Path "projects/my-project/prompt" -ItemType File

# For Unix/MacOS:
touch projects/my-project/prompt
```

3. Add your requirements to the prompt file. Example:
```
Create a simple calculator application with a graphical user interface using Python and tkinter.
Requirements:
- Support basic arithmetic operations (addition, subtraction, multiplication, division)
- Clean, modern look with proper spacing
- Error handling for invalid inputs
- Memory function (M+, M-, MR, MC)
- Support for decimal numbers
- Clear button (C) and all-clear button (AC)
```

## Step 6: Run the Project

You can run the project in multiple ways:

### Method 1: Create New Code
```bash
# Basic usage
poetry run espada projects/my-project --model gpt-4

# With custom temperature (0.0 to 1.0)
poetry run espada projects/my-project --model gpt-4 --temperature 0.7

# With maximum tokens
poetry run espada projects/my-project --model gpt-4 --max-tokens 4000
```

### Method 2: Improve Existing Code
```bash
# Basic improvement mode
poetry run espada projects/my-project --model gpt-4 -i

# With specific file focus
poetry run espada projects/my-project --model gpt-4 -i --files "src/*.py"
```

### Method 3: Vision-based Code Generation
```bash
# Using vision capabilities
poetry run espada projects/my-project --model gpt-4-vision-preview \
    --prompt_file prompt/text \
    --image_directory prompt/images -i
```

## Common Issues and Solutions

1. **Dependency Issues**
   - Clear Poetry cache:
     ```bash
     poetry cache clear . --all
     ```
   - Update dependencies:
     ```bash
     poetry update
     ```
   - Rebuild virtual environment:
     ```bash
     poetry env remove python
     poetry install
     ```

2. **API Key Issues**
   - Make sure your `.env` file is in the project root directory
   - Verify that your API key is correctly formatted
   - Ensure there are no spaces or quotes around the API key
   - Check API key permissions on OpenAI dashboard
   - Verify billing status on OpenAI account

3. **Model Issues**
   - Supported models:
     - gpt-4 (recommended)
     - gpt-3.5-turbo (faster, less expensive)
     - gpt-4-vision-preview (for image inputs)
   - Common model errors:
     - Rate limiting: Wait a few seconds and retry
     - Token limit exceeded: Reduce prompt size or use a model with higher token limit
     - Invalid API key: Double-check API key in .env file

4. **Python Version Conflicts**
   - Use pyenv to manage multiple Python versions
   - Ensure Poetry is using the correct Python version:
     ```bash
     poetry env use python3.10
     ```

## Additional Options

1. Custom Pre-prompts:
```bash
poetry run espada projects/my-project --model gpt-4 --use-custom-preprompts
```

2. Vision Capabilities:
```bash
poetry run espada projects/my-project --model gpt-4-vision-preview \
    --prompt_file prompt/text \
    --image_directory prompt/images -i
```

3. Debug Mode:
```bash
poetry run espada projects/my-project --model gpt-4 --debug
```

## Project Structure

```
espada/
├── projects/           # Your project directories
│   └── my-project/    # Example project
│       ├── prompt     # Project requirements
│       ├── src/       # Generated source code
│       └── tests/     # Generated tests
├── .env              # Environment variables
├── poetry.lock       # Dependency lock file
└── pyproject.toml    # Project configuration
```

## Notes

- The project requires Python 3.10 or higher
- Make sure you have sufficient OpenAI API credits
- The generated code will be in your project directory
- You can modify the prompt file at any time to change requirements
- Keep prompts clear, specific, and well-structured
- Regular backups of your projects are recommended
- Check the logs directory for debugging information

## Performance Tips

1. Use specific and clear prompts
2. Start with small projects to understand the workflow
3. Use appropriate model temperature for your needs
4. Monitor API usage to optimize costs
5. Keep project files organized and clean 