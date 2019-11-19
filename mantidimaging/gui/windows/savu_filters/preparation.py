import atexit
import os
import subprocess
import threading

from concurrent.futures import Future, ProcessPoolExecutor
from logging import getLogger
from typing import Optional, List

import socketio
from requests_futures.sessions import FuturesSession

from mantidimaging.core.utility.savu_interop.webapi import (PLUGINS_WITH_DETAILS_URL, SERVER_URL, SERVER_WS_URL,
                                                            WS_JOB_STATUS_NAMESPACE)

from mantidimaging.core.configs.savu_backend_docker import RemoteConfig, DevelopmentRemoteConfig, RemoteConstants

data: Optional[Future] = None
sio_client: Optional[socketio.Client] = None

LOG = getLogger(__name__)


class BackgroundService(threading.Thread):
    def __init__(self, docker_exe, args: List):
        super().__init__()
        self.docker_exe = docker_exe
        self.args = args
        self.callback = lambda output: LOG.debug(output)
        self.error_callback = lambda err_code, output: LOG.debug(f"BackgroundService error: {output}")
        self.success_callback = lambda: LOG.debug("BackgroundService success.")
        self.exit_code: int = -4444
        self.close_now = False
        self.docker_id = None
        self.close_intended = False
        self.process: Optional[subprocess.Popen] = None

    def run(self) -> None:
        self.process = subprocess.Popen(self.args, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while self.process.poll() is None:
            output = self.process.stdout.readline()
            if b"* Serving Flask app " in output:
                self.success()
            if output == '' and self.process.poll() is not None:
                break
            if output:
                self.callback(output)
        self.exit_code = self.process.poll()
        self.determine_run_outcome()

    def determine_run_outcome(self) -> int:
        if self.close_intended and self.exit_code == 0:
            self.success_callback()
        else:
            # docker could not be started, try to connect to an already running container
            prepare_data()
            if sio_client is not None and sio_client.sid is not None:
                LOG.info("Connected to SAVU Docker backend that was already running.")
                self.success_callback()
            else:
                self.error_callback(self.exit_code, self.process.stderr.readlines())

        return self.exit_code

    def success(self):
        prepare_data()
        docker_id = subprocess.check_output("docker ps | awk -F ' ' 'END {print $1}'", shell=True)
        self.docker_id = docker_id.decode("utf-8")

    def close(self):
        self.close_intended = True
        self.process.terminate()
        subprocess.call(f'{self.docker_exe} kill {self.docker_id}', shell=True)
        sio_client.reconnection = False
        sio_client.disconnect()


def is_exe(fpath):
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


def find_docker():
    docker_locations = [
        "docker",  # if in PATH
        "/snap/bin/docker",  # if installed via SNAP
        "/usr/bin/docker",  # if installed via apt
    ]
    for location in docker_locations:
        if is_exe(location):
            return location


async def prepare_backend() -> BackgroundService:

    docker_exe = find_docker()
    docker_args = [
        docker_exe,
        "run",
        "--network=host",
        "-e",
        f"PUID={subprocess.check_output(['id','-u']).decode('utf-8').strip()}",
        "-e",
        f"PGID={subprocess.check_output(['id','-g']).decode('utf-8').strip()}",
    ]

    if RemoteConfig.NVIDIA_RUNTIME["active"]:
        docker_args.append(RemoteConfig.NVIDIA_RUNTIME["value"])

    # if running in development mode, mount hebi and savu sources
    if RemoteConfig.DEVELOPMENT:
        docker_args.append("-v")
        docker_args.append(f"{DevelopmentRemoteConfig.HEBI_SOURCE_DIR}:{RemoteConstants.HEBI_SOURCE_DIR}")

        docker_args.append("-v")
        docker_args.append(f"{DevelopmentRemoteConfig.SAVU_SOURCE_DIR}:{RemoteConstants.SAVU_SOURCE_DIR}")

    docker_args.append("-v")
    docker_args.append(f"{RemoteConfig.LOCAL_DATA_DIR}:{RemoteConstants.DATA_DIR}")
    docker_args.append("-v")
    docker_args.append(f"{RemoteConfig.LOCAL_OUTPUT_DIR}:{RemoteConstants.OUTPUT_DIR}")

    docker_args.append("-t")

    if RemoteConfig.DEVELOPMENT:
        docker_args.append(f"{RemoteConfig.IMAGE_NAME}:{DevelopmentRemoteConfig.DEVELOPMENT_LABEL}")
    else:
        docker_args.append(RemoteConfig.IMAGE_NAME)

    docker_args = list(map(lambda arg: arg.replace("~", os.path.expanduser("~")) if "~" in arg else arg, docker_args))
    LOG.debug(f"Starting DOCKER service with args: {' '.join(docker_args)}")
    process = BackgroundService(docker_exe, docker_args)
    return process


def print_output(process):
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(f"DOCKER Backend Output:\n{output}")


def prepare_data():
    # TODO consider moving to CORE as this is not a GUI feature really
    session = FuturesSession(executor=ProcessPoolExecutor(max_workers=1))

    response: Future = session.get(f"{SERVER_URL}/{PLUGINS_WITH_DETAILS_URL}")
    LOG.debug("Preparing SOCKET IO connection")

    global data
    data = response

    global sio_client
    sio_client = socketio.Client()
    atexit.register(lambda sio: sio.disconnect(), sio_client)

    # make output from the communication libs a bit less verbose
    getLogger("engineio.client").setLevel("WARNING")
    getLogger("socketio.client").setLevel("WARNING")
    getLogger("urllib3.connectionpool").setLevel("INFO")

    try:
        sio_client.connect(SERVER_WS_URL, namespaces=[WS_JOB_STATUS_NAMESPACE])
    except socketio.exceptions.ConnectionError as err:
        LOG.info(f"SAVU backend could not be connected.")
        LOG.debug(f"Could not connect to SAVU Socket IO, error: {err}")
