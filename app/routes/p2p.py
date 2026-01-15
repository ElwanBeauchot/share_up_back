from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List

router = APIRouter(prefix="/p2p", tags=["p2p"])

# Stockage en mémoire simple : {uuid_destinataire: [messages]}
_p2p_messages: Dict[str, List[Dict[str, Any]]] = {}


def _store_message(to_uuid: str, msg: Dict[str, Any]):
    """Ajoute un message à la file d'attente du destinataire."""
    if to_uuid not in _p2p_messages:
        _p2p_messages[to_uuid] = []
    _p2p_messages[to_uuid].append(msg)


@router.post("/offer")
async def receive_offer(message: Dict[str, Any]):
    from_uuid = message.get("from")
    to_uuid = message.get("to")
    sdp = message.get("sdp")
    
    if not from_uuid or not to_uuid or not sdp:
        raise HTTPException(status_code=400, detail="from, to et sdp requis")
    
    _store_message(to_uuid, {
        "type": "offer",
        "from": from_uuid,
        "sdp": sdp
    })
    return {"status": "offer stored"}


@router.post("/answer")
async def receive_answer(message: Dict[str, Any]):
    from_uuid = message.get("from")
    to_uuid = message.get("to")
    sdp = message.get("sdp")
    
    if not from_uuid or not to_uuid or not sdp:
        raise HTTPException(status_code=400, detail="from, to et sdp requis")
    
    _store_message(to_uuid, {
        "type": "answer",
        "from": from_uuid,
        "sdp": sdp
    })
    return {"status": "answer stored"}


@router.post("/ice")
async def receive_ice(message: Dict[str, Any]):
    from_uuid = message.get("from")
    to_uuid = message.get("to")
    candidate = message.get("candidate")
    
    if not from_uuid or not to_uuid or not candidate:
        raise HTTPException(status_code=400, detail="from, to et candidate requis")
    
    _store_message(to_uuid, {
        "type": "ice",
        "from": from_uuid,
        "candidate": candidate,
        "sdpMid": message.get("sdpMid"),
        "sdpMLineIndex": message.get("sdpMLineIndex")
    })
    return {"status": "ice candidate stored"}


@router.get("/messages/{uuid}")
async def get_messages(uuid: str):
    messages = _p2p_messages.pop(uuid, [])
    return {"messages": messages}
