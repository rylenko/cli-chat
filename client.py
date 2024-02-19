from asyncio import get_event_loop

from cli_chat.client import main

if __name__ == "__main__":
	get_event_loop().run_until_complete(main())
