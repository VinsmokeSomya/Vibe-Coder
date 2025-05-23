from dataclasses import asdict, dataclass, field
from pathlib import Path

import tomlkit

default_config_filename = "espada.toml"

example_config = """
[run]
build = "npm run build"
test = "npm run test"
lint = "quick-lint-js"

[paths]
base = "./frontend"  # base directory to operate in (for monorepos)
src = "./src"        # source directory (under the base directory) from which context will be retrieved

[espadar1-app]  # this namespace is used for espadar1.app, may be used for internal experiments
project_id = "..."

]
"""


@dataclass
class _PathsConfig:
    base: str | None = None
    src: str | None = None


@dataclass
class _RunConfig:
    build: str | None = None
    test: str | None = None
    lint: str | None = None
    format: str | None = None


@dataclass
class _OpenApiConfig:
    url: str


@dataclass
class _EspadaAppConfig:
    project_id: str
    openapi: list[_OpenApiConfig] | None = None


def filter_none(d: dict) -> dict:
    # Drop None values and empty dictionaries from a dictionary
    return {
        k: v
        for k, v in (
            (k, filter_none(v) if isinstance(v, dict) else v)
            for k, v in d.items()
            if v is not None
        )
        if not (isinstance(v, dict) and not v)  # Check for non-empty after filtering
    }


@dataclass
class Config:
    """Configuration for the Espada CLI via `espada.toml`."""

    paths: _PathsConfig = field(default_factory=_PathsConfig)
    run: _RunConfig = field(default_factory=_RunConfig)
    espada_app: _EspadaAppConfig | None = None

    @classmethod
    def from_toml(cls, config_file: Path | str):
        if isinstance(config_file, str):
            config_file = Path(config_file)
        config_dict = read_config(config_file)
        return cls.from_dict(config_dict)

    @classmethod
    def from_dict(cls, config_dict: dict):
        run = _RunConfig(**config_dict.get("run", {}))
        paths = _PathsConfig(**config_dict.get("paths", {}))

        # load optional espada-app section
        espada_app_dict = config_dict.get("espada-app", {})
        espada_app = None
        if espada_app_dict:
            assert (
                "project_id" in espada_app_dict
            ), "project_id is required in espada-app section"
            espada_app = _EspadaAppConfig(
                # required if espada-app section is present
                project_id=espada_app_dict["project_id"],
                openapi=[
                    _OpenApiConfig(**openapi)
                    for openapi in espada_app_dict.get("openapi", [])
                ]
                or None,
            )

        return cls(paths=paths, run=run, espada_app=espada_app)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["espada-app"] = d.pop("espada_app", None)

        # Drop None values and empty dictionaries
        # Needed because tomlkit.dumps() doesn't handle None values,
        # and we don't want to write empty sections.
        d = filter_none(d)

        return d

    def to_toml(self, config_file: Path | str, save=True) -> str:
        """Write the configuration to a TOML file."""
        if isinstance(config_file, str):
            config_file = Path(config_file)

        # Load the TOMLDocument and overwrite it with the new values
        config = read_config(config_file)
        default_config = Config().to_dict()
        for k, v in self.to_dict().items():
            # only write values that are already explicitly set, or that differ from defaults
            if k in config or v != default_config[k]:
                if isinstance(v, dict):
                    config[k] = {
                        k2: v2
                        for k2, v2 in v.items()
                        if (
                            k2 in config[k]
                            or default_config.get(k) is None
                            or v2 != default_config[k].get(k2)
                        )
                    }
                else:
                    config[k] = v

        toml_str = tomlkit.dumps(config)
        if save:
            with open(config_file, "w") as f:
                f.write(toml_str)

        return toml_str


def read_config(config_file: Path) -> tomlkit.TOMLDocument:
    """Read the configuration file"""
    assert config_file.exists(), f"Config file {config_file} does not exist"
    with open(config_file, "r") as f:
        return tomlkit.load(f)
