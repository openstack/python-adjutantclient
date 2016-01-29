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

from stacktaskclient.openstack.common.apiclient import base


class Token(base.Resource):
    pass


class TokenParam(base.Resource):
    pass


class TokenManager(base.BaseManager):
    resource_class = Token

    def show(self, token_id):
        """Get details on a particular token object"""
        url = 'tokens/%s' % token_id
        return [self._get(url)]

    def submit(self, token_id, parameters):
        url = 'tokens/%s' % token_id
        json = parameters
        return self._post(url, json)

    def reissue(self, task_id):
        """ Given a task id, reissues the tokens associated with that task """
        url = 'tokens'
        json = {
            'task': task_id
        }
        return self._post(url, json)