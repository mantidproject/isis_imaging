from concurrent.futures import Future
from concurrent.futures import ProcessPoolExecutor
from logging import getLogger
from typing import Optional

import socketio
from requests_futures.sessions import FuturesSession

from mantidimaging.core.utility.savu_interop.webapi import (
    SERVER_URL,
    SERVER_WS_URL,
    PLUGINS_WITH_DETAILS_URL,
    WS_JOB_STATUS_NAMESPACE,
)

data: Optional[Future] = None
sio_client: Optional[socketio.Client] = None


async def prepare_data():
    # TODO consider moving to CORE as this is not a GUI feature really
    session = FuturesSession(executor=ProcessPoolExecutor(max_workers=1))

    response: Future = session.get(f"{SERVER_URL}/{PLUGINS_WITH_DETAILS_URL}")
    print("Preparing SOCKET IO connection")
    global sio_client
    sio_client = socketio.Client()

    # make output from the communication libs a bit less verbose
    getLogger("engineio.client").setLevel("WARNING")
    getLogger("socketio.client").setLevel("WARNING")
    getLogger("urllib3.connectionpool").setLevel("INFO")

    try:
        sio_client.connect(SERVER_WS_URL, namespaces=[WS_JOB_STATUS_NAMESPACE])
    except socketio.exceptions.ConnectionError as err:
        getLogger(__name__).warning(f"Could not connect to SAVU Socket IO, error: {err}")

    global data

    data = response
