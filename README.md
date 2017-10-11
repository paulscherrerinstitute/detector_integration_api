[![Build Status](https://travis-ci.org/datastreaming/detector_integration_api.svg?branch=master)](https://travis-ci.org/datastreaming/detector_integration_api) [![Build status](https://ci.appveyor.com/api/projects/status/3dh35htgwnu8v382?svg=true)](https://ci.appveyor.com/project/Babicaa/detector-integration-api)


# Integration REST API
REST API for integrating beamline software with the detector, backend, and writer.

# Table of content
1. [Quick introduction](#quick)
2. [Build](#build)
    1. [Conda setup](#conda_setup)
    2. [Local build](#local_build)
    3. [Docker build](#docker_build)
3. [Running the server](#running_the_server)
    1. [Detector integration server](#run_dia)
    2. [Docker Container](#run_docker_container)
4. [State machine](#state_machine)
5. [Configuration](#configuration)
    1. [Get config](#get_config)
    2. [Set config](#set_config)
    3. [Update config](#update_config)
    4. [Set last config](#set_last_config)
6. [Web interface](#web_interface)
    1. [Methods](#methods)
    2. [Python client](#python_client)
    3. [REST API](#rest_api)
7. [Deployed instances](#deployed_instances)
    1. [cSAXS Eiger 9M](#deployed_instances_csaxs)
    
<a id="quick"></a>
## Quick introduction
This is meant to be just a quick starting guide. Details on all topics covered in this introduction are available 
in the rest of this document. 

I will use the Python client for the examples, but the same functionality can be 
achieved via the REST interface (the python client is just a wrapper around the REST interface). Also, I will 
assume that the REST api is running on "http://0.0.0.0:10000" (you should adjust this to your server).

The Python client is part of the **detector\_integration\_api** module, and its class is **DetectorIntegrationClient**.

We will start by showing the normal workflow to start an acquisition:
```python
from detector_integration_api import DetectorIntegrationClient

# Address of our api server.
api_address = "http://0.0.0.0:10000"

# Initialize the client.
client = DetectorIntegrationClient(api_address)

# Get the status of the integration.
status = client.get_status()

# Check if the integration is in the INITIALIZED state.
if status != "IntegrationStatus.INITIALIZED":
    # Resetting the integration will bring us to the IntegrationStatus.INITIALIZED state.
    client.reset()

# Define the config for the writer.
writer_config = {"output_file": "/tmp/test.h5",
                 "user_id": 0,
                 "group_id": 0}

# Define the config for the backend.
backend_config = {"bit_depth": 16,
                  "n_frames": 100}

# Define the config for the detector.
detector_config = {"period": 0.1,
                   "frames": 100,
                   "exptime": 0.01,
                   "dr": 16}

# Send the config to the writer, backend and detector. 
# This changes the integration to IntegrationStatus.CONFIGURED state
response = client.set_config(writer_config=writer_config, 
                             backend_config=backend_config, 
                             detector_config=detector_config)

# Start the acquisition. This changes the integration to IntegrationStatus.RUNNING state.
client.start()

# You can manually stop the acquisition. This changes the integration to IntegrationStatus.INITIALIZED state.
client.stop()
```
    
<a id="build"></a>
## Build

<a id="conda_setup"></a>
### Conda setup
If you use conda, you can create an environment with the detector_integration_api library by running:

```bash
conda create -c paulscherrerinstitute --name <env_name> detector_integration_api
```

After that you can just source you newly created environment and start using the server.

<a id="local_build"></a>
### Local build
You can build the library by running the setup script in the root folder of the project:

```bash
python setup.py install
```

or by using the conda also from the root folder of the project:

```bash
conda build conda-recipe
conda install --use-local detector_integration_api
```

#### Requirements
The library relies on the following packages:

- python
- bottle
- requests
- mflow_nodes

In case you are using conda to install the packages, you might need to add the **paulscherrerinstitute** channel to 
your conda config:

```
conda config --add channels paulscherrerinstitute
```

<a id="docker_build"></a>
### Docker build
**Warning**: When you build the docker image with **build.sh**, your built will be pushed to the PSI repo as the 
latest detector_integration_api version. Please use the **build.sh** script only if you are sure that this 
is what you want.

To build the docker image, run the build from the **docker/** folder:
```bash
./build.sh
```

Before building the docker image, make sure the latest version of the library is available in Anaconda.

**Please note**: There is no need to build the image if you just want to run the docker container. 
Please see the [Docker Container](#run_docker_container) chapter.

<a id="running_the_server"></a>
## Running the server

The script for running the server is located in the **detector_integration_api/** folder.

- **DIA server** (start_server.py): Starts an instance of the detector integration API.

You can also use the docker container directly, see the [Docker Container](#run_docker_container) chapter.

Before you can run the server, you need to have (and specify where you have it) the detector configuration file and 
the environment configuration file. Please see the [Configuration](#configuration) chapter for more details.

<a id="run_dia"></a>
### Detector integration server
# TODO

<a id="run_docker_container"></a>
### Docker container
# TODO

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
| IntegrationStatus.RUNNING | Acquisition started. |||
| | | stop | IntegrationStatus.INITIALIZED |
| | | reset | IntegrationStatus.INITIALIZED |
| IntegrationStatus.ERROR | Something went wrong. |||
| | | stop | IntegrationStatus.INITIALIZED |
| | | reset | IntegrationStatus.INITIALIZED |

A short summary would be:

- You always need to configure the integration before starting the acquisition.
- You cannot change the configuration while the acquisition is running or there is an error.
- The stop method can be called in every state, but it stop the acquisition only if it is running.
- Whatever happens, you have the reset method that returns you in the initial state.

<a id="configuration"></a>
## Configuration
The integration can be configured only in the **IntegrationStatus.INITIALIZED** or in the 
**IntegrationStatus.CONFIGURED** states.

There are different methods of setting the configuration. It is recommended to always set the full configuration 
[Set config](#set_config), but if you are confident that nobody else interacted with the system you can use also more 
advanced methods to facilitate the usage and speed up your software.

More info on each method can be found in the [Web interface](#web_interface) chapter.

<a id="get_config"></a>
### Get config
Returns the current config stored in the integration server. This config will be used as a base in case you 
use the [Update config](#update_config) or [Set last config](#set_last_config) command.

The method return all 3 of the available configs:
- writer config
- backend config
- detector config

<a id="set_config"></a>
### Set config
Sets the complete config on the integration server. This command also propagates the config to all the integration 
servers (writer, backend, detector).

All 3 configs must be specified in full.

For an example, see [Quick introduction](#quick).

<a id="update_config"></a>
### Update config
With this method you can send only the changes to the server. It will take the config returned by 
[Get config](#get_config) as the base, and apply the changes you provided. You can specify any (or all) of the 3 
configs, and any number of fields inside each config.

This method is useful for making small changes to the previous config, without the need to re-submit the complete 
config again.

```python
from detector_integration_api import DetectorIntegrationClient
client = DetectorIntegrationClient("http://0.0.0.0:10000")

# ... suppose we already had an acquisition, and previously called set_config on this server.

# Change only the output file, but keep the rest of the configuration.
client.update_config(writer_config={"output_file":"/tmp/run2.h5"})
# Do another acquisition with the same config, just different output file name.
client.start()
```

<a id="set_last_config"></a>
### Set last config
This method will apply the config that is currently set in the integration server. This is the config returned 
from [Get config](#get_config).

This method is useful to quickly repeat the same acquisition without the need to set or update the config.
```python
from detector_integration_api import DetectorIntegrationClient
client = DetectorIntegrationClient("http://0.0.0.0:10000")

# ... suppose we already had an acquisition, and previously called set_config on this server.

# Use the same config as with the last acquisition.
client.set_last_config()
# Start the acquisition.
client.start()
```

<a id="web_interface"></a>
## Web interface
All integration api methods are exposed over a REST interface. For more information on what each command does 
check the [Methods](#methods) section in this document.

<a id="methods"></a>
### Methods
This section describes the available methods that can be accessed over the REST API or via the Python client (both 
discussed below).

| Method | Parameters | Return value | Description |
|--------|------------|--------------|-------------|
| start | / | / | Start the acquisition. |
| stop | / | / | Stop the acquisition. |
| reset | / | / | Reset the integration status. |
| get_status | / | Integration status. | Returns the integration status. See [State machine](#state_machine) |
| get_status_details | / | Status of all integration components. | Returns statuses of all components of the system. Useful when debuginig. |
| get_server_info | / | Integration server info. | Return diagnostics. |
| get_detector_value | Name of the value. | Detector value. | Read a value that is set on the detector. |
| get_config | / | Integration configuration. | Information about the current set configuration. |
| set_config | Writer, Backend and Detector config. | Config that was set. | Set the complete config for the acquisition. |
| set_last_config | / | Config that was set. | Re-apply the last used config. Used to transit from INITIALIZED to CONIFGURED without sending a new config. |
| update_config | Writer, Backend and Detector config. | Config that was set. | Update the current config on the server. You need to specify only the values you want to change. |


<a id="python_client"></a>
### Python client
The Python client is just a wrapper around the REST API. It is however recommended to use it, because the REST API 
might change in the future, while the Python client should be more stable.

Import and detector integration API client:
```python
from detector_integration_api import DetectorIntegrationClient

client = DetectorIntegrationClient("http://0.0.0.0:41000")
client.get_status()
```

Class definition:
# TODO
```
```

<a id="rest_api"></a>
### REST API
All request return a JSON with the following fields:
- **state** - \["ok", "error"\]
- **status** - Current status of the integration - \["IntegrationStatus.INITIALIZED", "IntegrationStatus.CONFIGURED", 
"IntegrationStatus.RUNNING", "IntegrationStatus.ERROR"\]
- Optional request specific field - \["value", "config", "server_info"\]

In the API description, localhost and port 8888 are assumed. Please change this for your specific case.
**Format**: Method name: HTTP CALL - description.

* start: `POST localhost:8888/api/v1/start` - Start the acquisition.
    - Response specific field: /
    
* stop: `POST localhost:8888/api/v1/stop` - Stop the acquisition.
    - Response specific field: /
    
* reset: `GET localhost:8888/api/v1/reset` - Reset the integration.
    - Response specific field: /
    
* get_status: `GET localhost:8888/api/v1/status` - Get the integration status.
    - Response specific field: /
    
* get_status_details: `GET localhost:8888/api/v1/status_details` - Get the statuses of all sub-systems.
    - Response specific field: "details" - Details on the statuses.
    
* get_config: `GET localhost:8888/api/v1/cam/config` - get the geometry of the camera.
    - Response specific field: "config" - Configuration of the server.

* set_config: `PUT localhost:8888/api/v1/cam/config` - get the geometry of the camera.
    - Response specific field: "config" - Configuration of the server.
    
* update_config: `POST localhost:8888/api/v1/cam/config` - get the geometry of the camera.
    - Response specific field: "config" - Configuration of the server.
    
* set_last_config: `POST localhost:8888/api/v1/configure` - get one PNG image of the camera.
    - Response specific field: "config" - Configuration of the server.
    
* get_detector_value: `GET localhost:8888/api/v1/detector/value/<value_name>` - return info on the camera manager.
    - Response specific field: "value" - Value of the requested parameter.
    
* get_server_info: `GET localhost:8888/api/v1/info` - Return info on the server.
    - Response specific field: "server_info" - Info about the server.


<a id="deployed_instances"></a>
## Deployed instances
This section is dedicated for the discussion of specific deployment instances, when there is some custom behaviour not 
described in the general documentation above.

<a id="deployed_instances_csaxs"></a>
### cSAXS Eiger 9M
In this section we will discuss only specific differences for the cSAXS Eiger 9M integration.

#### Example
This is a complete example of everything that needs to be done to start an acquisition on cSAXS for the Eiger 9M.

```python
from detector_integration_api import DetectorIntegrationClient

client = DetectorIntegrationClient("http://xbl-daq-28:10000")
client.reset()

# Define the config for the writer. Except for the first 3, all this value should come from Spec.
writer_config = {
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

# Define the config for the backend.
backend_config = {"bit_depth": 16,
                  "n_frames": 100}

# Define the config for the detector.
detector_config = {"period": 0.1,
                   "frames": 100,
                   "exptime": 0.01,
                   "dr": 16}

# Set the config.
client.set_config(writer_config=writer_config, backend_config=backend_config, detector_config=detector_config)

# Start the acquisition.
client.start()

# Stop the acquisition.
client.stop()
```

#### Integration status
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

#### Detector configuration
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

#### Backend configuration
Available and at the same time mandatory backend attributes:

- *"bit_depth"*: Dynamic range - number of bits (16, 32 etc.)
- *"n_frames"*: Number of frames per acquisition.

**Warning**: Please note that this 2 attributes must match the information you provided to the detector:

- (backend) bit_depth == (detector) dr
- (backend) frames == (detector) n_frames

If this is not the case, the configuration will fail.

#### Writer configuration
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
