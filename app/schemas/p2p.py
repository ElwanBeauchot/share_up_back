from pydantic import BaseModel
from typing import Optional


class P2PMessageBase(BaseModel):
    from_uuid: str
    to_uuid: str


class OfferMessage(P2PMessageBase):
    sdp: str


class AnswerMessage(P2PMessageBase):
    sdp: str


class IceMessage(P2PMessageBase):
    candidate: str
    sdpMid: Optional[str] = None
    sdpMLineIndex: Optional[int] = None


class ControlMessage(P2PMessageBase):
    reason: Optional[str] = None


class P2PMessageResponse(BaseModel):
    type: str
    from_uuid: str
    sdp: Optional[str] = None
    candidate: Optional[str] = None
    sdpMid: Optional[str] = None
    sdpMLineIndex: Optional[int] = None
