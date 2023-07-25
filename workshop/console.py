import logging
import asyncio
from termcolor import colored

from langchain.chat_models import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langwave.memory.volatile import VolatileMemory

log = logging.getLogger(__name__)


async def streaming_console(args):
    chat = ChatOpenAI(
        streaming=True,
        callbacks=[StreamingStdOutCallbackHandler()],
        temperature=0,
        verbose=args.debug,
    )
    history = VolatileMemory()
    user_input = args.initial

    while True:
        if user_input:
            history.add_user_message(user_input)
            resp = await chat.apredict_messages(history.messages)
            print("\n")
            # log.info(f"AI: {resp} and type is {type(resp)}")
            history.add_message(resp)

        user_input = input(colored(">>>: ", "green"))
        if user_input == "exit":
            break


async def main(args):
    log.info("Hello there!")
    # test_memory()
    await streaming_console(args)


import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", "-d", action="store_true", help="Enable debug logging"
    )
    parser.add_argument(
        "--initial",
        "-i",
        type=str,
        default="",
        help="Initial message to send to the chatbot",
    )
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(main(parse_args()))
