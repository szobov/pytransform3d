from __future__ import __annotations__

import enum
import types
import importlib
import warnings
import packaging.version
from typing import Optional, Dict, Tuple
import dataclasses

PACKAGE_NAME = __name__.split(".")[0]


def _parse_version(version_string: Optional[str]) -> packaging.version.Version:
    version = packaging.version.Version("")
    if version_string is not None:
        try:
            version = packaging.version.parse(version_string)
        except packaging.version.InvalidVersion:
            return version
    return version


@dataclasses.dataclass(frozen=True)
class PythonDependency:
    install_name: str
    _: dataclasses.KW_ONLY

    _min_version: dataclasses.InitVar[Optional[str]] = None
    min_version: packaging.version.Version = dataclasses.field(init=False)

    _import_name: dataclasses.InitVar[Optional[str]] = None
    import_name: str = dataclasses.field(init=False)

    is_installed: bool = dataclasses.field(init=False, default=False)
    is_old: bool = dataclasses.field(init=False, default=False)
    module: Optional[types.ModuleType] = dataclasses.field(init=False, default=None)
    version: packaging.version.Version = dataclasses.field(
        init=False, default=packaging.version.Version("")
    )
    missing_error_message: str = dataclasses.field(init=False, default="")
    too_old_error_message: str = dataclasses.field(init=False, default="")

    def __post_init__(self, _import_name: Optional[str], _min_version: Optional[str]):
        import_name = _import_name
        if import_name is None:
            import_name = self.install_name
        object.__setattr__(self, "import_name", import_name)

        module: Optional[types.ModuleType]

        try:
            module = importlib.import_module(self.import_name)
        except ImportError:
            module = None

        if module is not None:
            object.__setattr__(self, "is_installed", True)
        object.__setattr__(self, "module", module)

        object.__setattr__(
            self,
            "missing_error_message",
            f"Missing optional dependency '{self.install_name}' for {PACKAGE_NAME}. "
            f"Use pip or conda to install {self.install_name}.",
        )

        object.__setattr__(
            self, "version", _parse_version(getattr(self.module, "__version__", None))
        )
        object.__setattr__(self, "min_version", _parse_version(_min_version))

        if self.version < self.min_version:
            object.__setattr__(self, "is_old", True)
            object.__setattr__(
                self,
                "too_old_error_message",
                f"{PACKAGE_NAME} requires version '{str(self.min_version)}' of "
                f"{self.install_name}. Use pip or conda to install "
                f"{self.install_name}=={str(self.min_version)}. "
                f"(version '{self.version}' is currently installed)",
            )


@enum.unique
class OptionalImportErrorHandling(enum.Enum):
    RAISE = enum.auto()
    WARN = enum.auto()
    IGNORE = enum.auto()


def import_optional_dependency(
    module: PythonDependency, *, error_handling: OptionalImportErrorHandling
) -> Optional[types.ModuleType]:
    message = module.missing_error_message
    if module.is_old:
        message = module.too_old_error_message
    if not module.is_installed or module.is_old:
        if error_handling.RAISE:
            raise ImportError(message)
        if error_handling.WARN:
            warnings.warn(message, UserWarning)
            return None
        if error_handling.IGNORE:
            return None
    return module.module


matplotlib_module = PythonDependency("matplotlib")
trimesh_module = PythonDependency("trimesh")
beatifulsoap4_module = PythonDependency("beautifulsoup4", _import_name="bs4")
lxml_module = PythonDependency("lxml")
opend3d_module = PythonDependency("open3d")
scipy_module = PythonDependency("scipy")
pydot_module = PythonDependency("pydot")
numpydoc_module = PythonDependency("numpydoc_module")
sphinx_module = PythonDependency("sphinx_module")
sphinx_gallery_module = PythonDependency("sphinx-gallery")
sphinx_bootstrap_theme_module = PythonDependency("sphinx-bootstrap-theme")
pytest_module = PythonDependency("pytest")
pytest_cov_module = PythonDependency("pytest-cov")
pyqt4_module = PythonDependency("PyQt4")
pyqt5_module = PythonDependency("PyQt5")


_optional_dependencies = {
    "plotting_2d": (matplotlib_module,),
    "plotting_3d": (trimesh_module,),
    "editor": (pyqt5_module, matplotlib_module),
    "urdf": (beatifulsoap4_module, lxml_module),
    "rendering": (opend3d_module,),
    "transform_manager": (scipy_module,),
    "graph_visualization": (pydot_module,),
    "documentation": (
        numpydoc_module,
        sphinx_module,
        sphinx_gallery_module,
        sphinx_bootstrap_theme_module,
    ),
    "tests": (pytest_module, pytest_cov_module),
}


def get_optional_dependencies_for_setup_py() -> Dict[str, Tuple[str, ...]]:
    return {
        key: tuple(map(lambda item: item.install_name, val))
        for key, val in _optional_dependencies.items()
    }
