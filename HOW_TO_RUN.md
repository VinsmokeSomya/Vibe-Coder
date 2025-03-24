# How to Run Espada Project

This guide will walk you through the process of setting up and running the Espada project step by step.

## Prerequisites

1. Python 3.10 or higher installed on your system
2. Git installed on your system
3. OpenAI API key (get it from https://platform.openai.com/account/api-keys)

## Step 1: Clone the Repository

```bash
git clone https://github.com/gpt-engineer-org/espada.git
cd espada
```

## Step 2: Install Poetry

Poetry is the dependency management tool used in this project. Install it using pip:

```bash
python -m pip install poetry
```

## Step 3: Install Project Dependencies

Using Poetry, install all the project dependencies:

```bash
poetry install
```

## Step 4: Set Up Environment Variables

1. Create a `.env` file in the project root directory:
```bash
cp .env.template .env
```

2. Edit the `.env` file and add your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual OpenAI API key from https://platform.openai.com/account/api-keys

## Step 5: Create a Test Project

1. Create a new directory for your project:
```bash
mkdir projects/my-project
```

2. Create a `prompt` file (no extension) in your project directory with your requirements:
```bash
echo "Create a simple calculator application with a graphical user interface using Python and tkinter. The calculator should support basic arithmetic operations (addition, subtraction, multiplication, division) and have a clean, modern look." > projects/my-project/prompt
```

## Step 6: Run the Project

You can run the project in two ways:

### Method 1: Create New Code
```bash
poetry run espada projects/my-project --model gpt-4
```

### Method 2: Improve Existing Code
```bash
poetry run espada projects/my-project --model gpt-4 -i
```

## Common Issues and Solutions

1. **Dependency Issues**
   - If you encounter dependency conflicts, try:
   ```bash
   poetry update
   ```

2. **API Key Issues**
   - Make sure your `.env` file is in the project root directory
   - Verify that your API key is correctly formatted
   - Ensure there are no spaces around the API key in the `.env` file

3. **Model Issues**
   - The project supports various models including:
     - gpt-4
     - gpt-3.5-turbo
     - gpt-4-vision-preview (for image inputs)

## Additional Options

- To use custom pre-prompts:
```bash
poetry run espada projects/my-project --model gpt-4 --use-custom-preprompts
```

- To use vision capabilities:
```bash
poetry run espada projects/my-project gpt-4-vision-preview --prompt_file prompt/text --image_directory prompt/images -i
```

## Project Structure

```
espada/
├── projects/           # Your project directories
│   └── my-project/    # Example project
│       └── prompt     # Project requirements
├── .env              # Environment variables
├── poetry.lock       # Dependency lock file
└── pyproject.toml    # Project configuration
```

## Notes

- The project requires Python 3.10 or higher
- Make sure you have sufficient OpenAI API credits
- The generated code will be in your project directory
- You can modify the prompt file at any time to change requirements 