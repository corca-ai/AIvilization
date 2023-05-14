from socket import AF_INET, SOCK_STREAM, socket
from struct import pack

from core.civilization.person.base import MESSAGE_SENDER_BYTES, BasePerson, MessageType
from core.civilization.person.ear import BaseEar
from core.config import settings

from .base import BaseMouth


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
        sender_data = self.person.name.rjust(MESSAGE_SENDER_BYTES, "\0").encode()
        message_type_data = pack(">I", message_type.value)
        instruction_data = message_instruction.encode()
        instruction_length_data = pack(">I", len(instruction_data))
        extra_data = extra.encode()
        extra_length_data = pack(">I", len(extra_data))
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
        to: BaseEar,
        instruction: str,
        extra: str,
    ):
        data = self.construct_data(instruction, extra)
        client = socket(AF_INET, SOCK_STREAM)
        client.connect((settings.HOST, to.port))
        client.send(data)
        client.close()
