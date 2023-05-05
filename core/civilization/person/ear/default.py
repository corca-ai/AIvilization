from .base import (
    BaseEar,
    MessageType,
)
from socket import socket, AF_INET, SOCK_STREAM, error as socket_error
from core.config import settings
from struct import unpack
from core.civilization.person.base import (
    BasePerson,
    INSTRUCTION_LENGTH_BYTES,
    EXTRA_LENGTH_BYTES,
    MESSAGE_TYPE_BYTES,
    MESSAGE_SENTER_BYTES,
    INVALID_MESSAGE_SENDER_ERROR_MESSAGE,
    INVALID_MESSAGE_TYPE_ERROR_MESSAGE,
    TalkParams,
)
from typing import Tuple
from asyncio import run


class Ear(BaseEar):
    listener_socket: socket
    person: BasePerson
    port: int

    def __init__(self, person: BasePerson):
        super().__init__()
        self.person = person
        self.listener_socket = socket(AF_INET, SOCK_STREAM)
        if self.bind_port() == False:
            raise Exception("No Avaialable Ports For Person's Ear")
        if self.person.name == "David":
            run(self.listen())

    def bind_port(self):
        port_start = settings["PORT_START"]
        port_range = settings["PORT_RANGE"]
        host = settings["HOST"]
        for port in range(port_start, port_start + port_range):
            try:
                self.listener_socket.bind((host, port))
                self.port = port
                return True
            except socket_error:
                pass
        return False

    def get_instruction_length(self, conn: socket) -> int:
        instruction_length_data = conn.recv(INSTRUCTION_LENGTH_BYTES)
        return unpack(">Q", instruction_length_data)[0]

    def get_extra_length(self, conn: socket) -> int:
        extra_length_data = conn.recv(EXTRA_LENGTH_BYTES)
        return unpack(">Q", extra_length_data)[0]

    def get_sender(self, conn: socket) -> BasePerson:
        message_sender_data = conn.recv(MESSAGE_SENTER_BYTES)
        message_sender = message_sender_data.decode()
        if message_sender not in self.person.friends:
            raise Exception(INVALID_MESSAGE_SENDER_ERROR_MESSAGE)
        return self.person.friends[message_sender]

    def get_message_type(self, conn: socket) -> MessageType:
        message_type_data = conn.recv(MESSAGE_TYPE_BYTES)
        message_type = (unpack(">I", message_type_data))[0]
        if message_type not in MessageType.__members__.values():
            raise Exception(INVALID_MESSAGE_TYPE_ERROR_MESSAGE)
        return MessageType((unpack(">I", message_type_data))[0])

    def get_message(self, conn: socket, message_length: int) -> str:
        message_body_data = conn.recv(message_length)
        return message_body_data.decode()

    def parse_data(self, conn: socket) -> Tuple[BasePerson, MessageType, str, str]:
        instruction_length = self.get_instruction_length(conn)
        extra_length = self.get_extra_length(conn)
        sender = self.get_sender(conn)
        message_type = self.get_message_type(conn)
        instruction = self.get_message(conn, instruction_length)
        extra = self.get_message(conn, extra_length)
        return (sender, message_type, instruction, extra)

    async def listen(self):
        while True:
            conn, addr = self.listener_socket.accept()
            if addr[0] != "127.0.0.1":
                print("Unknown Message")
                continue
            try:
                message_sender, _, instruction, extra = self.parse_data(conn)
            except Exception as e:
                print(f"Something's Wrong : {e}")
                continue

            self.person.respond(message_sender, instruction, TalkParams.from_str(extra))

    def wait(self):
        _conn, _addr = self.listener_socket.accept()
        # if addr[0] != "127.0.0.1":
        #     raise Exception("Unknown Message")
        # try:
        #     message_sender, _, instruction, extra = self.parse_data(conn)
        # except Exception as e:
        #     raise Exception(f"Something's Wrong : {e}")
        # self.person.respond(message_sender, instruction, TalkParams.from_str(extra))
