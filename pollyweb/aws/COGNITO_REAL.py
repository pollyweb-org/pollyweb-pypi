from __future__ import annotations

from LOG import LOG

import boto3
cognito_idp = boto3.client('cognito-idp')


class COGNITO_REAL:
    
    @classmethod
    def CreateUser(cls, username, password, clientAlias='COGNITO'): 

        import os
        clientId = os.environ[clientAlias]

        sign_up_params = {
            'ClientId': clientId,
            'Username': username,
            'Password': password,
            'UserAttributes': [
                # Example: {'Name': 'custom:your_custom_attribute', 'Value': 'custom_value'}
                # Add any required attributes according to your user pool's configuration
            ]
        }

        try:
            # Call the sign_up method
            response = cognito_idp.sign_up(**sign_up_params)
            LOG.Print("User created successfully:", response)

        except cognito_idp.exceptions.UsernameExistsException:
            LOG.RaiseValidationException("This username already exists.")

        except Exception as e:
            LOG.RaiseException(e)