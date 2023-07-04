"""Optional 3D renderer based on Open3D's visualizer."""
from ..compatibility import (
    opend3d_module,
    import_optional_dependency,
    OptionalImportErrorHandling,
)

if import_optional_dependency(opend3d_module, error_handling=OptionalImportErrorHandling.RAISE):
    import open3d as o3d
    from ._artists import (Artist, Line3D, PointCollection3D, Vector3D, Frame,
                           Trajectory, Camera, Box, Sphere, Cylinder, Mesh,
                           Ellipsoid, Capsule, Cone, Plane, Graph)
    from ._figure import figure, Figure

    __all__ = ["figure", "Figure", "Artist", "Line3D", "PointCollection3D",
               "Vector3D", "Frame", "Trajectory", "Camera", "Box", "Sphere",
               "Cylinder", "Mesh", "Ellipsoid", "Capsule", "Cone", "Plane",
               "Graph"]
