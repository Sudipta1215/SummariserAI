from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import Workspace, WorkspaceAccess, User
from pydantic import BaseModel
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(tags=["Workspaces"])

# --- PYDANTIC MODELS ---
class WorkspaceCreate(BaseModel):
    user_id: int
    title: str

class WorkspaceUpdate(BaseModel):
    user_id: int
    content: str

class AddCollaborator(BaseModel):
    owner_id: int
    target_email: str
    permission: str = "view"

# --- EMAIL HELPER ---
def send_invitation_email(to_email: str, workspace_title: str, inviter_name: str, permission: str):
    # Mock email for testing if no SMTP server is configured
    print(f"📧 [Mock Email] Invite sent to {to_email} for '{workspace_title}' by {inviter_name}")
    return True

# --- API ROUTES ---

@router.post("/")
def create_workspace(data: WorkspaceCreate, db: Session = Depends(get_db)):
    ws = Workspace(owner_id=data.user_id, title=data.title)
    db.add(ws)
    db.commit()
    db.refresh(ws)
    return ws

@router.get("/user/{user_id}")
def get_user_workspaces(user_id: int, db: Session = Depends(get_db)):
    owned = db.query(Workspace).filter(Workspace.owner_id == user_id).all()
    shared_access = db.query(WorkspaceAccess).filter(WorkspaceAccess.user_id == user_id).all()
    shared = [access.workspace for access in shared_access]
    return {"owned": owned, "shared": shared}

@router.get("/{workspace_id}")
def get_workspace(workspace_id: int, user_id: int, db: Session = Depends(get_db)):
    ws = db.query(Workspace).filter(Workspace.workspace_id == workspace_id).first()
    if not ws: raise HTTPException(404, "Not found")
    
    if ws.owner_id == user_id:
        permission = "owner"
    else:
        access = db.query(WorkspaceAccess).filter(
            WorkspaceAccess.workspace_id == workspace_id,
            WorkspaceAccess.user_id == user_id
        ).first()
        if not access: raise HTTPException(403, "Access denied")
        permission = access.permission_level

    return {
        "workspace_id": ws.workspace_id,
        "title": ws.title,
        "content": ws.content,
        "permission": permission
    }

@router.put("/{workspace_id}")
def update_workspace(workspace_id: int, data: WorkspaceUpdate, db: Session = Depends(get_db)):
    ws = db.query(Workspace).filter(Workspace.workspace_id == workspace_id).first()
    if not ws: raise HTTPException(404, "Not found")

    allowed = False
    if ws.owner_id == data.user_id:
        allowed = True
    else:
        access = db.query(WorkspaceAccess).filter(
            WorkspaceAccess.workspace_id == workspace_id,
            WorkspaceAccess.user_id == data.user_id
        ).first()
        if access and access.permission_level == "edit":
            allowed = True
    
    if not allowed: raise HTTPException(403, "Permission denied")
    
    ws.content = data.content
    db.commit()
    return {"status": "saved"}

@router.post("/{workspace_id}/invite")
def invite_collaborator(workspace_id: int, data: AddCollaborator, db: Session = Depends(get_db)):
    ws = db.query(Workspace).filter(Workspace.workspace_id == workspace_id).first()
    if not ws or ws.owner_id != data.owner_id:
        raise HTTPException(403, "Only owner can invite")
    
    friend = db.query(User).filter(User.email == data.target_email).first()
    if not friend: raise HTTPException(404, "User not found")
        
    exists = db.query(WorkspaceAccess).filter(
        WorkspaceAccess.workspace_id == workspace_id,
        WorkspaceAccess.user_id == friend.user_id
    ).first()
    
    if exists:
        exists.permission_level = data.permission
    else:
        access = WorkspaceAccess(
            workspace_id=workspace_id, 
            user_id=friend.user_id,
            permission_level=data.permission
        )
        db.add(access)
    
    db.commit()
    
    inviter = db.query(User).filter(User.user_id == data.owner_id).first()
    send_invitation_email(friend.email, ws.title, inviter.name, data.permission)
    
    return {"message": "Invitation sent"}