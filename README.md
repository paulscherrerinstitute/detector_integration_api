[![Build Status](https://travis-ci.org/datastreaming/detector_integration_api.svg?branch=master)](https://travis-ci.org/datastreaming/detector_integration_api) [![Build status](https://ci.appveyor.com/api/projects/status/3dh35htgwnu8v382?svg=true)](https://ci.appveyor.com/project/Babicaa/detector-integration-api)


# Integration REST API
REST API for integrating beamline software with the detector, backend, and writer.

## cSAXS Eiger 9M
In this section we will discuss only specific differences for the cSAXS Eiger 9M integration.

### Integration status
When calculating the integration status, we must take into account all 3 components of our system:

- Detector status: "idle", "running"
- Backend status: "INITIALIZED", "CONFIGURED", "OPEN"
- Writer status: (is_running) True False

The status interpretation code is the following:
```python
from detector_integration_api.manager import IntegrationStatus

def interpret_status(writer, backend, detector):

    if writer is False and detector == "idle" and backend == "INITIALIZED":
        return IntegrationStatus.INITIALIZED

    elif writer is False and detector == "idle" and backend == "CONFIGURED":
        return IntegrationStatus.CONFIGURED

    elif writer is True and detector == "running" and backend == "OPEN":
        return IntegrationStatus.RUNNING

    return IntegrationStatus.ERROR
```

### Detector configuration
The mandatory attributes for the detector configuration are:

- *"period"*: Period of time (in seconds) for each frame.
- *"frames"*: Number of frames to acquire.
- *"exptime"*: Exposure time (in seconds).
- *"dr"*: Dynamic range - number of bits (16, 32 etc.)

In addition, any attribute that the detector supports can be passed here. Please refer to the detector manual for a 
complete list and explanation of the attributes.

An example of a valid detector config:
```json
{
  "period": 0.1,
  "frames": 1000,
  "exptime": 0.02,
  "dr": 32
}
```

### Backend configuration
Available and at the same time mandatory backend attributes:

- *"bit_depth"*: Dynamic range - number of bits (16, 32 etc.)
- *"n_frames"*: Number of frames per acquisition.

**Warning**: Please note that this 2 attributes must match the information you provided to the detector:

- (backend) bit_depth == (detector) dr
- (backend) frames == (detector) n_frames

If this is not the case, the configuration will fail.

### Writer configuration
Due to the data format used for the cSAXS acquisition, the writer configuration is quite large. It is divided into 2 
parts:

- Writer related config (config used by the writer itself to write the data to disk)
- cSAXS file format config (config used to write the file in the cSAXS format)

An example of a valid writer config would be:
```json
{
  "output_file": "/tmp/output.h5",
  "user_id": 0,
  "group_id": 0,
  
  "date": 1.0,
  "scan": 1.0,
  "curr": 1.0,
  "idgap": 1.0,
  "harmonic": 1.0,
  "sl0wh": 1.0,
  "sl0ch": 1.0,
  "sl1wh": 1.0,
  "sl1wv": 1.0,
  "sl1ch": 1.0,
  "sl1cv": 1.0,
  "mokev": 1.0,
  "moth1": 1.0,
  "temp_mono_cryst_1": 1.0,
  "temp_mono_cryst_2": 1.0,
  "mobd": 1.0,
  "sec": 1.0,
  "bpm4_gain_setting": 1.0,
  "bpm4s": 1.0,
  "bpm4_saturation_value": 1.0,
  "bpm4x": 1.0,
  "bpm4y": 1.0,
  "bpm4z": 1.0,
  "mith": 1.0,
  "mirror_coating": 1.0,
  "mibd": 1.0,
  "bpm5_gain_setting": 1.0,
  "bpm5s": 1.0,
  "bpm5_saturation_value": 1.0,
  "bpm5x": 1.0,
  "bpm5y": 1.0,
  "bpm5z": 1.0,
  "sl2wh": 1.0,
  "sl2wv": 1.0,
  "sl2ch": 1.0,
  "sl2cv": 1.0,
  "bpm6_gain_setting": 1.0,
  "bpm6s": 1.0,
  "bpm6_saturation_value": 1.0,
  "bpm6x": 1.0,
  "bpm6y": 1.0,
  "bpm6z": 1.0,
  "sl3wh": 1.0,
  "sl3wv": 1.0,
  "sl3ch": 1.0,
  "sl3cv": 1.0,
  "fil_comb_description": 1.0,
  "sl4wh": 1.0,
  "sl4wv": 1.0,
  "sl4ch": 1.0,
  "sl4cv": 1.0,
  "bs1x": 1.0,
  "bs1y": 1.0,
  "bs1_det_dist": 1.0,
  "bs1_status": 1.0,
  "bs2x": 1.0,
  "bs2y": 1.0,
  "bs2_det_dist": 1.0,
  "bs2_status": 1.0,
  "diode": 1.0,
  "sample_name": 1.0,
  "sample_description": 1.0,
  "samx": 1.0,
  "samy": 1.0,
  "temp": 1.0
}
```

#### Writer related config
To configure the writer, you must specify:

- *"output\_file"*: Location where the file will be written.
- *"user\_id"*: User to write the writer process under.
- *"group\_id"*: Group to write the writer process under.

In addition to this properties, a valid config must also have the parameters needed for the cSAXS file format.

#### cSAXS file format config

The following fields are required to write a valid cSAXS formated file. 
On the right side is the path inside the HDF5 file where the value will be stored.

- *"scan"*: "/entry/title",
- *"curr"*: "/entry/instrument/source/current",
- *"idgap"*: "/entry/instrument/insertion_device/gap",
- *"harmonic"*: "/entry/instrument/insertion_device/harmonic",
- *"sl0wh"*: "/entry/instrument/slit_0/x_gap",
- *"sl0ch"*: "/entry/instrument/slit_0/x_translation",
- *"sl1wh"*: "/entry/instrument/slit_1/x_gap",
- *"sl1wv"*: "/entry/instrument/slit_1/y_gap",
- *"sl1ch"*: "/entry/instrument/slit_1/x_translation",
- *"sl1cv"*: "/entry/instrument/slit_1/height",
- *"mokev"*: "/entry/instrument/monochromator/energy",
- *"moth1"*: \["/entry/instrument/monochromator/crystal_1/bragg_angle", "/entry/instrument/monochromator/crystal_2/bragg_angle"\],
- *"temp\_mono\_cryst_1"*: "/entry/instrument/monochromator/crystal_1/temperature",
- *"temp\_mono\_cryst_2"*: "/entry/instrument/monochromator/crystal_2/temperature",
- *"mobd"*: "/entry/instrument/monochromator/crystal_2/bend_x",
- *"sec"*: \["/entry/instrument/XBPM4/XBPM4/count_time", "/entry/instrument/XBPM5/XBPM5/count_time", "/entry/instrument/XBPM6/XBPM6/count_time"\],
- *"bpm4\_gain\_setting"*: "/entry/instrument/XBPM4/XBPM4/gain_setting",
- *"bpm4s"*: \["/entry/instrument/XBPM4/XBPM4_sum/data", "/entry/control/integral"\],
- *"bpm4\_saturation_value"*: "/entry/instrument/XBPM4/XBPM4_sum/saturation_value",
- *"bpm4x"*: "/entry/instrument/XBPM4/XBPM4_x/data",
- *"bpm4y"*: "/entry/instrument/XBPM4/XBPM4_y/data",
- *"bpm4z"*: "/entry/instrument/XBPM4/XBPM4_skew/data",
- *"mith"*: "/entry/instrument/mirror/incident_angle",
- *"mirror\_coating"*: "/entry/instrument/mirror/coating_material",
- *"mibd"*: "/entry/instrument/mirror/bend_y",
- *"bpm5\_gain\_setting"*: "/entry/instrument/XBPM5/XBPM5/gain_setting",
- *"bpm5s"*: "/entry/instrument/XBPM5/XBPM5_sum/data",
- *"bpm5\_saturation_value"*: "/entry/instrument/XBPM5/XBPM5_sum/saturation_value",
- *"bpm5x"*: "/entry/instrument/XBPM5/XBPM5_x/data",
- *"bpm5y"*: "/entry/instrument/XBPM5/XBPM5_y/data",
- *"bpm5z"*: "/entry/instrument/XBPM5/XBPM5_skew/data",
- *"sl2wh"*: "/entry/instrument/slit_2/x_gap",
- *"sl2wv"*: "/entry/instrument/slit_2/y_gap",
- *"sl2ch"*: "/entry/instrument/slit_2/x_translation",
- *"sl2cv"*: "/entry/instrument/slit_2/height",
- *"bpm6\_gain\_setting"*: "/entry/instrument/XBPM6/XBPM6/gain_setting",
- *"bpm6s"*: "/entry/instrument/XBPM6/XBPM6_sum/data",
- *"bpm6\_saturation\_value"*: "/entry/instrument/XBPM6/XBPM6_sum/saturation_value",
- *"bpm6x"*: "/entry/instrument/XBPM6/XBPM6_x/data",
- *"bpm6y"*: "/entry/instrument/XBPM6/XBPM6_y/data",
- *"bpm6z"*: "/entry/instrument/XBPM6/XBPM6_skew/data",
- *"sl3wh"*: "/entry/instrument/slit_3/x_gap",
- *"sl3wv"*: "/entry/instrument/slit_3/y_gap",
- *"sl3ch"*: "/entry/instrument/slit_3/x_translation",
- *"sl3cv"*: "/entry/instrument/slit_3/height",
- *"fil\_comb\_description"*: "/entry/instrument/filter_set/type",
- *"sl4wh"*: "/entry/instrument/slit_4/x_gap",
- *"sl4wv"*: "/entry/instrument/slit_4/y_gap",
- *"sl4ch"*: "/entry/instrument/slit_4/x_translation",
- *"sl4cv"*: "/entry/instrument/slit_4/height",
- *"bs1x"*: "/entry/instrument/beam_stop_1/x",
- *"bs1y"*: "/entry/instrument/beam_stop_1/y",
- *"bs1\_det\_dist"*: "/entry/instrument/beam_stop_1/distance_to_detector",
- *"bs1\_status"*: "/entry/instrument/beam_stop_1/status",
- *"bs2x"*: "/entry/instrument/beam_stop_2/x",
- *"bs2y"*: "/entry/instrument/beam_stop_2/y",
- *"bs2_det_dist"*: "/entry/instrument/beam_stop_2/distance_to_detector",
- *"bs2_status"*: "/entry/instrument/beam_stop_2/status",
- *"diode"*: "/entry/instrument/beam_stop_2/data",
- *"sample\_name"*: "/entry/sample/name",
- *"sample\_description"*: "/entry/sample/description",
- *"samx"*: "/entry/sample/x_translation",
- *"samy"*: "/entry/sample/y_translation",
- *"temp"*: "/entry/sample/temperature_log"
