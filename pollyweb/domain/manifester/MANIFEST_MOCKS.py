from PW_DOMAIN import MANIFEST

from pollyweb import UTILS


class MANIFEST_MOCKS():
    

    @classmethod
    def MockYaml(cls, domain:str='', name:str='', smallIcon:str='', bigIcon:str='') -> str:
        
        obj = {
            "Identity": {
                "Domain": domain,
                "Name": name,
                "SmallIcon": smallIcon,
                "BigIcon": bigIcon,
                "Translations": [{
                    "Language": "en-us",
                    "Translation": "<translationOf(any-host.org)>"
                },{
                    "Language": "pt-br",
                    "Translation": "<translationOf(any-host.org)>"
                }]
            },
            
            "Trusts": [
                {
                    "Action": "GRANT",
                    "Role": "VAULT",
                    "Query": "any-authority.org/<code>",
                    "Domain": "any-vault.org"
                },
                {
                    "Action": "GRANT",
                    "Query": "any-authority.org/<code>"
                },
                {
                    "Action": "GRANT",
                    "Role": "CONSUMER",
                    "Query": "pollyweb.org/PAY/COLLECTOR",
                    "Domain": "any-seller.org"
                },
                {
                    "Action": "GRANT",
                    "Roles": ["VAULT", "CONSUMER"],
                    "Queries": ["pollyweb.org/PAY/PAYMENT"],
                    "Domain": "any-payer.org"
                },
                {
                    "Action": "GRANT",
                    "Roles": ["VAULT","CONSUMER"],
                    "Queries": [
                        "pollyweb.org/PAY/COLLECTOR", 
                        "pollyweb.org/PAY/PAYMENT"
                    ],
                    "Domain": "any-collector.org"
                }
            ],

            "Codes": [
                {
                    "Path": "/BANK",
                    "Delegator": "pollyweb.org"
                },
                {
                    "Path": "/<code>",
                    "Name": "<translationOf(any-authority.org/<code>)>",
                    "Schemas": [{
                        "Output": "QR",
                        "Version": "1.0"
                    }]
                },
                {
                    "Path": "/<offer>",
                    "Name": "<translationOf(any-authority.org/<offer>)>",
                    "Schemas": [{
                        "Output": "QR",
                        "Version": "1.0"
                    }]
                },
                {
                    "Path": "/PAY/PAYER",
                },
                {
                    "Path": "/PAY/PAYMENT",
                },
                {
                    "Path": "/PAY/COLLECTOR",
                },
                {
                    "Path": "/BANK/BALANCE",
                    "Delegator": "pollyweb.org",
                    "Name": "Bank account balance",
                    "Translations": [{
                        "Language": "pt-br",
                        "Translation": "Saldo bancário"
                    }],
                    "Schemas": [
                        {
                            "Output": "SHARE",
                            "Version": '1',
                            "Format": {
                                "properties": {
                                    "Balance": {
                                        "type": "number"
                                    }
                                }
                            }
                        }
                    ]
                }
            ]
        }
        return UTILS.ToYaml(obj)


    @classmethod
    def MockManifest(cls, 
                     domain:str='any-domain2.org', 
                     name:str='Any Domain',
                     smallIcon:str="https://example.com/small-icon.png",
                     bigIcon:str="https://example.com/big-icon.png"
                     ) -> MANIFEST:
        
        yaml = cls.MockYaml(
            domain=domain, 
            name=name, 
            smallIcon=smallIcon,
            bigIcon=bigIcon)

        return MANIFEST(yaml)
