USERNAME_MAX_LENGTH = 20
SECRET_KEY_LENGTH = 16  # Must be even

READ_BUFSIZE = 1024
DATETIME_FORMAT = "%H:%M:%S"

commands = {
	'DISCONNECT': "/disconnect",
	'USERS_REQUEST': "/users",
	'COMMANDS_REQUEST': "/commands",
}

signals = {
	'CREDENTIALS_ENQUIRE': b"!credentials-enquire",
	'CREDENTIALS_ARE_VALID': b"!credentials-are-valid",
	'CREDENTIALS_ARE_INVALID': b"!credentials-are-invalid",
}

colors = {
	'RED': "\033[91m",
	'GREEN': "\033[92m",
	'YELLOW': "\033[93m",
	'BLUE': "\033[94m",
	'PURPLE': "\033[95m",
}
COLOR_BOLD = "\033[1m"
COLOR_END = "\033[0m"

SERVER_MESSAGE_PREFIX = COLOR_BOLD + colors['RED'] + "*" + COLOR_END
