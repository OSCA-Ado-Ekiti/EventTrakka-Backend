from fastapi import APIRouter

from app.api.routes import attendees, auth, events, organizations, users

api_router = APIRouter()
api_router.include_router(attendees.router, tags=["attendees"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(events.router, tags=["events"])
api_router.include_router(organizations.router, tags=["organizations"])
api_router.include_router(users.router, tags=["users"])
