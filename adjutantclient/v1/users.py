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


from six.moves.urllib import parse

from adjutantclient.common import base


class User(base.Resource):
    def __repr__(self):
        return "<User %s>" % self._info

    def invite(self, **fields):
        return self.manager.create(self.identifier, **fields)

    def get(self):
        # set_loaded() first ... so if we have to bail, we know we tried.
        self._loaded = True
        if not hasattr(self.manager, 'get'):
            return

        new = self.manager.get(self.identifier)
        if new:
            self._add_details(new._info)

    @property
    def identifier(self):
        return '%s/%s' % (self.stack_name, self.id)


class UserManager(base.ManagerWithFind):
    resource_class = User

    def get(self, user):
        return self._get("/openstack/users/%s" % base.getid(user))

    def list(self, **kwargs):
        """Get a list of users.

        :param limit: maximum number of users to return
        :param marker: begin returning users that appear later in the user
                       list than that represented by this user id
        :rtype: list of :class:`User`
        """
        def paginate(params):
            '''Paginate users, even if more than API limit.'''
            current_limit = int(params.get('limit') or 0)
            url = 'openstack/users?%s' % parse.urlencode(params, True)
            users = self._list(url, 'users')
            for user in users:
                yield user

            num_users = len(users)
            remaining_limit = current_limit - num_users
            if remaining_limit > 0 and num_users > 0:
                params['limit'] = remaining_limit
                params['marker'] = user.id
                for stack in paginate(params):
                    yield stack

        params = {}
        # if 'filters' in kwargs:
        #     filters = kwargs.pop('filters')
        #     params.update(filters)

        for key, value in (kwargs).items():
            if value:
                params[key] = value

        return paginate(params)

    def invite(self, username, email, role_list):
        """Invite a user to the current project."""

        fields = {
            'username': username,
            'email': email,
            'roles': role_list
        }
        return self.client.post('openstack/users', data=fields)

    def cancel(self, user_id):
        """Cancel a user invite task."""
        url = 'openstack/users/%s' % user_id
        return self._delete(url)

    def revoke(self, user_id):
        """Revoke all user roles on project."""
        # NOTE(adriant): This doesn't work yet.
        # Uses the same endpoint as cancel, but doesn't
        # yet actually revoke all roles if an actual user
        # rather than an invite.
        return self.cancel(user_id)

    def password_forgot(self, email, username=None):
        """Forgot password email submission."""
        params = {"email": email}
        if username:
            params['username'] = username

        return self.client.post("openstack/users/password-reset",
                                data=params)

    def password_force_reset(self, email):
        """Force a password reset for a user.

        This is an admin only function.
        """
        params = {"email": email}
        return self.client.post(
            "openstack/users/password-set", data=params)
