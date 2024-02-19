from getpass import getpass
from datetime import datetime
from argparse import ArgumentParser
from asyncio import create_task, open_connection, sleep, StreamReader, \
	StreamWriter

from aioconsole import ainput

from . import consts
from .consts import signals, commands
from .helpers import AESCipher, real_read, hash_sha512_md5, \
	convert_str_to_address


parser = ArgumentParser()
parser.add_argument("server_address", type=convert_str_to_address)


async def send_credentials_for_verification(
	reader: StreamReader, writer: StreamWriter, /,
	secret_key_hash: str, username: str,
) -> bool:
	enquire_signal = signals['CREDENTIALS_ENQUIRE']
	are_valid_signal = signals['CREDENTIALS_ARE_VALID']
	are_invalid_signal = signals['CREDENTIALS_ARE_INVALID']

	start_signal = await real_read(reader)
	if start_signal != enquire_signal:
		raise RuntimeError("A %r signal was expected, but got %r." % (
			enquire_signal, start_signal,
		))

	writer.write(secret_key_hash.encode())
	await sleep(0.2)  # To seperate the sending of data
	writer.write(username.encode())
	await writer.drain()

	response_signal = await real_read(reader)

	if response_signal == are_valid_signal:
		return True
	elif response_signal == are_invalid_signal:
		return False

	raise RuntimeError("%r or %r signals were expected, but got %r." % (
		are_valid_signal, are_invalid_signal, response_signal,
	))


async def receive_messages(reader: StreamReader, /, aes: AESCipher) -> None:
	while True:
		# We explicitly specify utf8, because without it
		# an error will pop up when decoding colored text
		message = aes.decrypt(await real_read(reader)).decode("utf8")
		now = datetime.now().strftime(consts.DATETIME_FORMAT)
		print("(%s)" % now, message)


async def write_messages(writer: StreamWriter, /, aes: AESCipher) -> None:
	while True:
		while True:
			message = await ainput()
			if message:
				break

		writer.write(aes.encrypt(message.encode()))
		await writer.drain()

		if message == commands['DISCONNECT']:
			writer.close()
			break


async def main() -> None:
	args = parser.parse_args()

	secret_key = getpass("Enter secret key: ")
	secret_key_hash = hash_sha512_md5(secret_key)
	username = input("Enter your username: ")

	reader, writer = await open_connection(*args.server_address)

	if not await send_credentials_for_verification(
		reader, writer, secret_key_hash, username,
	):
		writer.close()
		print("Invalid secret key or unsuitable username.")
		return

	aes = AESCipher(secret_key.encode())

	t1 = create_task(receive_messages(reader, aes))
	await write_messages(writer, aes)
	t1.cancel()
