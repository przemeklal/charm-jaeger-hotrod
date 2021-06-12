#!/usr/bin/env python3
# Copyright 2021 Przemysław Lal
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charm the service.

Refer to the following post for a quick-start guide that will help you
develop a new k8s charm using the Operator Framework:

    https://discourse.charmhub.io/t/4208
"""

import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus

logger = logging.getLogger(__name__)


class JaegerHotrodCharm(CharmBase):
    """Charm the service."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.hotrod_pebble_ready, self._on_hotrod_pebble_ready)
        self.framework.observe(self.on.config_changed, self._on_config_changed)

        self.framework.observe(self.on["distributed-tracing"].relation_changed,
                               self._on_jaeger_relation_changed)

        self._stored.set_default(jaeger_agent_host="127.0.0.1")
        self._stored.set_default(jaeger_agent_port="6831")

    def _on_hotrod_pebble_ready(self, event):
        self._update_env_and_run()
        self.unit.status = ActiveStatus()

    def _update_env_and_run(self):
        self.unit.status = MaintenanceStatus('Updating hotrod configuration and restarting,'
                                             'new agent endpoint is {}:{}'
                                             .format(self._stored.jaeger_agent_host,
                                                     self._stored.jaeger_agent_port))

        jeager_ui_address = "http://{}:16686".format(self._stored.jaeger_agent_host)

        pebble_layer = {
            "summary": "hotrod layer",
            "description": "pebble config layer for hotrod",
            "services": {
                "hotrod": {
                    "override": "replace",
                    "summary": "hotrod",
                    "command": "/go/bin/hotrod-linux all -j {}".format(jeager_ui_address),
                    "startup": "enabled",
                    "environment": {
                        "JAEGER_AGENT_HOST": self._stored.jaeger_agent_host,
                        "JAEGER_AGENT_PORT": self._stored.jaeger_agent_port,
                    },
                }
            },
        }

        container = self.unit.get_container("hotrod")
        container.add_layer("hotrod", pebble_layer, combine=True)

        if container.get_service("hotrod").is_running():
            container.stop("hotrod")
        container.start("hotrod")

        self.unit.status = ActiveStatus()

    def _on_jaeger_relation_changed(self, event):

        self.unit.status = MaintenanceStatus(
            "Updating jaeger relation"
        )

        data = event.relation.data[event.app]

        agent_host = data.get("agent-address")
        agent_port = data.get("port")

        logger.debug("jaeger relation data %s", data)

        self._stored.jaeger_agent_host = agent_host
        self._stored.jaeger_agent_port = agent_port

        self._update_env_and_run()

        self.unit.status = ActiveStatus()

    def _on_config_changed(self, _):
        return


if __name__ == "__main__":
    main(JaegerHotrodCharm)
