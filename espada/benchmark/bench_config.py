# Import necessary modules and classes
from dataclasses import dataclass, field
from pathlib import Path

# Import Integer type from tomlkit for handling integer values in TOML files
from tomlkit.items import Integer

# Import the read_config function from the project_config module
from espada.core.project_config import read_config

# Define a dataclass for AppsConfig
@dataclass
class AppsConfig:
    # Whether the apps benchmark is active
    active: bool | None = True
    # Start index for test data
    test_start_index: int | None = 0
    # End index for test data
    test_end_index: int | None = 1
    # Start index for training data
    train_start_index: int | None = 0
    # End index for training data
    train_end_index: int | None = 0
    # Number of examples per problem
    examples_per_problem: int | None = 10

# Define a dataclass for MbppConfig
@dataclass
class MbppConfig:
    # Whether the mbpp benchmark is active
    active: bool | None = True
    # Length of test data
    test_len: int | None = 1
    # Length of training data
    train_len: int | None = 0

# Define a dataclass for Espadar1Config
@dataclass
class Espadar1Config:
    # Whether the espadar1 benchmark is active
    active: bool | None = True

# Define a dataclass for BenchConfig
@dataclass
class BenchConfig:
    # Configuration for apps benchmark
    apps: AppsConfig = field(default_factory=AppsConfig)
    # Configuration for mbpp benchmark
    mbpp: MbppConfig = field(default_factory=MbppConfig)
    # Configuration for espadar1 benchmark
    espadar1: Espadar1Config = field(default_factory=Espadar1Config)

    # Class method to create BenchConfig from a TOML file
    @classmethod
    def from_toml(cls, config_file: Path | str):
        # Convert string path to Path object if necessary
        if isinstance(config_file, str):
            config_file = Path(config_file)
        # Read configuration from the TOML file
        config_dict = read_config(config_file)
        # Create BenchConfig from the dictionary
        return cls.from_dict(config_dict)

    # Class method to create BenchConfig from a dictionary
    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(
            # Create AppsConfig from the dictionary
            apps=AppsConfig(**config_dict.get("apps", {})),
            # Create MbppConfig from the dictionary
            mbpp=MbppConfig(**config_dict.get("mbpp", {})),
            # Create Espadar1Config from the dictionary
            espadar1=Espadar1Config(**config_dict.get("espadar1", {})),
        )

    # Static method to resolve Integer types in a dictionary
    @staticmethod
    def recursive_resolve(data_dict):
        for key, value in data_dict.items():
            # Convert Integer to int
            if isinstance(value, Integer):
                data_dict[key] = int(value)
            # Recursively resolve nested dictionaries
            elif isinstance(value, dict):
                BenchConfig.recursive_resolve(value)

    # Method to convert BenchConfig to a dictionary
    def to_dict(self):
        dict_config = {
            # Convert each benchmark configuration to a dictionary
            benchmark_name: {key: val for key, val in spec_config.__dict__.items()}
            for benchmark_name, spec_config in self.__dict__.items()
        }
        # Resolve any Integer types in the dictionary
        BenchConfig.recursive_resolve(dict_config)

        return dict_config
