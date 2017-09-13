from setuptools import setup

setup(name="detector_integration",
      version="0.0.1",
      maintainer="Paul Scherrer Institute",
      maintainer_email="daq@psi.ch",
      author="Paul Scherrer Institute",
      author_email="daq@psi.ch",
      description="Rest API to interface beamline software with the detector, backend, and writer.",

      license="GPL3",

      packages=['detector_integration',
                'detector_integration.scripts'],
)
