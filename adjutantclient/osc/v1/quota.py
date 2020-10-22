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

import logging

from osc_lib.command import command
from osc_lib.i18n import _


LOG = logging.getLogger(__name__)


class QuotaShow(command.Lister):
    """Displays current quota information.

    If not given a region it will print basic details of the state of
    the quotas. If given a region it will print all details for it.
    """

    def get_parser(self, prog_name):
        parser = super(QuotaShow, self).get_parser(prog_name)

        parser.add_argument(
            '--region', metavar='<region>', required=False,
            help=_("Single region to display details on."))

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.admin_logic

        if not parsed_args.region:
            quota_data = client.quota.get()

            headers = [
                'Region', 'Current Size', 'Preapproved Sizes']

            rows = []
            for region in quota_data['regions']:
                rows.append([
                    region['region'],
                    region['current_quota_size'],
                    ", ".join(region['quota_change_options']),
                ])
            return headers, rows
        else:
            quota_data = client.quota.get(regions=parsed_args.region)
            headers = ['Service', 'Resource', 'Current Quota', 'Current Usage']
            region = quota_data['regions'][0]

            rows = []
            for service, service_detail in region['current_usage'].items():
                for resource, value in service_detail.items():
                    current_quota = region['current_quota'][service].get(
                        resource)
                    rows.append([service, resource, current_quota, value])
            return headers, rows


class QuotaSizes(command.Lister):
    """Displays possible quota sizes."""

    def take_action(self, parsed_args):
        client = self.app.client_manager.admin_logic

        quota_data = client.quota.get()

        headers = [
            'Size Name', 'Service', 'Resource', 'Value']

        rows = []
        for size, size_details in quota_data['quota_sizes'].items():
            for service, service_details in size_details.items():
                for resource, value in service_details.items():
                    rows.append([size, service, resource, value])

        return headers, rows


class QuotaTasks(command.Lister):
    """Displays quota tasks."""

    def take_action(self, parsed_args):
        client = self.app.client_manager.admin_logic

        quota_data = client.quota.get()

        headers = [
            'ID', 'Regions', 'Proposed Size', 'Requested By', 'Created On',
            'valid', 'status',
        ]

        rows = []
        for task in quota_data['active_quota_tasks']:
            rows.append([
                task['id'],
                ", ".join(task['regions']),
                task['size'],
                task['request_user'],
                task['task_created'],
                task['valid'],
                task['status'],
            ])

        return headers, rows


class QuotaUpdate(command.Command):
    """Submits a quota update task."""

    def get_parser(self, prog_name):
        parser = super(QuotaUpdate, self).get_parser(prog_name)

        parser.add_argument(
            'size', metavar='<size>',
            help=_("The size to update to."))
        parser.add_argument(
            '--regions', metavar='<regions>', nargs='+', required=False,
            help=_("Regions to update the quota on."))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.admin_logic
        if parsed_args.regions:
            status = client.quota.update(parsed_args.size, parsed_args.regions)
        else:
            # NOTE(amelia): regions aren't set the API will update all of them
            status = client.quota.update(parsed_args.size)
        status_code = status.status_code

        if status_code == 200:
            if parsed_args.regions:
                print("Regions: %s quota updated to size %s."
                      % (parsed_args.regions, parsed_args.size))
            else:
                print("All regions' quota updated to size %s."
                      % (parsed_args.size))
        elif status_code == 202:
            print("The task has been created however requires admin approval"
                  " before executing.")
