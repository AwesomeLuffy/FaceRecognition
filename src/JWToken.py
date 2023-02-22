import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta
import re


class JWToken:
    """Class to manage the JWT token
    Translated from my code in PHP
    See : https://github.com/AwesomeLuffy/SimpleToken/blob/master/src/JWToken.php
    """

    def __init__(self, head, payl, sig):
        self.header: str = head
        self.payload: str = payl
        self.signature: str = sig

    @staticmethod
    def generate_jw_token(header, payload, secret, validity=7):
        if validity < 1:
            raise Exception("Validity should be 1 day or higher!")
        now = datetime.now()
        payload["iat"] = now.timestamp()
        payload["exp"] = (now + timedelta(days=validity)).timestamp()
        header_encoded = JWToken.b64_encode(json.dumps(header))
        payload_encoded = JWToken.b64_encode(json.dumps(payload))
        signature = JWToken.generate(header_encoded, payload_encoded, secret)
        signature = JWToken.b64_encode(signature)
        return JWToken(header_encoded, payload_encoded, signature)

    @staticmethod
    def generate(header_encoded, payload_encoded, secret):
        """Generate the signature of the token
        :param header_encoded: the header encoded in base64
        :param payload_encoded: the payload encoded in base64
        :param secret: the secret key
        :return: the signature
        """
        secret_encoded = JWToken.b64_encode(secret).encode('utf-8')
        # Create hmac with sha256 and secret
        dig = hmac.new(secret_encoded, msg=f"{header_encoded}.{payload_encoded}".encode('utf-8'),
                       digestmod=hashlib.sha256).digest()
        return base64.urlsafe_b64encode(dig).decode()

    def check_token_signature(self, secret):
        return JWToken.b64_encode(JWToken.generate(self.header, self.payload, secret)) == self.signature

    def is_expired(self):
        payload = self.read_payload()
        now = datetime.now()
        return payload["exp"] < now.timestamp()

    @staticmethod
    def is_valid(token):
        return bool(re.match('^[a-zA-Z0-9\-\_\=]+\.[a-zA-Z0-9\-\_\=]+\.[a-zA-Z0-9\-\_\=]+$', token))

    def __str__(self):
        return f"{self.header}.{self.payload}.{self.signature}"

    @staticmethod
    def token_from_string(token):
        if JWToken.is_valid(token):
            token_exploded = token.split(".")
            return JWToken(token_exploded[0], token_exploded[1], token_exploded[2])
        return None

    @staticmethod
    def b64_encode(data: str) -> str:
        # 1 - Encode in base64 the data (payload or header)
        # 2 - Replace + to - & / to _ with strtr (Not in JWT chart)
        # 3 - Remove the "=" with trim (Not in JWT chart)
        return base64.urlsafe_b64encode(data.encode('utf-8')).rstrip(b"=").decode('utf-8')

    def read_header(self) -> dict:
        return json.loads(base64.urlsafe_b64decode(self.header + '==').decode('utf-8'))

    def read_payload(self) -> dict:
        return json.loads(base64.urlsafe_b64decode(self.payload + '==').decode('utf-8'))
