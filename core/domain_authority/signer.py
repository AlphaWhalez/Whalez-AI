from .manager import DomainAuthority


class CertificateSigner:
    def __init__(self, cfg="config/tls.settings.json"):
        self.da = DomainAuthority(cfg)

    def ensure(self):
        return self.da.issue_server_cert()
