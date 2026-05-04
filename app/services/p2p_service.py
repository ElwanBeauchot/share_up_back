import asyncio
import json
from typing import Dict, AsyncIterator
from app.schemas import OfferMessage, AnswerMessage, IceMessage, ControlMessage
from app.logging_config import logger

# Ancien stockage utilisé pour le polling (remplacé par SSE)
# _p2p_messages: Dict[str, List[Dict[str, Any]]] = {}

# Une queue par UUID destinataire connecté en SSE
_subscribers: Dict[str, asyncio.Queue] = {}


def _send(to_uuid: str, msg: dict) -> None:
    queue = _subscribers.get(to_uuid)
    if queue is not None:
        queue.put_nowait(msg)


async def store_offer(message: OfferMessage):
    logger.info(f"Offer from {message.from_uuid} to {message.to_uuid}")
    _send(message.to_uuid, {"type": "offer", "from_uuid": message.from_uuid, "sdp": message.sdp})


async def store_answer(message: AnswerMessage):
    logger.info(f"Answer from {message.from_uuid} to {message.to_uuid}")
    _send(message.to_uuid, {"type": "answer", "from_uuid": message.from_uuid, "sdp": message.sdp})


async def store_ice(message: IceMessage):
    logger.info(f"ICE from {message.from_uuid} to {message.to_uuid}")
    _send(message.to_uuid, {
        "type": "ice",
        "from_uuid": message.from_uuid,
        "candidate": message.candidate,
        "sdpMid": message.sdpMid,
        "sdpMLineIndex": message.sdpMLineIndex,
    })


# Ancien endpoint de polling (remplacé par event_stream / SSE)
# async def get_messages(uuid: str) -> List[Dict[str, Any]]:
#     messages = _p2p_messages.pop(uuid, [])
#     logger.info(f"Retrieving {len(messages)} messages for UUID: {uuid}")
#     return messages


async def relay_signal(signal_type: str, message: ControlMessage):
    logger.info(f"{signal_type} from {message.from_uuid} to {message.to_uuid}")
    _send(message.to_uuid, {
        "type": signal_type,
        "from_uuid": message.from_uuid,
        "reason": message.reason,
    })


async def event_stream(uuid: str) -> AsyncIterator[str]:
    queue: asyncio.Queue = asyncio.Queue()
    _subscribers[uuid] = queue
    logger.info(f"SSE connected: {uuid}")
    try:
        while True:
            msg = await queue.get()
            yield f"data: {json.dumps(msg)}\n\n"
    finally:
        _subscribers.pop(uuid, None)
        logger.info(f"SSE disconnected: {uuid}")
