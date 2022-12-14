from base64 import b64decode, b64encode
from django.utils import timezone
from datetime import datetime, timedelta
import uuid
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from hvac import Client

def _generate_and_store_key(vault_client: Client, path: str) -> bytes:
    new_key = get_random_bytes(32)
    vault_client.secrets.kv.v2.create_or_update_secret(
        path=path,
        secret={'key': new_key.hex()},
    )
    return new_key

def get_or_generate_secret_key(vault_client: Client, path: str) -> bytes:
    '''
    Gets a secret key from Vault, or generates a new one if it doesn't exist.
    '''
    try:
        key = vault_client.secrets.kv.v2.read_secret_version(path=path)
        if key is None or 'data' not in key or 'data' not in key['data'] or 'key' not in key['data']['data']:
            raise Exception('No key found')
        return bytes.fromhex(key["data"]["data"]["key"])
    except Exception as e:
        print(e)
        return _generate_and_store_key(vault_client, path)


def generate_temp_ids(uuid: uuid.UUID, key: bytes) -> list[str]:
    '''
    Generates a list of temporary IDs for a given user ID.

    The temporary IDs are generated by encrypting the user ID with AES-256 in GCM mode.
    '''
    uuid_bytes = uuid.bytes
    temp_ids = []
    epoch_start = timezone.now() - timedelta(seconds=30)
    epoch_end = epoch_start + timedelta(minutes=15)

    for i in range(4 * 6):
        # temp id format:
        #
        # b64encode(
        #   Encrypt(
        #       uuid_bytes (16 bytes) || start_time (4 bytes) || end_time (4 bytes)
        #   ) (24 bytes) ||
        #   nonce (12 bytes) ||
        #   tag (16 bytes)
        # )

        # Encrypt with AES-GCM
        # https://pycryptodome.readthedocs.io/en/latest/src/cipher/modern.html#gcm-mode

        epoch_start_bytes = int(epoch_start.timestamp()).to_bytes(4, 'big')
        epoch_end_bytes = int(epoch_end.timestamp()).to_bytes(4, 'big')
        # print(int(epoch_start.timestamp()), epoch_start_bytes.hex().upper())
        # print(int(epoch_end.timestamp()), epoch_end_bytes.hex().upper())

        nonce = get_random_bytes(12)    # 96 bit / 12 byte IV

        plaintext = uuid_bytes + epoch_start_bytes + epoch_end_bytes    # 24 bytes
        # print(len(plaintext), plaintext)

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(plaintext)
        # print(len(ciphertext), ciphertext.hex().upper())
        # print(len(tag), tag.hex().upper())

        # Combine ciphertext, nonce, and tag
        temp_id_bytes = ciphertext + nonce + tag    # 52 bytes
        temp_id = b64encode(temp_id_bytes)          # 72 bytes
        # print(len(temp_id_bytes), temp_id_bytes)
        # print(len(temp_id), temp_id)

        temp_ids.append({
            'temp_id': temp_id.decode('utf-8'),
            'start': int(epoch_start.timestamp()),
            'end': int(epoch_end.timestamp())
        })

        # Increment epoch_start and epoch_end by 15 minutes
        epoch_start = epoch_end
        epoch_end += timedelta(minutes=15)

    return temp_ids, int(epoch_start.timestamp())

def decrypt_temp_id(temp_id: dict, key: bytes, user_id: uuid.UUID, user_recent_infection) -> bool:
    if 'temp_id' not in temp_id or 'contact_timestamp' not in temp_id or 'rssi' not in temp_id:
        return False
    if not isinstance(temp_id['contact_timestamp'], int) or not isinstance(temp_id['rssi'], int):
        return False
    try:
        temp_id_bytes = b64decode(temp_id['temp_id'])
        ciphertext = temp_id_bytes[:24]
        nonce = temp_id_bytes[24:36]
        tag = temp_id_bytes[36:]

        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        uuid_bytes = plaintext[:16]
        epoch_start_bytes = plaintext[16:20]
        epoch_end_bytes = plaintext[20:]

        contact_uuid = uuid.UUID(bytes=uuid_bytes)
        epoch_start = int.from_bytes(epoch_start_bytes, 'big')
        epoch_end = int.from_bytes(epoch_end_bytes, 'big')
        if not (epoch_start <= temp_id['contact_timestamp'] <= epoch_end):
            return False
        
        # Do not save records that are on themselves.
        if user_id == contact_uuid:
            return False
        
        temp_id['contact_timestamp'] = datetime.fromtimestamp(temp_id['contact_timestamp'])
        temp_id['infected_user'] = user_id
        temp_id['contacted_user'] = contact_uuid
        temp_id['infectionhistory'] = user_recent_infection
    except:
        return False

    return True

