# Nautobot to Arista CloudVision Sync

A plugin for [Nautobot](https://github.com/nautobot/nautobot) that allows synchronization between Arista Cloudvision and Nautobot.

This plugin is an extension of the [Nautobot Single Source of Truth (SSoT)](https://github.com/nautobot/nautobot-plugin-ssot) and you must have that plugin installed before installing this extension.

## Installation

The plugin is available as a Python package in pypi and can be installed with pip

```shell
pip install nautobot_ssot_aristacv
```

> The plugin is compatible with Nautobot 1.0.0 and higher

To ensure Nautobot to Arista CloudVision Sync is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot_ssot_aristacv` package:

```no-highlight
# echo nautobot_ssot_aristacv >> local_requirements.txt
```

Once installed, the plugin needs to be enabled in your `nautobot_configuration.py`

```python
# In your configuration.py
PLUGINS = ["nautobot_ssot", "nautobot_ssot_aristacv"]

# PLUGINS_CONFIG = {
#   "nautobot_ssot" : {
#     ADD YOUR SETTINGS HERE
#   }
#   "nautobot_ssot_aristacv": {
#     ADD YOUR SETTINGS HERE
#   }
# }
```

Upon installation, this plugin creates the following custom fields in Nautobot:

- `arista_bgp`
- `arists_eos`
- `arista_eostrain`
- `arista_mlag`
- `arista_mpls`
- `arista_pim`
- `arista_pimbidir`
- `arista_sflow`
- `arista_systype`
- `arista_tapagg`
- `arista_terminattr`
- `arista_topology_network_type`
- `arista_topology_type`
- `arista_ztp`

> While these contain the prefix "arista" in the custom field admin portal, when looking at them on a device the prefix is removed.

The plugin can connect to either on-premise or a cloud instance of Cloudvision. To connect to an on-premise instance you must set the following variables in the nautobot configuration file.

- `cvp_host` string: The hostname or address of the onprem instance of Cloudvision
- `cvp_user` string: The username used to connect to the onprem instance Cloudvision.
- `cvp_password` string: The password used to connect to the onprem instance Cloudvision.
- `insecure` boolean: If true, the plugin will download the certificate from Cloudvision and trusted for gRPC.

To connect to a cloud instance of Cloudvision you must set the following variable:
- `cvaas_token` string: Token to be used when connected to Cloudvision as a Service.


When syncing from Cloudvision, this plugin will create new devices that do not exist in Nautobot. In order for this to work properly, you must provide the following default value sin the nautobot config file.

- `from_cloudvision_default_site` string: The default site used when syncing creates new devices in Nautobot.
- `from_cloudvision_default_device_role` string: The default device role used when the syncing creates new devices in Nautobot.
- `from_cloudvision_default_device_role_color` string: The default color to assign to the default role.
- `from_cloudvision_default_device_status`: string: The default status used when the syncing creates new devices in Nautobot.

Lastly, when a device exists in Nautobot but not in Cloudvision, this plugin can either delete or leave the device in Nautobot. That behavior can be set with the following variable in the nautobot config file.

- `delete_devices_on_sync_cv_source` boolean (default False): If true, this will delete devices in Nautbot that do not exist in Cloudvision when syncing from Cloudvision.

## Usage

This extension can sync data both `to` and `from` Nautobot. Once the plugin has been installed succesfully two new options are available under the [Nautobot Single Source of Truth (SSoT)](https://github.com/nautobot/nautobot-plugin-ssot) plugin.

![Arista Extension](https://user-images.githubusercontent.com/38091261/124857275-9a6c0100-df71-11eb-8ace-2ddf67a2471f.PNG)


### Syncing From Cloudvision

> When loading Nautobot data, this tool only loads devices with a deice type that has a manufacturer of "Arista"
When syncing data from Cloudvision to Nautobot, system tags as well as devices are synced.  When a device exists in Cloudvision that doesn't exist in Nautobot, this tool creates the device in Nautobot with the default values specified in the configuration file. When a device exists in Nautobot that doesn't exist in Cloudvision, this tool will delete that device from Nautobot. You can watch the below video for an example.

![fromcv_sync](https://user-images.githubusercontent.com/38091261/126499331-e41946c4-4e61-4b5e-8b7f-73efb9cd8d3f.gif)

When syncing data from Nautobot to Cloudvision, the tag data in Nautobot is copied into User Tags in Cloudvision. You can watch the video below for an example.

![tocv_sync](https://user-images.githubusercontent.com/38091261/126499484-2e4c4feb-0492-4dc6-abb6-a092701c81ed.gif)


## Contributing

Pull requests are welcomed and automatically built and tested against multiple version of Python and multiple version of Nautobot through TravisCI.

The project is packaged with a light development environment based on `docker-compose` to help with the local development of the project and to run the tests within TravisCI.

The project is following Network to Code software development guideline and is leveraging:

- Black, Pylint, Bandit and pydocstyle for Python linting and formatting.
- Django unit test to ensure the plugin is working properly.

### Development Environment

The development environment can be used in 2 ways. First, with a local poetry environment if you wish to develop outside of Docker. Second, inside of a docker container.

#### Invoke tasks

The [PyInvoke](http://www.pyinvoke.org/) library is used to provide some helper commands based on the environment.  There are a few configuration parameters which can be passed to PyInvoke to override the default configuration:

* `nautobot_ver`: the version of Nautobot to use as a base for any built docker containers (default: develop-latest)
* `project_name`: the default docker compose project name (default: aristacv-sync)
* `python_ver`: the version of Python to use as a base for any built docker containers (default: 3.6)
* `local`: a boolean flag indicating if invoke tasks should be run on the host or inside the docker containers (default: False, commands will be run in docker containers)
* `compose_dir`: the full path to a directory containing the project compose files
* `compose_files`: a list of compose files applied in order (see [Multiple Compose files](https://docs.docker.com/compose/extends/#multiple-compose-files) for more information)

Using PyInvoke these configuration options can be overridden using [several methods](http://docs.pyinvoke.org/en/stable/concepts/configuration.html).  Perhaps the simplest is simply setting an environment variable `INVOKE_ARISTACV-SYNC_VARIABLE_NAME` where `VARIABLE_NAME` is the variable you are trying to override.  The only exception is `compose_files`, because it is a list it must be overridden in a yaml file.  There is an example `invoke.yml` in this directory which can be used as a starting point.

#### Local Poetry Development Environment

1.  Copy `development/creds.example.env` to `development/creds.env` (This file will be ignored by git and docker)
2.  Uncomment the `POSTGRES_HOST`, `REDIS_HOST`, and `NAUTOBOT_ROOT` variables in `development/creds.env`
3.  Create an invoke.yml with the following contents at the root of the repo:

```shell
---
aristacv_sync:
  local: true
  compose_files:
    - "docker-compose.requirements.yml"
```

3.  Run the following commands:

```shell
poetry shell
poetry install
export $(cat development/dev.env | xargs)
export $(cat development/creds.env | xargs)
```

4.  You can now run nautobot-server commands as you would from the [Nautobot documentation](https://nautobot.readthedocs.io/en/latest/) for example to start the development server:

```shell
nautobot-server runserver 0.0.0.0:8080 --insecure
```

Nautobot server can now be accessed at [http://localhost:8080](http://localhost:8080).

#### Docker Development Environment

This project is managed by [Python Poetry](https://python-poetry.org/) and has a few requirements to setup your development environment:

1.  Install Poetry, see the [Poetry Documentation](https://python-poetry.org/docs/#installation) for your operating system.
2.  Install Docker, see the [Docker documentation](https://docs.docker.com/get-docker/) for your operating system.

Once you have Poetry and Docker installed you can run the following commands to install all other development dependencies in an isolated python virtual environment:

```shell
poetry shell
poetry install
invoke start
```

Nautobot server can now be accessed at [http://localhost:8080](http://localhost:8080).

### CLI Helper Commands

The project is coming with a CLI helper based on [invoke](http://www.pyinvoke.org/) to help setup the development environment. The commands are listed below in 3 categories `dev environment`, `utility` and `testing`.

Each command can be executed with `invoke <command>`. Environment variables `INVOKE_ARISTACV-SYNC_PYTHON_VER` and `INVOKE_ARISTACV-SYNC_NAUTOBOT_VER` may be specified to override the default versions. Each command also has its own help `invoke <command> --help`

#### Docker dev environment

```no-highlight
  build            Build all docker images.
  debug            Start Nautobot and its dependencies in debug mode.
  destroy          Destroy all containers and volumes.
  restart          Restart Nautobot and its dependencies.
  start            Start Nautobot and its dependencies in detached mode.
  stop             Stop Nautobot and its dependencies.
```

#### Utility

```no-highlight
  cli              Launch a bash shell inside the running Nautobot container.
  create-user      Create a new user in django (default: admin), will prompt for password.
  makemigrations   Run Make Migration in Django.
  nbshell          Launch a nbshell session.
```

#### Testing

```no-highlight
  bandit           Run bandit to validate basic static code security analysis.
  black            Run black to check that Python files adhere to its style standards.
  flake8           This will run flake8 for the specified name and Python version.
  pydocstyle       Run pydocstyle to validate docstring formatting adheres to NTC defined standards.
  pylint           Run pylint code analysis.
  tests            Run all tests for this plugin.
  unittest         Run Django unit tests for the plugin.
```

## Questions

For any questions or comments, please check the [FAQ](FAQ.md) first and feel free to swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #networktocode).
Sign up [here](http://slack.networktocode.com/)

## Screenshots

This screenshot shows the Cloudvision to Nautobot home page. This contains a list of all the system tags from Cloudvision and how they map to custom fields in Nautobot. This also displays current plugin configuration and sync history.

![cv_to_naut](https://user-images.githubusercontent.com/38091261/124859726-03557800-df76-11eb-9622-af4c29ba8d40.PNG)

This screenshow shows the Nautobot to Cloudvision home page. It also contains data mappings, plugin configuration and sync history.

![naut_to_cv](https://user-images.githubusercontent.com/38091261/124859903-55969900-df76-11eb-87c4-64ca2616bffe.PNG)

