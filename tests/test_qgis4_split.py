"""Run with QGIS 4 Python: python tests/test_qgis4_split.py."""

from collections import Counter
import hashlib
import importlib
import importlib.util
import os
from pathlib import Path
import struct
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import numpy as np
from osgeo import gdal
from qgis.core import Qgis, QgsApplication
from qgis.PyQt.QtCore import QT_VERSION_STR

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "demto3d_qgis4_test"
spec = importlib.util.spec_from_file_location(
    PACKAGE, ROOT / "__init__.py", submodule_search_locations=[str(ROOT)]
)
package = importlib.util.module_from_spec(spec)
sys.modules[PACKAGE] = package
spec.loader.exec_module(package)
STL = importlib.import_module(PACKAGE + ".model_builder.STL_Builder").STL
Model = importlib.import_module(PACKAGE + ".model_builder.Model_Builder").Model


def read_binary(path):
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    assert len(data) == 84 + count * 50
    return np.array([
        struct.unpack_from("<12fH", data, 84 + i * 50)[:12]
        for i in range(count)
    ])



def read_ascii(path):
    lines = path.read_text(encoding="ascii").splitlines()
    assert lines[0] == "solid model" and lines[-1] == "endsolid model"
    assert (len(lines) - 2) % 7 == 0
    faces = []
    for i in range(1, len(lines) - 1, 7):
        assert lines[i + 1].strip() == "outer loop"
        assert lines[i + 5].strip() == "endloop"
        assert lines[i + 6].strip() == "endfacet"
        values = lines[i].split()[2:]
        for vertex in lines[i + 2:i + 5]:
            assert vertex.split()[0] == "vertex"
            values += vertex.split()[1:]
        faces.append([float(v) for v in values])
    return np.array(faces)



class SplitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="demto3d4-tests-")
        self.addCleanup(self.tmp.cleanup)
        self.directory = Path(self.tmp.name)
        self.matrix = self.to_grid([
            [[x, y, 3 + x * 0.13 + y * 0.07] for x in (0, 10, 20)]
            for y in (20, 10, 0)
        ])
        self.params = dict(
            divideCols=1, divideRow=1, width=20, height=20,
            spacing_mm=10, has_borders=True, borders=0,
        )

    @staticmethod
    def to_grid(values):
        return [[STL.pto(*point) for point in row] for row in values]

    @staticmethod
    def build_mesh(width, height, spacing):
        gdal.UseExceptions()
        dataset = gdal.GetDriverByName("MEM").Create("", 8, 8, 1, gdal.GDT_Float32)
        dataset.SetGeoTransform((0, 1000, 0, 5000, 0, -1000))
        dataset.GetRasterBand(1).Fill(3)
        model = Model(dict(
            baseModel=2, crs_map=None, crs_layer=None,
            roi_rect_Param=dict(rotation=0, width=width),
        ))
        return model.matrix_dem_builder(
            dataset, height, width, 1000, spacing, width, 0, 0, 0, 1, True
        )

    @staticmethod
    def mesh_volume(triangles):
        return np.einsum(
            "ij,ij->i", triangles[:, 0], np.cross(triangles[:, 1], triangles[:, 2])
        ).sum() / 6


    def assert_exact_tiles(self, matrix, width, height, columns, rows, output_format):
        params = dict(
            width=width, height=height, spacing_mm=10,
            divideCols=columns, divideRow=rows, has_borders=True, borders=0,
            stl_format=output_format,
        )
        builder = STL(params, str(self.directory / "tiles.stl"), matrix)
        builder.run()
        reader = read_ascii if output_format == "ascii" else read_binary
        triangles = [
            reader(Path(path))[:, 3:12].reshape((-1, 3, 3))
            for path in builder.output_files
        ]
        self.assertEqual(len(triangles), columns * rows)
        points = [faces.reshape((-1, 3)) for faces in triangles]
        lower = [part.min(axis=0) for part in points]
        upper = [part.max(axis=0) for part in points]
        tolerance = max(width, height) * np.finfo(np.float32).eps * 2
        if output_format == "ascii":
            tolerance = 1e-11
        for i in range(rows):
            for j in range(columns):
                index = i * columns + j
                np.testing.assert_allclose(
                    lower[index][:2], [width * j / columns, height * (rows - i - 1) / rows],
                    rtol=0, atol=tolerance,
                )
                np.testing.assert_allclose(
                    upper[index][:2], [width * (j + 1) / columns, height * (rows - i) / rows],
                    rtol=0, atol=tolerance,
                )
                # Every triangle edge of the closed solid must have exactly two faces.
                edges = Counter(
                    tuple(sorted((tuple(face[a]), tuple(face[b]))))
                    for face in triangles[index] for a, b in ((0, 1), (1, 2), (2, 0))
                )
                invalid = [(edge, count) for edge, count in edges.items() if count != 2]
                self.assertFalse(invalid, invalid[:3])
                for neighbor, axis, limit in (
                    (index + 1, 0, upper[index][0]),
                    (index + columns, 1, lower[index][1]),
                ):
                    if (axis == 0 and j + 1 == columns) or (axis == 1 and i + 1 == rows):
                        continue
                    first = points[index][points[index][:, axis] == limit]
                    second = points[neighbor][points[neighbor][:, axis] == limit]
                    np.testing.assert_array_equal(
                        np.unique(first, axis=0), np.unique(second, axis=0)
                    )

        # Cutting must conserve the original triangulated terrain's volume.
        source = self.directory / "whole.stl"
        STL(dict(params, divideCols=1, divideRow=1), str(source), matrix).run()
        expected_volume = self.mesh_volume(reader(source)[:, 3:12].reshape((-1, 3, 3)))
        actual_volume = sum(self.mesh_volume(faces) for faces in triangles)
        self.assertAlmostEqual(
            actual_volume, expected_volume,
            delta=max(abs(expected_volume) * (5e-7 if output_format == "binary" else 1e-12), 1e-9),
        )
        return np.concatenate(points)


    def test_qgis4_qt6_runtime(self):
        self.assertGreaterEqual(Qgis.QGIS_VERSION_INT, 40000)
        self.assertTrue(QT_VERSION_STR.startswith("6."))

    def test_model_respects_requested_spacing(self):
        for spacing in (0.2, 0.5, 0.75, 1):
            with self.subTest(spacing=spacing):
                matrix = self.build_mesh(2, 1, spacing)
                self.assertEqual(matrix[0][1].x - matrix[0][0].x, spacing)
                self.assertEqual(matrix[-1][-1].x, 2)
                self.assertEqual(matrix[0][0].y, 1)
                self.assertEqual(matrix[-1][0].y, 0)

    def test_unsplit_binary_remains_byte_identical(self):
        # Captured from qgis-4.x commit 376a4e9 before the geometry fix.
        for border, digest in (
            (0, "aea414117e4d1c51e01d0f309dd090bf01427e33b147d307b6b132c1f92115c4"),
            (2, "a15207f38d9e3992cc4cc8f91d857e6e08db34afb4d279da1dfcb2a0178bb103"),
        ):
            with self.subTest(border=border):
                target = self.directory / "whole.stl"
                STL(dict(self.params, borders=border), str(target), self.matrix).run()
                self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), digest)

    def test_exact_divisions_cross_coarse_cells(self):
        matrix = self.to_grid([
            [[x, y, z] for x, z in zip((0, 10, 20), heights)]
            for y, heights in zip((20, 10, 0), ((3, 8, 5), (11, 4, 13), (7, 16, 6)))
        ])
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 20, 20, 3, 4, output_format)

    def test_nonplanar_original_triangles_are_preserved(self):
        matrix = self.to_grid([[[0, 1, 8], [1, 1, 14]], [[0, 0, 2], [1, 0, 4]]])
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                points = self.assert_exact_tiles(matrix, 1, 1, 3, 4, output_format)
                for x, y, z in ((1 / 3, 1 / 3, 6), (1 / 3, 1 / 4, 31 / 6)):
                    selected = points[np.isclose(points[:, 0], x) & np.isclose(points[:, 1], y)]
                    selected = selected[selected[:, 2] > 0]
                    self.assertGreater(len(selected), 0)
                    np.testing.assert_allclose(selected[:, 2], z, rtol=0, atol=2e-6)

    def test_regression_gap_with_matching_spacing(self):
        matrix = self.build_mesh(90, 1, 0.75)
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 90, 1, 35, 1, output_format)

    def test_regression_gap_with_configured_half_mm_spacing(self):
        matrix = self.build_mesh(100, 1, 0.5)
        self.assertEqual(matrix[0][1].x, 0.5)
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 100, 1, 7, 1, output_format)

    def test_exact_divisions_on_2000_mm_model(self):
        matrix = self.build_mesh(2000, 1, 0.5)
        matrix = [[p._replace(z=p.z + p.x * 0.13 + p.y * 0.07) for p in row] for row in matrix]
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 2000, 1, 30, 1, output_format)

    def test_exact_divisions_with_decimal_height(self):
        matrix = self.build_mesh(2, 100.1, 0.2)
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 2, 100.1, 1, 7, output_format)

    def test_exact_dimensions_with_nonuniform_edge_cells(self):
        matrix = self.build_mesh(10.123, 10.345, 0.7)
        self.assertEqual(matrix[-1][-1].x, 10.123)
        self.assertEqual(matrix[0][0].y, 10.345)
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                self.assert_exact_tiles(matrix, 10.123, 10.345, 3, 4, output_format)

    def test_ascii_and_binary_match_with_all_side_options(self):
        for sides, border in ((False, 0), (True, 0), (True, 2)):
            with self.subTest(sides=sides, border=border):
                files = {}
                for output_format in ("binary", "ascii"):
                    builder = STL(dict(self.params, divideCols=3, divideRow=4,
                                       stl_format=output_format, has_borders=sides, borders=border),
                                  str(self.directory / (output_format + ".stl")), self.matrix)
                    builder.run()
                    files[output_format] = builder.output_files
                for binary, ascii_path in zip(files["binary"], files["ascii"]):
                    actual = read_binary(Path(binary))
                    np.testing.assert_allclose(actual, read_ascii(Path(ascii_path)), atol=2e-6)
                    triangles = actual[:, 3:12].reshape((-1, 3, 3))
                    if sides:
                        edges = Counter(
                            tuple(sorted((tuple(face[a]), tuple(face[b]))))
                            for face in triangles for a, b in ((0, 1), (1, 2), (2, 0))
                        )
                        self.assertTrue(all(count == 2 for count in edges.values()))
                    else:
                        self.assertGreater(triangles[:, :, 2].min(), 0)

    def test_many_divisions_have_unique_paths_in_dotted_directory(self):
        directory = self.directory / "project.v1"
        directory.mkdir()
        builder = STL(dict(self.params, divideCols=12, divideRow=12),
                      str(directory / "terrain.v2.stl"), self.matrix)
        builder.run()
        self.assertEqual(len(builder.output_files), 144)
        self.assertEqual(len(set(builder.output_files)), 144)
        self.assertEqual(len(list(directory.glob("*.stl"))), 144)
        for path in builder.output_files:
            self.assertEqual(Path(path).parent, directory)
            self.assertTrue(Path(path).name.startswith("terrain.v2_"))

    def test_cancellation_stops_before_next_tile(self):
        for output_format in ("binary", "ascii"):
            with self.subTest(output_format=output_format):
                builder = STL(dict(self.params, divideCols=3, divideRow=4, stl_format=output_format),
                              str(self.directory / "cancel.stl"), self.matrix)

                def cancel():
                    builder.quit = True

                builder.updateProgress.connect(cancel)
                builder.run()
                self.assertTrue(builder.quit)
                self.assertEqual(len(builder.output_files), 1)

    def test_cancellation_removes_only_generated_tiles(self):
        module = importlib.import_module(PACKAGE + ".DEMto3D_Dialog.Export_dialog")
        from qgis.PyQt.QtWidgets import QMessageBox

        paths = [self.directory / "cancel_0_0.stl", self.directory / "cancel_0_1.stl"]
        for path in paths:
            path.write_bytes(b"partial")
        unrelated = self.directory / "keep.stl"
        unrelated.write_bytes(b"keep")
        exporter = types.SimpleNamespace(
            prepareUi=Mock(),
            mainDlg=types.SimpleNamespace(ui=Mock(), tr=lambda text: text),
            STL=types.SimpleNamespace(quit=True, output_files=[str(path) for path in paths]),
        )
        with patch.object(QMessageBox, "information"):
            module.Export.finish_model(exporter)
        self.assertTrue(all(not path.exists() for path in paths))
        self.assertEqual(unrelated.read_bytes(), b"keep")


if __name__ == "__main__":
    app = QgsApplication([], False)
    app.initQgis()
    unittest.main(verbosity=2)
