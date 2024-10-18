# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiosmtpd",
# ]
# ///

import asyncio

from aiosmtpd.controller import Controller


class CustomEmailHandler:
    async def handle_DATA(self, server, session, envelope):
        print("Message from:", envelope.mail_from)
        print("Message to:", envelope.rcpt_tos)
        print("Message content:", envelope.content.decode("utf-8"))
        return "250 Message accepted for delivery"


async def main():
    handler = CustomEmailHandler()
    controller = Controller(handler, hostname="localhost", port=1026)
    controller.start()
    try:
        print("SMTP  server is running on localhost:1026. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt:
        controller.stop()
        print("\nShutting down SMTP server...")


# Create and start the server
if __name__ == "__main__":
    asyncio.run(main())
