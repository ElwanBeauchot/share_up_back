from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse

from app.core.security import verify_api_key
from app.schemas import OfferMessage, AnswerMessage, IceMessage, ControlMessage, P2PMessageResponse
from app.services.p2p_service import store_offer, store_answer, store_ice, relay_signal, event_stream
import logging
router = APIRouter(prefix="/p2p", tags=["p2p"])
logger = logging.getLogger('share_up_app')


@router.post("/offer")
async def receive_offer(message: OfferMessage, dep=Depends(verify_api_key)):
    if not message.from_uuid or not message.to_uuid or not message.sdp:
        raise HTTPException(status_code=400, detail="from, to et sdp requis")
    
    await store_offer(message)
    return {"status": "offer stored"}


@router.post("/answer")
async def receive_answer(message: AnswerMessage, dep=Depends(verify_api_key)):
    if not message.from_uuid or not message.to_uuid or not message.sdp:
        raise HTTPException(status_code=400, detail="from, to et sdp requis")
    
    await store_answer(message)
    return {"status": "answer stored"}


@router.post("/ice")
async def receive_ice(message: IceMessage, dep=Depends(verify_api_key)):
    if not message.from_uuid or not message.to_uuid or not message.candidate:
        raise HTTPException(status_code=400, detail="from, to et candidate requis")
    
    await store_ice(message)
    return {"status": "ice candidate stored"}

    
@router.post("/reject")
async def p2p_reject(message: ControlMessage, dep=Depends(verify_api_key)):
    if not message.from_uuid or not message.to_uuid:
        raise HTTPException(status_code=400, detail="from et to requis")
    await relay_signal("reject", message)
    return {"status": "reject relayed"}


@router.post("/cancel")
async def p2p_cancel(message: ControlMessage, dep=Depends(verify_api_key)):
    if not message.from_uuid or not message.to_uuid:
        raise HTTPException(status_code=400, detail="from et to requis")
    await relay_signal("cancel", message)
    return {"status": "cancel relayed"}


# Ancien endpoint de polling (remplacé par GET /p2p/events/{uuid})
# @router.get("/messages/{uuid}")
# async def get_messages_endpoint(uuid: str):
#     messages = await get_messages(uuid)
#     return {"messages": messages}


@router.get("/events/{uuid}")
async def p2p_events(uuid: str):
    return StreamingResponse(event_stream(uuid), media_type="text/event-stream")
