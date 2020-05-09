# Copyright (c) 2016 Catalyst IT Ltd.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json
import logging

from osc_lib.command import command


LOG = logging.getLogger(__name__)


class Status(command.Command):
    """Lists adjutant tasks. """

    def take_action(self, parsed_args):
        client = self.app.client_manager.admin_logic

        status = client.status.get().json()
        print(json.dumps(status, indent=2))
