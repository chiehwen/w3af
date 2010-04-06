import re
from plugins.attack.payloads.base_payload import base_payload

class mysql_config_directory(base_payload):
    '''
    This payload finds MySQL configuration directory.
    '''
    def api_read(self):
        result = []
        paths = []

        def parse_mysql_init( mysql_init ):
            directory = re.search('(?<=$0: WARNING: )(.*?)my.cnf cannot', mysql_init)
            if directory:
                return directory.group(1)
            else:
                return ''

        def check_mysql_config_dir( mysql ):
            my = self.shell.read( mysql+ 'my.cnf')
            if my != '':
                return True
            else:
                return False

        paths.append( parse_mysql_init( self.shell.read('/etc/init.d/mysql') ) )
        paths.append('/etc/mysql/')
        paths.append('/etc/')
        paths.append('/opt/local/etc/mysql5/')
        paths.append('/var/lib/mysql/')

        folders = self.exec_payload('users_folders')
        for folder in folders:
            paths.append(folder)

        for path in paths:
            if check_mysql_config_dir(path):
                result.append(path)

        result = list(set(result))
        result = [p for p in result if p != '']
        return result
        
    def run_read(self):
        result = self.api_read()
        if result == [ ]:
            result.append('MySQL configuration directory not found.')
        return result
        
