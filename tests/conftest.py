import json
from pathlib import Path
import os
from typing import List

import pandas as pd
import pytest
import numpy as np
import nrrd

import navis


@pytest.fixture(scope="session")
def data_dir():
    return Path(__file__).resolve().parent.parent / "navis" / "data"


@pytest.fixture(scope="session")
def fixture_dir():
    return Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(
    params=["Path", "pathstr", "swcstr", "textbuffer", "rawbuffer", "DataFrame"]
)
def swc_source(request, swc_paths: List[Path]):
    swc_path: Path = swc_paths[0]
    if request.param == "Path":
        yield swc_path
    elif request.param == "pathstr":
        yield str(swc_path)
    elif request.param == "swcstr":
        yield swc_path.read_text()
    elif request.param == "textbuffer":
        with open(swc_path) as f:
            yield f
    elif request.param == "rawbuffer":
        with open(swc_path, "rb") as f:
            yield f
    elif request.param == "DataFrame":
        df = pd.read_csv(swc_path, sep=" ", header=None, comment="#")
        df.columns = navis.io.swc_io.NODE_COLUMNS
        yield df
    else:
        raise ValueError("Unknown parameter")


@pytest.fixture(
    params=["dirstr", "dirpath", "list", "listwithdir"],
)
def swc_source_multi(request, swc_paths: List[Path]):
    fpath = swc_paths[0]
    dpath = fpath.parent
    if request.param == "dirstr":
        yield str(dpath)
    elif request.param == "dirpath":
        yield dpath
    elif request.param == "list":
        yield [fpath, fpath]
    elif request.param == "listwithdir":
        yield [dpath, fpath]
    else:
        raise ValueError(f"Unknown parameter '{request.param}'")


@pytest.fixture
def voxel_nrrd_path(tmp_path):
    parent = tmp_path / "nrrd"
    parent.mkdir()
    path = parent / "simple.nrrd"
    data = np.zeros((15, 15, 15))
    rng = np.random.RandomState(1991)
    core = rng.random((5, 5, 15))
    data[5:10, 5:10, :] = core

    header = {
        "space directions": np.diag([1, 2, 3]).tolist(),
        "space units": ["um", "um", "um"],
    }
    nrrd.write(os.fspath(path), data, header)

    return path


def data_paths(dpath, glob="*"):
    return sorted(dpath.glob(glob))


@pytest.fixture(scope="session")
def swc_paths(data_dir: Path):
    return data_paths(data_dir / "swc", "*.swc")


@pytest.fixture(scope="session")
def gml_paths(data_dir: Path):
    return data_paths(data_dir / "gml", "*.gml")


@pytest.fixture(scope="session")
def obj_paths(data_dir: Path):
    return data_paths(data_dir / "obj", "*.obj")


@pytest.fixture(scope="session")
def synapses_paths(data_dir: Path):
    return data_paths(data_dir / "synapses", "*.csv")


@pytest.fixture(scope="session")
def volumes_paths(data_dir: Path):
    return data_paths(data_dir / "volumes", "*.obj")


@pytest.fixture
def treeneuron_dfs(swc_paths, synapses_paths):
    swc_reader = navis.io.swc_io.SwcReader()
    out = []
    for swc_path, syn_path in zip(swc_paths, synapses_paths):
        neuron = swc_reader.read_file_path(swc_path)
        neuron.connectors = pd.read_csv(syn_path)
        out.append(neuron)
    return out


@pytest.fixture
def neuron_connections(fixture_dir: Path):
    expected_jso = json.loads(
        fixture_dir.joinpath("network_connector", "expected.json").read_text()
    )
    expected = {
        int(pre): {
            int(post): n for post, n in d.items()
        } for pre, d in expected_jso.items()
    }

    nl = navis.read_json(
        str(fixture_dir.joinpath("network_connector", "network.json"))
    )
    nrns = []
    for nrn in nl:
        nrn.name = f"skeleton {nrn.id}"
        nrn.id = int(nrn.id)
        nrns.append(nrn)

    return nrns, expected
