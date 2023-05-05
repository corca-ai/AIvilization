from .base import BaseMouth
from socket import socket, AF_INET, SOCK_STREAM
from core.config import settings
from struct import pack
from core.civilization.person.base import BasePerson, MessageType


class Mouth(BaseMouth):
    person: BasePerson

    def __init__(self, person: BasePerson):
        super().__init__()
        self.person = person

    def construct_data(
        self,
        message_instruction: str,
        extra: str,
        message_type: MessageType = MessageType.Default,
    ) -> bytes:
        sender_data = self.person.name.encode()
        message_type_data = pack(">I", message_type.value)
        instruction_data = message_instruction.encode()
        instruction_length_data = pack(">Q", len(instruction_data))
        extra_data = extra.encode()
        extra_length_data = pack(">Q", len(extra_data))

        return (
            instruction_length_data
            + extra_length_data
            + sender_data
            + message_type_data
            + instruction_data
            + extra_data
        )

    def talk(
        self,
        listener: BasePerson,
        instruction: str,
        extra: str,
        message_type: MessageType = MessageType.Default,
    ):
        data = self.construct_data(instruction, extra, message_type)
        client = socket(AF_INET, SOCK_STREAM)
        client.connect((settings["HOST"], listener.ear.port))
        client.send(data)
        client.close()
