import mailbox
import os
import gzip
import rfc822
from gettext import gettext as _

import mailpile.mailboxes
import mailpile.mailboxes.maildir as maildir


class MailpileMailbox(maildir.MailpileMailbox):
    """A Gmvault class that supports pickling and a few mailpile specifics."""

    @classmethod
    def parse_path(cls, config, fn, create=False):
        if os.path.isdir(fn) and os.path.exists(os.path.join(fn, 'db')):
            return (fn, )
        raise ValueError('Not a Gmvault: %s' % fn)

    def __init__(self, dirname, factory=rfc822.Message, create=True):
        maildir.MailpileMailbox.__init__(self, dirname, factory, create)
        self._paths = {'db': os.path.join(self._path, 'db')}
        self._toc_mtimes = {'db': 0}

    def get_file(self, key):
        """Return a file-like representation or raise a KeyError."""
        fname = self._lookup(key)
        if fname.endswith('.gz'):
            f = gzip.open(os.path.join(self._path, fname), 'rb')
        else:
            f = open(os.path.join(self._path, fname), 'rb')
        return mailbox._ProxyFile(f)

    def _refresh(self):
        """Update table of contents mapping."""
        # Refresh toc
        self._toc = {}
        for path in self._paths:
            for dirpath, dirnames, filenames in os.walk(self._paths[path]):
                for filename in [f for f in filenames
                                 if f.endswith(".eml.gz")
                                 or f.endswith(".eml")]:
                    self._toc[filename] = os.path.join(dirpath, filename)


mailpile.mailboxes.register(50, MailpileMailbox)
