"""Download any requirements that aren't available on PyPI."""

import urllib
urllib.urlretrieve(
    "https://sourcesup.renater.fr/frs/download.php/4425/"
    "ScientificPython-2.9.3.tar.gz",
    "ScientificPython-2.9.3.tar.gz")
