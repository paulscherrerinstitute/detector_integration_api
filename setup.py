from setuptools import setup

setup(name="detector_integration_api",
      version="1.3.0",
      maintainer="Paul Scherrer Institute",
      maintainer_email="daq@psi.ch",
      author="Paul Scherrer Institute",
      author_email="daq@psi.ch",
      description="Rest API to interface beamline software with the detector, backend, and writer.",

      license="GPL3",

      package_dir={'detector_integration_api.tests': "tests"},

      packages=['detector_integration_api',
                'detector_integration_api.client',
                'detector_integration_api.debug',
                'detector_integration_api.rest_api',
                'detector_integration_api.tests'],

      include_package_data=True
      )
