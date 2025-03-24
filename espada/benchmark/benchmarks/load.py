from espada.benchmark.bench_config import BenchConfig  # Import BenchConfig class from bench_config module
from espada.benchmark.benchmarks.apps.load import load_apps  # Import load_apps function from apps.load module
from espada.benchmark.benchmarks.espadar1.load import load_espadar1  # Import load_espadar1 function from espadar1.load module
from espada.benchmark.benchmarks.mbpp.load import load_mbpp  # Import load_mbpp function from mbpp.load module
from espada.benchmark.types import Benchmark  # Import Benchmark type from types module

# Dictionary mapping benchmark names to their respective load functions
BENCHMARKS = {
    "espadar1": load_espadar1,  # Mapping for espadar1 benchmark
    "apps": load_apps,  # Mapping for apps benchmark
    "mbpp": load_mbpp,  # Mapping for mbpp benchmark
}

# Function to get the benchmark based on the name and configuration
def get_benchmark(name: str, config: BenchConfig) -> Benchmark:
    # Check if the benchmark name is in the BENCHMARKS dictionary
    if name not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark {name}.")  # Raise an error if the benchmark name is unknown
    # Return the benchmark by calling the corresponding load function with the specific configuration
    return BENCHMARKS[name](config.__getattribute__(name))
