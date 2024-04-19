from re import sub
from socket import AF_INET, SOCK_STREAM
from socket import error as socket_error
from socket import socket
from struct import unpack
from threading import Thread
from typing import Tuple

from core.civilization.god.system import System
from core.civilization.person.base import (
    EXTRA_LENGTH_BYTES,
    INSTRUCTION_LENGTH_BYTES,
    INVALID_MESSAGE_SENDER_ERROR_MESSAGE,
    INVALID_MESSAGE_TYPE_ERROR_MESSAGE,
    MESSAGE_SENDER_BYTES,
    MESSAGE_TYPE_BYTES,
    BasePerson,
    TalkParams,
)
from core.config import settings

from .base import BaseEar, MessageType


class Ear(BaseEar):
    listener_socket: socket
    person: BasePerson
    port: int

    def __init__(self, person: BasePerson):
        super().__init__()
        self.person = person
        self.listener_socket = socket(AF_INET, SOCK_STREAM)
        if self.bind_port() == False:
            # TODO what if there's no available port? We need to let llm knows about resource limitations
            raise Exception(
                System.error(f"No Avaialable Ports For {self.person.name}'s Ear")
            )
        if self.person.name != "David":
            t = Thread(target=self.listen)
            t.start()

    def bind_port(self):
        port_start = settings.PORT_START
        port_range = settings.PORT_RANGE
        host = settings.HOST
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
        return unpack(">I", instruction_length_data)[0]

    def get_extra_length(self, conn: socket) -> int:
        extra_length_data = conn.recv(EXTRA_LENGTH_BYTES)
        return unpack(">I", extra_length_data)[0]

    def get_sender(self, conn: socket) -> BasePerson:
        message_sender_data = conn.recv(MESSAGE_SENDER_BYTES)
        message_sender = sub("[\0]", "", message_sender_data.decode())
        if message_sender not in self.person.experts:
            raise Exception(INVALID_MESSAGE_SENDER_ERROR_MESSAGE)
        return self.person.experts[message_sender]

    def get_message_type(self, conn: socket) -> MessageType:
        message_type_data = conn.recv(MESSAGE_TYPE_BYTES)
        message_type = (unpack(">I", message_type_data))[0]
        if message_type not in [e.value for e in MessageType]:
            raise Exception(INVALID_MESSAGE_TYPE_ERROR_MESSAGE)
        return MessageType(message_type)

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

    def listen(self):
        self.listener_socket.listen()
        print(f"[{self.person.name}-Ear] : Listening On {self.port}")
        while True:
            conn, addr = self.listener_socket.accept()
            if addr[0] != settings.HOST:
                print(
                    System.announcement(f"[{self.person.name}-Ear] : Unknown Message")
                )
                continue
            try:
                message_sender, _, instruction, extra = self.parse_data(conn)
            except Exception as e:
                print(
                    System.announcement(
                        f"[{self.person.name}-Ear] : Parsing Message Failed\n{e}"
                    )
                )
                continue
            self.person.respond(
                message_sender,
                message_sender.to_format(instruction),
                TalkParams.from_str(extra),
            )

    def wait(self):
        self.listener_socket.listen()
        print(
            System.announcement(
                f"[{self.person.name}-Ear] : Waiting For Response On {self.port}"
            )
        )
        _conn, _addr = self.listener_socket.accept()
        print(System.announcement(f"[{self.person.name}-Ear] : Response Received"))
