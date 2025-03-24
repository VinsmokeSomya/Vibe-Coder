import time  # Importing time module for tracking execution duration
import json  # Importing json module for handling JSON data
import os  # Importing os module for interacting with the operating system
from pathlib import Path  # Importing Path class for filesystem path manipulations
from typing import Dict, List, Optional, Tuple  # Importing typing for type hinting

import yaml  # Importing yaml module for handling YAML data

# Importing necessary classes from espada.benchmark.types
from espada.benchmark.types import Assertable, Benchmark, TaskResult
# Importing BaseAgent class from espada.core.base_agent
from espada.core.base_agent import BaseAgent
# Importing DiskExecutionEnv class from espada.core.default.disk_execution_env
from espada.core.default.disk_execution_env import DiskExecutionEnv

def run(
    agent: BaseAgent,  # The agent responsible for improving code
    benchmark: Benchmark,  # The benchmark containing tasks to run
    verbose=False,  # Flag to enable verbose output
) -> List[TaskResult]:  # Returns a list of TaskResult objects

    task_results = []  # Initialize an empty list to store task results
    for task in benchmark.tasks:  # Iterate over each task in the benchmark
        print(f"--> Running task: {task.name}\n")  # Print the name of the current task

        t0 = time.time()  # Record the start time
        # Use the agent to improve the initial code using the provided prompt
        files_dict = agent.improve(task.initial_code, task.prompt)
        t1 = time.time()  # Record the end time

        env = DiskExecutionEnv()  # Create a new disk execution environment
        env.upload(files_dict)  # Upload the improved files to the environment

        if task.command:  # If a command is specified for the task
            p = env.popen(task.command)  # Open a process to execute the command
            stdout, stderr = p.communicate(benchmark.timeout)  # Communicate with the process
            # Decode the standard output and error from bytes to string
            stdout, stderr = stdout.decode("utf-8"), stderr.decode("utf-8")
        else:
            p, stdout, stderr = None, None, None  # No process, stdout, or stderr if no command

        # Create an Assertable object to store execution results
        exec_result = Assertable(
            files=files_dict,
            env=env,
            process=p,
            stdout=stdout,
            stderr=stderr,
        )

        # Append the task result to the list
        task_results.append(
            TaskResult(
                task_name=task.name,
                # Evaluate assertions and store results
                assertion_results={
                    assertion_name: assertion(exec_result)
                    for assertion_name, assertion in task.assertions.items()
                },
                duration=t1 - t0,  # Calculate the duration of the task
            )
        )

        if verbose:  # If verbose output is enabled
            print_results(task_results)  # Print the results of the tasks
    return task_results  # Return the list of task results

def print_results(results: list[TaskResult]):  # Function to print task results

    for task_result in results:  # Iterate over each task result
        print(f"\n--- Results for {task_result.task_name} ---")  # Print task name
        print(f"{task_result.task_name} ({task_result.duration:.2f}s)")  # Print task duration
        for assertion_name, assertion_result in task_result.assertion_results.items():
            # Print each assertion result with a checkmark or cross
            checkmark = "✅" if assertion_result else "❌"
            print(f"  {checkmark} {assertion_name}")
        print()  # Print a newline for spacing

    # Calculate success rates for each task
    success_rates = [task_result.success_rate for task_result in results]
    avg_success_rate = sum(success_rates) / len(results)  # Calculate average success rate

    total_time = sum(task_result.duration for task_result in results)  # Calculate total execution time

    # Calculate the number of correct assertions
    correct_assertions = sum(
        sum(
            assertion_result
            for assertion_result in task_result.assertion_results.values()
        )
        for task_result in results
    )
    # Calculate the total number of assertions
    total_assertions = sum(
        len(task_result.assertion_results) for task_result in results
    )
    # Identify tasks with a 100% success rate
    correct_tasks = [
        task_result for task_result in results if task_result.success_rate == 1
    ]

    print("--- Results ---")  # Print results summary
    print(f"Total time: {total_time:.2f}s")  # Print total execution time
    print(f"Completely correct tasks: {len(correct_tasks)}/{len(results)}")  # Print number of completely correct tasks
    print(f"Total correct assertions: {correct_assertions}/{total_assertions}")  # Print number of correct assertions
    print(f"Average success rate: {avg_success_rate * 100}% on {len(results)} tasks")  # Print average success rate
    print("--- Results ---")  # End of results summary
    print()  # Print a newline for spacing

def export_yaml_results(yaml_path, complete_results, config):  # Function to export results to a YAML file
    for results in complete_results.values():  # Iterate over each set of results
        # Identify tasks that are fully solved
        correct_tasks = [
            task_result
            for task_result in results["detailed"]
            if task_result["solved"] == 1.0
        ]
        # Calculate the fraction of fully solved tasks
        fraction_correct = len(correct_tasks) / len(results["detailed"])
        results["fully_solved"] = fraction_correct  # Store the fraction in the results
    complete_results["config"] = config  # Add configuration to the results
    with open(yaml_path, "w") as f:  # Open the YAML file for writing
        yaml.dump(complete_results, f, indent=4)  # Dump the results into the file with indentation
