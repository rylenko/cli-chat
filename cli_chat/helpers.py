import random
from typing import Tuple
from hashlib import md5, sha512
from asyncio import StreamReader

from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from . import consts
from .consts import colors


AddressType = Tuple[str, int]


def convert_str_to_address(s: str, /) -> AddressType:
	try:
		host, port_str = s.split(":")
		return (host, int(port_str))
	except ValueError as exc:
		raise ValueError("Invalid address.") from exc


def hash_sha512_md5(value: str, /) -> str:
	sha512_hex = sha512(value.encode()).hexdigest()
	return md5(sha512_hex.encode()).hexdigest()


async def real_read(reader: StreamReader, /) -> bytes:
	"""General function for receiving `reader` data.
	The main purpose is to ignore empty data."""

	while True:
		rv = await reader.read(consts.READ_BUFSIZE)
		if rv:
			return rv


def set_random_color(value: str, /) -> str:
	color = random.choice(tuple(colors.values()))
	return color + value + consts.COLOR_END


class AESCipher:
	__slots__ = ("secret_key",)

	def __init__(self, secret_key: bytes, /) -> None:
		self.secret_key = secret_key

	def encrypt(self, value: bytes, /) -> bytes:
		padded_value = pad(value, AES.block_size)
		iv = Random.new().read(AES.block_size)
		cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
		return iv + cipher.encrypt(padded_value)

	def decrypt(self, value: bytes, /) -> bytes:
		iv = value[:AES.block_size]
		cipher = AES.new(self.secret_key, AES.MODE_CBC, iv)
		padded_value = cipher.decrypt(value[AES.block_size:])
		return unpad(padded_value, AES.block_size)
