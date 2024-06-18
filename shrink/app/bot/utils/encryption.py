# ШИФРОВАНИЕ XOR + HEX
import uuid

class Encryption():
    def __init__(self) -> None:
        pass
    
    def _crypto_xor(self, password: str, secret: str) -> str:
        new_chars = list()
        i = 0
        for num_chr in (ord(c) for c in password):
            num_chr ^= ord(secret[i])
            new_chars.append(num_chr)
            i += 1
            if i >= len(secret):
                i = 0

        return ''.join(chr(c) for c in new_chars)
    
    def _generate_secret(self) -> str:
        return str(uuid.uuid1())

    # шифровка значения по ключу
    def encrypt(self, password: str) -> tuple[str, str]:
        secret = self._generate_secret()
        return self._crypto_xor(password, secret).encode('utf-8').hex(), secret

    # расшифровка значения по ключу
    def decrypt(self, password_hex: str, secret: str) -> str:
        password = bytes.fromhex(password_hex).decode('utf-8')
        return self._crypto_xor(password, secret)
    



# '''EXAMPLE'''

# password = 'password'
# encryption = Encryption()

# encrypted_password, secret  = encryption.encrypt(password)
# # print(encrypted_password)
# decrypted_password = encryption.decrypt("11004717425f4b06", secret)
# print(decrypted_password)
