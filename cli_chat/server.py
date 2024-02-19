import re
import secrets
from argparse import ArgumentParser
from collections import namedtuple
from typing import List, Tuple, Optional
from asyncio import sleep, start_server, StreamReader, StreamWriter

from . import consts
from .consts import signals, commands
from .helpers import (AESCipher, real_read, convert_str_to_address,
  					hash_sha512_md5, set_random_color)


secret_key: str
secret_key_hash: str
aes: AESCipher

parser = ArgumentParser()
parser.add_argument("address", type=convert_str_to_address)

User = namedtuple("User", ("reader", "writer", "username", "colored_username"))
users: List[User] = []


def verify_username(username: str, /) -> bool:
	for user in users:
		if user.username == username:
			return False

	return 0 < len(username) <= consts.USERNAME_MAX_LENGTH


async def enquire_and_verify_credentials(
	reader: StreamReader, writer: StreamWriter, /,
) -> Optional[Tuple[str, str]]:
	writer.write(signals['CREDENTIALS_ENQUIRE'])

	user_secret_key_hash = (await real_read(reader)).decode()
	username = (await real_read(reader)).decode()

	if user_secret_key_hash == secret_key_hash and verify_username(username):
		writer.write(signals['CREDENTIALS_ARE_VALID'])
		await writer.drain()

		return (secret_key_hash, username)

	writer.write(signals['CREDENTIALS_ARE_INVALID'])
	await writer.drain()

	return None


async def broadcast(
	message: str,
	/,
	*,
	prefix: str = consts.SERVER_MESSAGE_PREFIX,
	sender: Optional[User] = None,
) -> None:
	"""
	:param prefix: A prefix that comes before the main
		message. For example the username with a colon.
	:param sender: The sender of this message. Specified so as not
		to send him his own message. If the sender is a server - `None`.
	"""

	text = prefix + " " + message
	data = aes.encrypt(text.encode())

	for user in users:
		if user is not sender:
			try:
				user.writer.write(data)
				await user.writer.drain()
			except BrokenPipeError:
				# This happens when user closes the
				# connection without notifying the server
				await disconnect_user(user)


async def disconnect_user(user: User, /) -> None:
	users.remove(user)
	user.writer.close()
	await broadcast("%s disconnected." % user.colored_username)


async def handle_command(message: str) -> None:
	if message == commands['USERS_REQUEST']:
		await broadcast(", ".join(u.colored_username for u in users))
	elif message == commands['COMMANDS_REQUEST']:
		await broadcast(", ".join(c for c in commands.values()))


async def receive_messages(user: User) -> None:
	while True:
		raw_message = aes.decrypt(await real_read(user.reader)).decode()
		message = re.sub(r"(\s|\n|\t)+", r" ", raw_message)

		if message == commands['DISCONNECT']:
			await disconnect_user(user)
			break

		await broadcast(
			message,
			prefix=user.colored_username + ":",
			sender=user,
		)
		if message in commands.values():
			await handle_command(message)


async def handle_connection(
	reader: StreamReader,
	writer: StreamWriter,
	/,
) -> None:
	credentials = await enquire_and_verify_credentials(reader, writer)
	if credentials is None:
		writer.close()
		return

	_, username = credentials
	colored_username = set_random_color(username)

	user = User(reader, writer, username, colored_username)
	del reader, writer, username, colored_username
	users.append(user)

	await sleep(0.2)  # To seperate the sending of data
	await broadcast("%s connected." % user.colored_username)
	await receive_messages(user)


async def main() -> None:
	global secret_key, secret_key_hash, aes

	args = parser.parse_args()

	secret_key = secrets.token_hex(consts.SECRET_KEY_LENGTH // 2)
	print("Your secret key:", secret_key)
	secret_key_hash = hash_sha512_md5(secret_key)

	aes = AESCipher(secret_key.encode())

	async with await start_server(handle_connection, *args.address) as server:
		print("Listen on %s:%d..." % args.address)
		await server.serve_forever()
