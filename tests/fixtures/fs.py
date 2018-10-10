import pytest
import tempfile
import shutil
from pathlib import Path
from functools import partial


@pytest.fixture(scope='function')
def mkdtemp(request):
    def _mkdtemp(*args, **kwargs):
        path = Path(tempfile.mkdtemp())
        cleanup = partial(shutil.rmtree, path, ignore_errors=True)

        request.addfinalizer(cleanup)
        return path

    return _mkdtemp
