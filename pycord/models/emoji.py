"""
MIT License

Copyright (c) 2017 Kyb3r

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from .core import Snowflake, Serializable
from ..models.role import Role
from ..utils import Collection


class Emoji(Snowflake, Serializable):
    __slots__ = ('guild', 'id', 'name', 'roles', 'client')

    def __init__(self, guild, data=None):
        if data is None:
            data = {}
        self.guild = guild
        self.client = guild.client
        self.id = int(data.get('id', 0))
        self.name = data.get('name', '')
        self.require_colons = bool(data.get('require_colons', False))
        self.managed = bool(data.get('managed', False))
        self.roles = Collection(Role)
        self.from_dict(data)

    def from_dict(self, data):
        self.id = int(data.get('id', 0))
        self.name = data.get('name')

        for role in data.get('roles', []):
            if role:
                if self.guild._roles.has(role):
                    rolee = self.guild._roles.get(role)
                    self.roles.add(rolee)

    def delete(self, reason=None):
        return self.client.api.delete_custom_emoji(self.guild, self, reason)
