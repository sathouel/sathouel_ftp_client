import os
from ftplib import FTP

import paramiko


class Client:

    def __init__(self, host, username, password, port=22, sftp=False):
        self.host, self.username, self.password, self.port = host, username, password, port
        self.sftp = sftp

        self._client = self.init_sftp_client() if self.sftp else self.init_ftp_client()

    @property
    def ftp_client(self):
        return self._client

    def init_ftp_client(self):
        if not self.username or not self.password or not self.host:
            raise ValueError('Please set host, user and password to init Genial Client')

        if hasattr(self, '_client'):
            return self._client

        self._client = FTP(self.host, self.username, self.password)
        return self._client

    def init_sftp_client(self):
        if not self.username or not self.password or not self.host:
            raise ValueError('Please set host, user and password to init Genial Client')

        if hasattr(self, '_client'):
            return self._client

        transport = paramiko.Transport((self.host, self.port if self.port else 22))
        transport.connect(None, self.username, self.password)
        self._client = paramiko.SFTPClient.from_transport(transport)

        return self._client

    def fetch_remote_filepaths(self, remote_dirpath):
        if not self.sftp:
            filepaths = []
            self.ftp_client.retrlines('NLST {}'.format(remote_dirpath), filepaths.append)
            if remote_dirpath and remote_dirpath != '.':
                filepaths = [
                    os.path.join(remote_dirpath, filename) if os.path.dirname(filename) != remote_dirpath else filename
                    for filename in filepaths
                    if filename not in ['.', '..']
                ]
            return filepaths
        else:
            filenames = self.ftp_client.listdir(remote_dirpath)
            filepaths = [os.path.join(remote_dirpath, filename) for filename in filenames]
            return filepaths

    def fetch_remote_file_content(self, remote_filepath, tmp_filename):
        if not self.sftp:
            file_obj = open(tmp_filename, 'wb')
            self.ftp_client.retrbinary('RETR {}'.format(remote_filepath), file_obj.write)
            file_obj.close()
            file_obj = open(tmp_filename, 'rb')
            file_content = file_obj.read()
            file_obj.close()
            os.remove(tmp_filename)
            return file_content
        else:
            file_obj = self.ftp_client.open(remote_filepath, mode='rb')
            file_content = file_obj.read()
            file_obj.close()
            return file_content

    def send_file_to_server(self, remote_path, local_filepath):
        if not self.sftp:
            file_obj = open(local_filepath, 'rb')
            self.ftp_client.storbinary('STOR {}'.format(remote_path), file_obj)
            file_obj.close()
            return
        else:
            self.ftp_client.put(local_filepath, remote_path)
            return

