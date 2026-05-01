from fastapi import APIRouter
from app.schemas.channel_schema import (
    ChannelCreateRequest, ChannelUpdateRequest, ChannelDeleteRequest, ChannelListRequest,
)
from app.schemas.common_schema import BaseResponse, PageData
from app.services.channel_service import ChannelService
from app.core.context import get_db

router = APIRouter(prefix="/api/channel", tags=["频道"])


@router.post("/create")
async def create_channel(req: ChannelCreateRequest):
    db = get_db()
    channel = await ChannelService.create(db, req.name, req.description, req.sort_order)
    return BaseResponse(data={"id": channel.id, "name": channel.name})


@router.post("/update")
async def update_channel(req: ChannelUpdateRequest):
    db = get_db()
    channel = await ChannelService.update(db, req.channel_id, req.name, req.description, req.sort_order, req.status)
    return BaseResponse(data={"id": channel.id, "name": channel.name, "status": channel.status})


@router.post("/delete")
async def delete_channel(req: ChannelDeleteRequest):
    db = get_db()
    await ChannelService.delete(db, req.channel_id)
    return BaseResponse(message="删除成功")


@router.post("/list")
async def list_channels(req: ChannelListRequest):
    db = get_db()
    channels, total = await ChannelService.get_list(db, req.page, req.page_size)
    total_pages = (total + req.page_size - 1) // req.page_size
    items = [
        {"id": c.id, "name": c.name, "description": c.description,
         "sort_order": c.sort_order, "status": c.status}
        for c in channels
    ]
    return BaseResponse(data=PageData(
        items=items, total=total, page=req.page, page_size=req.page_size, total_pages=total_pages
    ).model_dump())


@router.post("/public_list")
async def public_list_channels():
    db = get_db()
    channels = await ChannelService.get_public_list(db)
    return BaseResponse(data=[
        {"id": c.id, "name": c.name, "sort_order": c.sort_order}
        for c in channels
    ])
