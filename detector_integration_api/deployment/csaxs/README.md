# cSAXS Eiger 9M detector integration

The following README is useful for controlling the Eiger 9M deployment at cSAXS.

The detector integration is made up from the following components:

- Detector integration API (running on xbl-daq-27)
    - https://github.com/datastreaming/detector_integration_api
- Detector client (running on xbl-daq-27)
    - https://github.com/slsdetectorgroup/slsDetectorPackage
- Backend server (running on xbl-daq-28)
    - https://git.psi.ch/HPDI/dafl-eiger
- Writer process (running on xbl-daq-27)
    - https://git.psi.ch/babic_a/cpp_h5_writer
    
# Table of content
1. [Quick introduction](#quick)
    1. [Python client](#quick_python)
    2. [Rest API](#quick_rest)
2. [State machine](#state_machine)
3. [DIA configuration parameters](#dia_configuration_parameters)
    1. [Detector configuration](#dia_configuration_parameters_detector)
    2. [Backend configuration](#dia_configuration_parameters_backend)
    3. [Writer configuration](#dia_configuration_parameters_writer)
4. [xbl-daq-28 (Backend server)](#deployment_info_28)
5. [xbl-daq-27 (DIA and writer server)](#deployment_info_27)

<a id="quick"></a>
## Quick introduction

**DIA Address:** http://xbl-daq-27:10000

To get a feeling on how to use the DIA, you can use the following example to start and write a test file.

You can control the DIA via the Python client or over the REST api directly.

**More documentation about the DIA can be found on its repository** (referenced above).

**Note**: The writer needs a lot of parameters to write the MX file format. You probably do not care about this, so you 
can use the DEBUG_FORMAT_PARAMETERS parameters for now.

<a id="quick_python"></a>
### Python client

To use the Python client you need to source our central Python:
```bash
source /opt/gfa/python
```
or you can install it using conda:
```bash
conda install -c paulscherrerinstitute detector_integration_api
```

```python
# Just some mock value for the file format.
DEBUG_FORMAT_PARAMETERS = {
    "sl2wv": 1.0, "sl0ch": 1.0, "sl2wh": 1.0, "temp_mono_cryst_1": 1.0, "harmonic": 1,
    "mokev": 1.0, "sl2cv": 1.0, "bpm4_gain_setting": 1.0, "mirror_coating": "placeholder text",
    "samx": 1.0, "sample_name": "placeholder text", "bpm5y": 1.0, "sl2ch": 1.0, "curr": 1.0,
    "bs2_status": "placeholder text", "bs2y": 1.0, "diode": 1.0, "samy": 1.0, "sl4ch": 1.0,
    "sl4wh": 1.0, "temp_mono_cryst_2": 1.0, "sl3wh": 1.0, "mith": 1.0, "bs1_status": "placeholder text",
    "bpm4s": 1.0, "sl0wh": 1.0, "bpm6z": 1.0, "bs1y": 1.0, "scan": "placeholder text", "bpm5_gain_setting": 1.0,
    "bpm4z": 1.0, "bpm4x": 1.0, "date": "placeholder text", "mibd": 1.0, "temp": 1.0,
    "idgap": 1.0, "sl4cv": 1.0, "sl1wv": 1.0, "sl3wv": 1.0, "sl1ch": 1.0, "bs2x": 1.0, "bpm6_gain_setting": 1.0,
    "bpm4y": 1.0, "bpm6s": 1.0, "sample_description": "placeholder text", "bpm5z": 1.0, "moth1": 1.0,
    "sec": 1.0, "sl3cv": 1.0, "bs1x": 1.0, "bpm6_saturation_value": 1.0, "bpm5s": 1.0, "mobd": 1.0,
    "sl1wh": 1.0, "sl4wv": 1.0, "bs2_det_dist": 1.0, "bpm5_saturation_value": 1.0,
    "fil_comb_description": "placeholder text", "bpm5x": 1.0, "bpm4_saturation_value": 1.0, "bs1_det_dist": 1.0,
    "sl3ch": 1.0, "bpm6y": 1.0, "sl1cv": 1.0, "bpm6x": 1.0, "ftrans": 1.0, "samz": 1.0
}

# Import the client.
from detector_integration_api import DetectorIntegrationClient

# Connect to the Eiger 9M DIA.
client = DetectorIntegrationClient("http://xbl-daq-27:10000")

# Make sure the status of the DIA is initialized.
client.reset()

# Write 1000 frames, as user id 11057 (gac-x12saop), to file "/sls/X12SA/Data10/gac-x12saop/tmp/dia_test.h5".
writer_config = {"n_frames": 1000, "user_id": 11057, "output_file": "/sls/X12SA/Data10/gac-x12saop/tmp/dia_test.h5"}

# Expect 1000, 16 bit frames.
backend_config = {"bit_depth": 16, "n_frames": 1000}

# Acquire 1000, 16 bit images with a period of 0.02.
detector_config = {"dr": 16, "frames": 1000, "period": 0.02}

# Add format parameters to writer. In this case, we use the debugging one.
writer_config.update(DEBUG_FORMAT_PARAMETERS)

# Set the configs.
client.set_config(writer_config=writer_config, backend_config=backend_config, detector_config=detector_config)

# Start the acquisition.
client.start()

# Get the current acquisition status (it should be "IntegrationStatus.RUNNING")
client.get_status()

# Block until the acquisition has finished (this is optional).
client.wait_for_status("IntegrationStatus.FINISHED")

```

<a id="quick_rest"></a>
### Rest API

The direct calls to the REST Api will be shown with cURL. 

Responses from the server are always JSONs. The "state" attribute in the JSON response is:

- **"ok"**: The server processed your request successfully
    - Response example: {"state": "ok", "status": "IntegrationStatus.INITIALIZED"}
- **"error"**: An error happened on the server. The field **"status"** will tell you what is the problem.
    - Response example: {"state": "error", "status": "Specify config JSON with 3 root elements..."}

**Note**: Most of the writer parameters in the **config** calls are just for the file format. Only the first 3 are 
important right now:

- n_frames (10 in this example)
- output_file (/sls/X12SA/Data10/gac-x12saop/tmp/dia_test.h5 in this example)
- user_id (11057: gac-x12saop in this example)

**Tip**: You can get a user id by running:
```bash
# Get the id for user gac-x12saop
id -u gac-x12saop
```

```bash
# Make sure the status of the DIA is initialized.
curl -X POST http://xbl-daq-27:10000/api/v1/reset

# Write 1000 frames, as user id 11057 (gac-x12saop), to file "/sls/X12SA/Data10/gac-x12saop/tmp/dia_test.h5".
curl -X PUT http://xbl-daq-27:10000/api/v1/config -H "Content-Type: application/json" -d '
{"backend": {"bit_depth": 16, "n_frames": 10},
 "detector": {"dr": 16, "exptime": 1, "frames": 10, "period": 0.1},
 "writer": {
  "n_frames": 10,
  "output_file": "/sls/X12SA/Data10/gac-x12saop/tmp/dia_test_4.h5",
  "user_id": 11057,
  
  "bpm4_gain_setting": 1.0,
  "bpm4_saturation_value": 1.0,
  "bpm4s": 1.0,
  "bpm4x": 1.0,
  "bpm4y": 1.0,
  "bpm4z": 1.0,
  "bpm5_gain_setting": 1.0,
  "bpm5_saturation_value": 1.0,
  "bpm5s": 1.0,
  "bpm5x": 1.0,
  "bpm5y": 1.0,
  "bpm5z": 1.0,
  "bpm6_gain_setting": 1.0,
  "bpm6_saturation_value": 1.0,
  "bpm6s": 1.0,
  "bpm6x": 1.0,
  "bpm6y": 1.0,
  "bpm6z": 1.0,
  "bs1_det_dist": 1.0,
  "bs1_status": "placeholder text",
  "bs1x": 1.0,
  "bs1y": 1.0,
  "bs2_det_dist": 1.0,
  "bs2_status": "placeholder text",
  "bs2x": 1.0,
  "bs2y": 1.0,
  "curr": 1.0,
  "date": "placeholder text",
  "diode": 1.0,
  "fil_comb_description": "placeholder text",
  "ftrans": 1.0,
  "harmonic": 1,
  "idgap": 1.0,
  "mibd": 1.0,
  "mirror_coating": "placeholder text",
  "mith": 1.0,
  "mobd": 1.0,
  "mokev": 1.0,
  "moth1": 1.0,
  "sample_description": "placeholder text",
  "sample_name": "placeholder text",
  "samx": 1.0,
  "samy": 1.0,
  "samz": 1.0,
  "scan": "placeholder text",
  "sec": 1.0,
  "sl0ch": 1.0,
  "sl0wh": 1.0,
  "sl1ch": 1.0,
  "sl1cv": 1.0,
  "sl1wh": 1.0,
  "sl1wv": 1.0,
  "sl2ch": 1.0,
  "sl2cv": 1.0,
  "sl2wh": 1.0,
  "sl2wv": 1.0,
  "sl3ch": 1.0,
  "sl3cv": 1.0,
  "sl3wh": 1.0,
  "sl3wv": 1.0,
  "sl4ch": 1.0,
  "sl4cv": 1.0,
  "sl4wh": 1.0,
  "sl4wv": 1.0,
  "temp": 1.0,
  "temp_mono_cryst_1": 1.0,
  "temp_mono_cryst_2": 1.0
 }
}'

# Start the acquisition.
curl -X POST http://xbl-daq-27:10000/api/v1/start

# Get integration status.
curl -X GET http://xbl-daq-27:10000/api/v1/status

# Stop the acquisition. This should be called only in case of emergency:
#   by default it should stop then the selected number of images is collected.
curl -X POST http://xbl-daq-27:10000/api/v1/stop
```

<a id="state_machine"></a>
## State machine

The table below describes the possible states of the integration and the methods that cause a transition 
(this are also the methods that are allowed for a defined state).

Methods that do not modify the state machine are not described in this table, as they can be executed in every state.

| State | State description | Transition method | Next state |
|-------|-------------------|-------------------|------------|
| IntegrationStatus.INITIALIZED | Integration ready for configuration. |||
| | | set_config | IntegrationStatus.CONFIGURED |
| | | set_last_config | IntegrationStatus.CONFIGURED |
| | | update_config | IntegrationStatus.CONFIGURED |
| | | stop | IntegrationStatus.INITIALIZED |
| | | reset | IntegrationStatus.INITIALIZED |
| IntegrationStatus.CONFIGURED | Acquisition configured. |||
| | | start | IntegrationStatus.RUNNING |
| | | set_config | IntegrationStatus.CONFIGURED |
| | | set_last_config | IntegrationStatus.CONFIGURED |
| | | update_config | IntegrationStatus.CONFIGURED |
| | | stop | IntegrationStatus.INITIALIZED |
| | | reset | IntegrationStatus.INITIALIZED |
| IntegrationStatus.RUNNING | Acquisition running. |||
| | | stop | IntegrationStatus.INITIALIZED |
| | | reset | IntegrationStatus.INITIALIZED |
| IntegrationStatus.DETECTOR_STOPPED | Waiting for backend and writer to finish. |||
| | | stop | IntegrationStatus.INITIALIZED |
| | | reset | IntegrationStatus.INITIALIZED |
| IntegrationStatus.FINISHED | Acquisition completed. |||
| | | reset | IntegrationStatus.INITIALIZED |
| IntegrationStatus.ERROR | Something went wrong. |||
| | | stop | IntegrationStatus.INITIALIZED |
| | | reset | IntegrationStatus.INITIALIZED |

A short summary would be:

- You always need to configure the integration before starting the acquisition.
- You cannot change the configuration while the acquisition is running or there is an error.
- The stop method can be called in every state, but it stop the acquisition only if it is running.
- Whatever happens, you have the reset method that returns you in the initial state.
- When the detector stops sending data, the status is DETECTOR_STOPPED. Call STOP to close the backend and stop the 
writing.
- When the detector stops sending data, the backend and writer have completed, 
the status is FINISHED.

<a id="dia_configuration_parameters"></a>
## DIA configuration parameters

The following are the parameters in the DIA.

<a id="dia_configuration_parameters_detector"></a>
### Detector configuration
The mandatory attributes for the detector configuration are:

- *"period"*: Period of time (in seconds) for each frame.
- *"frames"*: Number of frames to acquire.
- *"dr"*: Dynamic range - number of bits (16, 32 etc.)

In addition, any attribute that the detector supports can be passed here. Please refer to the detector manual for a 
complete list and explanation of the attributes.

An example of a valid detector config:
```json
{
  "period": 0.1,
  "frames": 1000,
  "dr": 32
}
```

<a id="dia_configuration_parameters_backend"></a>
### Backend configuration
Available and at the same time mandatory backend attributes:

- *"bit_depth"*: Dynamic range - number of bits (16, 32 etc.)
- *"n_frames"*: Number of frames per acquisition.

**Warning**: Please note that this 2 attributes must match the information you provided to the detector:

- (backend) bit_depth == (detector) dr
- (backend) n_frames == (detector) frames

If this is not the case, the configuration will fail.

<a id="dia_configuration_parameters_writer"></a>
### Writer configuration
Due to the data format used for the cSAXS acquisition, the writer configuration is quite large. It is divided into 2 
parts:

- Writer related config (config used by the writer itself to write the data to disk)
- cSAXS file format config (config used to write the file in the cSAXS format)

An example of a valid writer config would be:
```json
{
    "output_file": "/tmp/dia_test.h5",
    "n_frames": 1000, 
    "user_id": 0, 
    

    "sl2wv": 1.0, "sl0ch": 1.0, "sl2wh": 1.0, "temp_mono_cryst_1": 1.0, "harmonic": 1,
    "mokev": 1.0, "sl2cv": 1.0, "bpm4_gain_setting": 1.0, "mirror_coating": "placeholder text",
    "samx": 1.0, "sample_name": "placeholder text", "bpm5y": 1.0, "sl2ch": 1.0, "curr": 1.0,
    "bs2_status": "placeholder text", "bs2y": 1.0, "diode": 1.0, "samy": 1.0, "sl4ch": 1.0,
    "sl4wh": 1.0, "temp_mono_cryst_2": 1.0, "sl3wh": 1.0, "mith": 1.0, "bs1_status": "placeholder text",
    "bpm4s": 1.0, "sl0wh": 1.0, "bpm6z": 1.0, "bs1y": 1.0, "scan": "placeholder text", "bpm5_gain_setting": 1.0,
    "bpm4z": 1.0, "bpm4x": 1.0, "date": "placeholder text", "mibd": 1.0, "temp": 1.0,
    "idgap": 1.0, "sl4cv": 1.0, "sl1wv": 1.0, "sl3wv": 1.0, "sl1ch": 1.0, "bs2x": 1.0, "bpm6_gain_setting": 1.0,
    "bpm4y": 1.0, "bpm6s": 1.0, "sample_description": "placeholder text", "bpm5z": 1.0, "moth1": 1.0,
    "sec": 1.0, "sl3cv": 1.0, "bs1x": 1.0, "bpm6_saturation_value": 1.0, "bpm5s": 1.0, "mobd": 1.0,
    "sl1wh": 1.0, "sl4wv": 1.0, "bs2_det_dist": 1.0, "bpm5_saturation_value": 1.0,
    "fil_comb_description": "placeholder text", "bpm5x": 1.0, "bpm4_saturation_value": 1.0, "bs1_det_dist": 1.0,
    "sl3ch": 1.0, "bpm6y": 1.0, "sl1cv": 1.0, "bpm6x": 1.0, "ftrans": 1.0, "samz": 1.0
}
```

**Warning**: Please note that this 2 attributes must match the information you provided to the detector:

- (writer) n_frames == (detector) frames

If this is not the case, the configuration will fail.

#### Writer related config
To configure the writer, you must specify:

- *"output\_file"*: Location where the file will be written.
- *"n_frames"*: Number of frames to acquire.
- *"user_id"*: Under which user to run the writer.

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

<a id="deployment_info"></a>
## Deployment information

In this section we will describe the current deployment, server by server.

<a id="deployment_info_28"></a>
## xbl-daq-28 (Backend server)
On xbl-daq-28 we are running the backend server. The backend is listening on address:

- **http://xbl-daq-28:8080**

It is run using a **systemd** service (/etc/systemd/system/detector_backend.service). 

The services invokes the startup file **/home/dbe/start_dbe.sh**.

The service can be controlled with the following commands (using sudo or root):
- **systemctl start detector\_backend.service** (start the backend)
- **systemctl stop detector\_backend.service** (stop the backend)
- **journalctl -u detector\_backend.service -f** (check the backend logs)

<a id="deployment_info_27"></a>
## xbl-daq-27 (DIA and writer server)
On xbl-daq-27 we are running the detector integration api. The DIA is listening on address:

- **http://xbl-daq-27:10000**

It is run using a **systemd** service (/etc/systemd/system/dia.service). 

The services invokes the startup file **/home/dia/start_dia.sh**.

The service can be controlled with the following commands (using sudo or root):
- **systemctl start dia.service** (start the backend)
- **systemctl stop dia.service** (stop the backend)
- **journalctl -u dia.service -f** (check the dia logs)

### Writer
The writer is spawn on request from the DIA. To do that, DIA uses the startup file **/home/dia/start_writer.sh**.

Each time the writer is spawn, a separate log file is generated in **/var/log/h5_zmq_writer/**.