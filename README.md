[![Build Status](https://travis-ci.org/datastreaming/detector_integration_api.svg?branch=master)](https://travis-ci.org/datastreaming/detector_integration_api)

# Integration REST API
REST API for integrating beamline software with the detector, backend, and writer.

# Table of content
1. [Quick introduction](#quick)
2. [Build](#build)
    1. [Conda setup](#conda_setup)
    2. [Local build](#local_build)
    3. [Docker build](#docker_build)
3. [Running the server](#running_the_server)
5. [Configuration](#configuration)
    1. [Get config](#get_config)
    2. [Set config](#set_config)
    3. [Update config](#update_config)
    4. [Set last config](#set_last_config)
6. [Public interface](#public_interface)
    1. [Methods](#methods)
    2. [Python client](#python_client)
    3. [REST API](#rest_api)
7. [Deployed instances](#deployed_instances)
    1. [cSAXS Eiger 9M](https://github.com/paulscherrerinstitute/csaxs_dia)
    2. [SwissFEL](https://github.com/paulscherrerinstitute/sf_dia)
    
<a id="quick"></a>
## Quick introduction
This is meant to be just a quick starting guide. Details on all topics covered in this introduction are available 
in the rest of this document. Also beamline specific documentation and examples can be found in their 
README files.

I will use the Python client for the examples, but the same functionality can be 
achieved via the REST interface (the python client is just a wrapper around the REST interface). Also, I will 
assume that the REST api is running on "http://0.0.0.0:10000" (you should adjust this to your server).

The Python client is part of the **detector\_integration\_api** module, and its class is **DetectorIntegrationClient**.

**Warning**: This procedure might not work on your deployment Consult the example in your deployment README.

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
                 "n_frames": 100,
                 "user_id": 0}

# Define the config for the backend.
backend_config = {"bit_depth": 16,
                  "n_frames": 100}

# Define the config for the detector.
detector_config = {"period": 0.1,
                   "frames": 100,
                   "exptime": 0.01,
                   "dr": 16}
                   
configuration = {"writer": writer_config,
                 "backend": backend_config,
                 "detector": detector_config}

# Send the config to the writer, backend and detector. 
# This changes the integration to IntegrationStatus.CONFIGURED state
response = client.set_config(configuration)

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

<a id="running_the_server"></a>
## Running the server

The scripts for running the server are located under each deployment folder in 
**detector_integration_api/deployment**.

- **DIA server** (\[deployment_name\]_start_server.py): Starts an instance of the detector integration API.

You can also use the docker container directly. For more information consult your deployment specific README.

<a id="configuration"></a>
## Configuration
The integration can be configured only in the **IntegrationStatus.INITIALIZED** or in the 
**IntegrationStatus.CONFIGURED** states.

There are different methods of setting the configuration. It is recommended to always set the full configuration 
[Set config](#set_config), but if you are confident that nobody else interacted with the system you can use also more 
advanced methods to facilitate the usage and speed up your software.

More info on each method can be found in the [Public interface](#public_interface) chapter.

<a id="get_config"></a>
### Get config
Returns the current config stored in the integration server. This config will be used as a base in case you 
use the [Update config](#update_config) or [Set last config](#set_last_config) command.

The method return all of the available configs. This are at least:
- writer config
- backend config
- detector config

Some deployments might have more configurations (for example bsread).

<a id="set_config"></a>
### Set config
Sets the complete config on the integration server. This command also propagates the config to all the integration 
servers (writer, backend, detector).

All configs must be specified in full.

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

# ... suppose we already had an acquisition, and had previously called set_config on this server.

# Change only the output file, but keep the rest of the configuration.
client.update_config({"writer": {"output_file":"/tmp/run2.h5"}})
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

# ... suppose we already had an acquisition, and had previously called set_config on this server.

# Use the same config as with the last acquisition.
client.set_last_config()
# Start the acquisition.
client.start()
```

<a id="public_interface"></a>
## Public interface
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
| get_status | / | Integration status. | Returns the integration status. |
| get_status_details | / | Status of all integration components. | Returns statuses of all components of the system. Useful when debuginig. |
| get_config | / | Integration configuration. | Information about the current set configuration. |
| set_config | Configs for all components. | Config that was set. | Set the complete config for the acquisition. |
| update_config | Config for any or all components. | Config that was set. | Update the current config on the server. You need to specify only the values you want to change. |
| set_last_config | / | Config that was set. | Re-apply the last used config. Used to transit from INITIALIZED to CONIFGURED without sending a new config. |
| get_detector_value | Name of the detector parameter. | Value fo the parameter. | Get a detector parameter. |
| get_server_info | / | Integration server info. | Return diagnostics. |
| get_metrics | / | Acquisition statistics. | Return metrics for each system component. |


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
```
class DetectorIntegrationClient(builtins.object)
 |  Methods defined here:
 |  
 |  __init__(self, api_address=None)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |  
 |  get_backend(self, action, configuration={})
 |  
 |  get_clients_enabled(self)
 |  
 |  get_config(self)
 |  
 |  get_detector_value(self, name)
 |  
 |  get_metrics(self)
 |  
 |  get_server_info(self)
 |  
 |  get_status(self)
 |  
 |  get_status_details(self)
 |  
 |  put_backend(self, action, configuration={})
 |  
 |  reset(self)
 |  
 |  set_clients_enabled(self, configuration)
 |  
 |  set_config(self, configuration)
 |  
 |  set_config_from_file(self, filename)
 |  
 |  set_detector_value(self, parameter_name, parameter_value)
 |  
 |  set_last_config(self)
 |  
 |  start(self)
 |  
 |  stop(self)
 |  
 |  update_config(self, configuration)
 |  
 |  wait_for_status(self, target_status, timeout=None, polling_interval=0.2)

```

<a id="rest_api"></a>
### REST API
All request return a JSON with the following fields:
- **state** - \["ok", "error"\]
- **status** - Current status of the integration
    - if state == "ok" : ["IntegrationStatus.INITIALIZED", "IntegrationStatus.CONFIGURED", 
    "IntegrationStatus.RUNNING", "IntegrationStatus.ERROR"\] 
    - if state == "error" : Exception text describing the problem.
- Optional request specific field ("field" : \[list of methods returning this field\]):
    - "details" : get_status_details, 
    - "config" : set_last_config, get_config, set_config, update_config
    - "server_info" : get_server_info
    - "metrics" : get_metrics

In the API description, localhost and port 10000 are assumed. Please change this for your specific case.
**Format**: Method name: HTTP CALL - description.

* start: POST localhost:10000/api/v1/start` - Start the acquisition.
    - Request: ```curl -X POST http://localhost:10000/api/v1/start```
    - Example response: 
        ```json
        {"state":"ok", "status": "IntegrationStatus.RUNNING"}
        ```
        
* stop: `POST localhost:10000/api/v1/stop` - Stop the acquisition.
    - Request: ```curl -X POST http://localhost:10000/api/v1/stop```
    - Example response: 
        ```json
        {"state":"ok", "status": "IntegrationStatus.FINISHED"}
        ```
        
* reset: `GET localhost:10000/api/v1/reset` - Reset the integration.
    - Request: ```curl -X POST http://localhost:10000/api/v1/reset```
    - Example response: 
        ```json
        {"state":"ok", "status": "IntegrationStatus.INITIALIZED"}
        ```
        
* get_status: `GET localhost:10000/api/v1/status` - Get the integration status.
    - Request: ```curl -X GET http://localhost:10000/api/v1/status```
    - Example response: 
        ```json
        {"state":"ok", "status": "IntegrationStatus.RUNNING"}
        ```
        
* get_status_details: `GET localhost:10000/api/v1/status_details` - Get the statuses of all sub-systems.
    - Request: ```curl -X GET http://localhost:10000/api/v1/status_details```
    - Example response: 
        ```json
        {"state": "ok", "status": "IntegrationStatus.INITIALIZED", 
         "details": {"writer": "stopped", 
                     "backend": "INITIALIZED", 
                     "detector": "idle"}}
        ```
    
* get_config: `GET localhost:10000/api/v1/config` - Get the configs of all components.
    - Request: ```curl -X GET http://localhost:10000/api/v1/config```
    - Example response:
        ```json
        {"state": "ok", "status": "IntegrationStatus.INITIALIZED", 
         "config": {"writer": {}, 
                    "backend": {}, 
                    "detector": {}}}
        ```

* set_config: `PUT localhost:10000/api/v1/config` - Set the config for all components.
    - Example request:
        ```bash
        curl -X PUT http://localhost:10000/api/v1/config -H "Content-Type: application/json" -d '
        {"backend": {},
         "detector": {},
         "writer": {}}'
        ```
    - Example response:
        ```json
        {"state": "ok", "status": "IntegrationStatus.CONFIGURED", 
         "config": {"writer": {}, 
                    "backend": {}, 
                    "detector": {}
                    }}
        ```
    
* update_config: `POST localhost:10000/api/v1/config` - Update the config for the specified components.
    - Example request:
        ```bash
        curl -X POST http://localhost:10000/api/v1/config -H "Content-Type: application/json" -d '
        {"backend": {"frames": 500}'
        ```
    - Example response:
        ```json
        {"state": "ok", "status": "IntegrationStatus.CONFIGURED", 
         "config": {"writer": {}, 
                    "backend": {}, 
                    "detector": {}
                    }}
        ```
    
* set_last_config: `POST localhost:10000/api/v1/configure` - Use the last set config.
    - Request: ```curl -X POST http://localhost:10000/api/v1/configure```
    - Example response:
        ```json
        {"state": "ok", "status": "IntegrationStatus.CONFIGURED", 
         "config": {"writer": {}, 
                    "backend": {}, 
                    "detector": {}
                    }}
         ```
    
* get_detector_value: `GET localhost:10000/api/v1/detector/value/<value_name>` - get a detector parameter.
    - Example request: ```curl -X GET http://localhost:10000/api/v1/detector/value/dr```
    - Example response:
        ```json
        {"state": "ok", "status": "IntegrationStatus.CONFIGURED", 
         "value": 16}
         ```
    
* get_server_info: `GET localhost:10000/api/v1/info` - Return info on the server.
    - Request: ```curl -X GET http://localhost:10000/api/v1/info```
    - Example response:
        ```json
        {"state": "ok", "status": "IntegrationStatus.RUNNING"
        }
        ```
    
* get_metrics: `GET localhost:10000/api/v1/metrics` - Return components statistics.
    - Request: ```curl -X GET http://localhost:10000/api/v1/metrics```
    - Example response:
        ```json
        {"state": "ok", "status": "IntegrationStatus.RUNNING"
        }
        ```
    