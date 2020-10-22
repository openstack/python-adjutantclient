# Copyright (C) 2016 Catalyst IT Ltd
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

from urllib import parse

from adjutantclient.common import base


class QuotaManager(base.BaseManager):

    def get(self, regions=None):
        """Gets data about current quota settings"""
        url = '/openstack/quotas/'
        if regions:
            url += '?%s' % parse.urlencode({
                'regions': regions
            })
        return self.client.get(url).json()

    def update(self, size, regions=None):
        """Updates the quota to a specified size.

        If region is not set it will update all regions
        """
        url = '/openstack/quotas/'
        fields = {
            'size': size,
            'regions': regions
        }
        return self.client.post(url, data=fields)
