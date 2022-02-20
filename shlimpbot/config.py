import json

from jsonpath_ng import parse


class Config:
    def __init__(self, filename):
        self._config = {}
        self._filename = filename
        with open(filename) as config_file:
            self._config = json.load(config_file)

    def write_config(self):
        with open(self._filename, 'w') as config_file:
            json.dump(self._config, config_file)

    def get_global(self, path):
        jsonpath_expr = parse(f'$.global.{path}')
        return jsonpath_expr.find(self._config)[0].value

    def get_server(self, server_id, path):
        jsonpath_expr = parse(f'$.servers."{server_id}".{path}')
        return jsonpath_expr.find(self._config)[0].value

    def get_user(self, server_id, user_id, path):
        jsonpath_expr = parse(f'$.users."{user_id}"."{server_id}".{path}')
        return jsonpath_expr.find(self._config)[0].value

    def set_global(self, path, data):
        jsonpath_expr = parse(f'$.global.{path}')
        jsonpath_expr.update_or_create(self._config, data)
        self.write_config()
        return self.get_global(path)

    def set_server(self, server_id, path, data):
        jsonpath_expr = parse(f'$.servers."{server_id}".{path}')
        jsonpath_expr.update_or_create(self._config, data)
        self.write_config()
        return self.get_server(server_id, path)

    def set_user(self, server_id, user_id, path, data):
        jsonpath_expr = parse(f'$.users."{user_id}"."{server_id}".{path}')
        jsonpath_expr.update_or_create(self._config, data)
        self.write_config()
        return self.get_user(server_id, user_id, path)
