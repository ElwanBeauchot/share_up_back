from typing import List, Dict, Any
from app.schemas import OfferMessage, AnswerMessage, IceMessage
from app.logging_config import logger

# Stockage en mémoire simple : {uuid_destinataire: [messages]}
_p2p_messages: Dict[str, List[Dict[str, Any]]] = {}


def _store_message(to_uuid: str, msg: Dict[str, Any]):
    """Ajoute un message à la file d'attente du destinataire."""
    if to_uuid not in _p2p_messages:
        _p2p_messages[to_uuid] = []
    _p2p_messages[to_uuid].append(msg)


async def store_offer(message: OfferMessage):
    logger.info(f"Storing offer from {message.from_uuid} to {message.to_uuid}")
    _store_message(message.to_uuid, {
        "type": "offer",
        "from_uuid": message.from_uuid,
        "sdp": message.sdp
    })


async def store_answer(message: AnswerMessage):
    logger.info(f"Storing answer from {message.from_uuid} to {message.to_uuid}")
    _store_message(message.to_uuid, {
        "type": "answer",
        "from_uuid": message.from_uuid,
        "sdp": message.sdp
    })


async def store_ice(message: IceMessage):
    logger.info(f"Storing ICE candidate from {message.from_uuid} to {message.to_uuid}")
    _store_message(message.to_uuid, {
        "type": "ice",
        "from_uuid": message.from_uuid,
        "candidate": message.candidate,
        "sdpMid": message.sdpMid,
        "sdpMLineIndex": message.sdpMLineIndex
    })


async def get_messages(uuid: str) -> List[Dict[str, Any]]:
    messages = _p2p_messages.pop(uuid, [])
    logger.info(f"Retrieving {len(messages)} messages for UUID: {uuid}")
    return messages
