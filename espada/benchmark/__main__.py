import importlib  # Import the importlib module for dynamic imports
import os.path  # Import os.path for path manipulations
import sys  # Import sys to manipulate the Python runtime environment

from typing import Annotated, Optional  # Import typing for type annotations

import typer  # Import typer for building command-line interfaces

from langchain.globals import set_llm_cache  # Import function to set LLM cache
from langchain_community.cache import SQLiteCache  # Import SQLiteCache for caching

from espada.applications.cli.main import load_env_if_needed  # Import function to load environment variables
from espada.benchmark.bench_config import BenchConfig  # Import BenchConfig for benchmark configuration
from espada.benchmark.benchmarks.load import get_benchmark  # Import function to load benchmarks
from espada.benchmark.run import export_yaml_results, print_results, run  # Import functions for running benchmarks and exporting results

# Create a Typer app for the CLI with custom help option names
app = typer.Typer(
    context_settings={"help_option_names": ["-h", "--help"]}
)

def get_agent(path):
    # Dynamically import the Python module at the given path
    sys.path.append(os.path.dirname(path))  # Add the directory of the path to sys.path
    agent_module = importlib.import_module(path.replace("/", ".").replace(".py", ""))  # Import the module
    return agent_module.default_config_agent()  # Return the default agent configuration

# Define the main command for the Typer app
@app.command(
    help="""
        Run any benchmark(s) against the specified agent.

        \b
        Currently available benchmarks are: apps, mbpp, and espadar1
    """
)
def main(
    path_to_agent: Annotated[
        str,
        typer.Argument(
            help="python file that contains a function called 'default_config_agent'"
        ),
    ],
    bench_config: Annotated[
        str, typer.Argument(help="optional task name in benchmark")
    ] = os.path.join(os.path.dirname(__file__), "default_bench_config.toml"),  # Default path to the benchmark config
    yaml_output: Annotated[
        Optional[str],
        typer.Option(help="print results for each task", show_default=False),
    ] = None,  # Optional YAML output path
    verbose: Annotated[
        Optional[bool],
        typer.Option(help="print results for each task", show_default=False),
    ] = False,  # Verbose mode flag
    use_cache: Annotated[
        Optional[bool],
        typer.Option(
            help="Speeds up computations and saves tokens when running the same prompt multiple times by caching the LLM response.",
            show_default=False,
        ),
    ] = True,  # Use cache flag
):

    if use_cache:
        set_llm_cache(SQLiteCache(database_path=".langchain.db"))  # Set up LLM cache
    load_env_if_needed()  # Load environment variables if needed
    config = BenchConfig.from_toml(bench_config)  # Load benchmark configuration from TOML file
    print("using config file: " + bench_config)  # Print the config file being used
    benchmarks = list()  # Initialize list to store active benchmarks
    benchmark_results = dict()  # Initialize dictionary to store benchmark results
    for specific_config_name in vars(config):  # Iterate over each configuration in BenchConfig
        specific_config = getattr(config, specific_config_name)  # Get the specific configuration
        if hasattr(specific_config, "active"):  # Check if the configuration has an 'active' attribute
            if specific_config.active:  # Check if the benchmark is active
                benchmarks.append(specific_config_name)  # Add active benchmark to the list

    for benchmark_name in benchmarks:  # Iterate over each active benchmark
        benchmark = get_benchmark(benchmark_name, config)  # Load the benchmark
        if len(benchmark.tasks) == 0:  # Check if there are no tasks in the benchmark
            print(
                benchmark_name
                + " was skipped, since no tasks are specified. Increase the number of tasks in the config file at: "
                + bench_config
            )
            continue  # Skip to the next benchmark if no tasks are specified
        agent = get_agent(path_to_agent)  # Get the agent for the benchmark

        results = run(agent, benchmark, verbose=verbose)  # Run the benchmark with the agent
        print(
            f"\n--- Results for agent {path_to_agent}, benchmark: {benchmark_name} ---"
        )
        print_results(results)  # Print the results of the benchmark
        print()  # Print a newline for spacing
        benchmark_results[benchmark_name] = {
            "detailed": [result.to_dict() for result in results]  # Store detailed results
        }
    if yaml_output is not None:  # Check if YAML output is specified
        export_yaml_results(yaml_output, benchmark_results, config.to_dict())  # Export results to YAML

# Entry point for the script
if __name__ == "__main__":
    typer.run(main)  # Run the Typer app
