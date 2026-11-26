import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from agno.media import File as AgnoFile, Image as AgnoImage
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.agents.factory import build_agent
from app.core.config import ALLOWED_IMAGE_TYPES
from app.db.database import SessionLocal
from app.models.agent_task import AgentTask, TaskStatus
from app.models.conversation import Conversation, ConversationVisibility
from app.models.conversation_member import ConversationMember, MemberType
from app.models.file import File
from app.models.message import Message, MessageRole
from app.models.user import User
from app.services import agent_service, message_service

log = logging.getLogger("broker")

MAX_DEPTH = 5
MAX_ACTIVE = 10

_ACTIVE_STATES = [TaskStatus.queued, TaskStatus.running]
_executor = ThreadPoolExecutor(max_workers=8)
_lock = threading.Lock()
_active: set[UUID] = set()

def _now():
    return datetime.now(timezone.utc)


def _system(db: Session, cid: UUID, text: str):
    message_service.create_message(db, cid, text, MessageRole.system)


# ---------------------------------------------------------------- routing

def _agent_is_member(db: Session, cid: UUID, agent_id: UUID) -> bool:
    return db.query(ConversationMember.id).filter(
        ConversationMember.conversation_id == cid,
        ConversationMember.agent_mate_id == agent_id,
    ).first() is not None


def _pick_targets(db: Session, conversation: Conversation, message: Message) -> list[UUID]:
    ids: list[UUID] = []
    for m in message.mentions or []:
        if m.get("type") != "agent":
            continue
        aid = UUID(m["agent_mate_id"])
        if aid != message.sender_agent_mate_id and aid not in ids:  # no self-mention, no duplicates
            ids.append(aid)
    if ids:
        return ids

    # no @tag: only a human message can fall back to the default agent
    default = conversation.default_agent_id
    if message.role == MessageRole.user and default:
        private = conversation.visibility == ConversationVisibility.private
        if (private or message.file_id) and _agent_is_member(db, conversation.session_id, default):
            return [default]
    return []


def _report_unknown_tags(db: Session, cid: UUID, message: Message):
    found = {h.lower() for h in message_service.MENTION_RE.findall(message.content or "")}
    known = {m["handle"] for m in (message.mentions or [])}
    unknown = sorted(found - known)
    if unknown:
        tags = ", ".join("@" + u for u in unknown)
        _system(db, cid, f"No member in this conversation matches {tags}.")


def handle(db: Session, conversation: Conversation, message: Message, acting_user_id: UUID,
           depth: int = 0, parent_task_id: UUID | None = None) -> list[AgentTask]:
    """Every saved message goes through here. Creates tasks, never runs them."""
    if message.role == MessageRole.system:
        return []
    cid = conversation.session_id

    if message.role == MessageRole.user:
        _report_unknown_tags(db, cid, message)

    targets = _pick_targets(db, conversation, message)
    if not targets:
        return []

    if depth > MAX_DEPTH:
        _system(db, cid, "Stopped: agents asked each other too many times in a row.")
        return []
    active = db.query(func.count(AgentTask.id)).filter(
        AgentTask.conversation_id == cid, AgentTask.status.in_(_ACTIVE_STATES)).scalar()
    if active + len(targets) > MAX_ACTIVE:
        _system(db, cid, "Too many tasks are running. Wait for them to finish or press stop.")
        return []

    sender = message.sender_name or "Someone"
    kind = "agent" if message.role == MessageRole.agent else "user"
    instruction = f'{sender} ({kind}) wrote: "{message.content}"'

    tasks = [
        AgentTask(
            conversation_id=cid, agent_mate_id=aid, trigger_message_id=message.id,
            acting_user_id=acting_user_id, requested_by_agent_id=message.sender_agent_mate_id,
            parent_task_id=parent_task_id, depth=depth, instruction=instruction,
            file_id=message.file_id,
        )
        for aid in targets
    ]
    db.add_all(tasks)
    db.commit()
    _kick(cid)
    return tasks


# ---------------------------------------------------------------- worker

def _kick(cid: UUID):
    """Start a worker loop for this conversation unless one is already running."""
    with _lock:
        if cid in _active:
            return
        _active.add(cid)
    _executor.submit(_run_loop, cid)


def _run_loop(cid: UUID):
    """One task at a time per conversation, oldest first."""
    while True:
        # the 'is there more work' check and the exit share one lock with _kick,
        # so a task queued at the last moment is never lost
        with _lock:
            with SessionLocal() as db:
                row = (db.query(AgentTask.id)
                       .filter(AgentTask.conversation_id == cid, AgentTask.status == TaskStatus.queued)
                       .order_by(AgentTask.created_at.asc()).first())
            if row is None:
                _active.discard(cid)
                return
        task_id = row[0]
        try:
            with SessionLocal() as db:
                _execute(db, task_id)
        except Exception:
            log.exception("task %s crashed outside its handler", task_id)
            with SessionLocal() as db:   # never leave a task queued forever
                db.query(AgentTask).filter(
                    AgentTask.id == task_id, AgentTask.status.in_(_ACTIVE_STATES)
                ).update({"status": TaskStatus.failed, "error": "Internal error",
                          "finished_at": _now()}, synchronize_session=False)
                db.commit()


def _roster(db: Session, cid: UUID) -> str:
    members = (db.query(ConversationMember)
               .options(joinedload(ConversationMember.user), joinedload(ConversationMember.agent))
               .filter(ConversationMember.conversation_id == cid).all())
    lines = []
    for m in members:
        if m.member_type == MemberType.user and m.user:
            lines.append(f"- @{m.user.username} (human)")
        elif m.agent:
            lines.append(f"- @{m.agent.agent_id} (agent {m.agent.agent_name}): "
                         f"{m.agent.desc or ''} {m.agent.role or ''}".strip())
    return "\n".join(lines)


def _recent(db: Session, cid: UUID, limit: int = 15) -> str:
    rows = (db.query(Message)
            .options(joinedload(Message.sender_user), joinedload(Message.sender_agent))
            .filter(Message.conversation_id == cid, Message.deleted_at.is_(None),
                    Message.role != MessageRole.system)
            .order_by(Message.created_at.desc(), Message.id.desc()).limit(limit).all())
    lines = []
    for m in reversed(rows):
        kind = "agent" if m.role == MessageRole.agent else "human"
        lines.append(f"[{m.sender_name or 'unknown'} ({kind})] {(m.content or '')[:1500]}")
    return "\n".join(lines)


def _is_cancelled(db: Session, task: AgentTask) -> bool:
    db.commit()           # end any open transaction so we read fresh data
    db.refresh(task)
    return task.status == TaskStatus.cancelled


def _execute(db: Session, task_id: UUID):
    # atomic claim: loses against a concurrent stop(), which is what we want
    claimed = (db.query(AgentTask)
               .filter(AgentTask.id == task_id, AgentTask.status == TaskStatus.queued)
               .update({"status": TaskStatus.running, "started_at": _now()},
                       synchronize_session=False))
    db.commit()
    if not claimed:
        return
    task = db.get(AgentTask, task_id)
    cid = task.conversation_id

    try:
        conversation = db.get(Conversation, cid)
        mate = agent_service.get_agent_by_id(db, task.agent_mate_id)
        if not mate or not conversation or conversation.deleted_at:
            raise RuntimeError("Agent or conversation is no longer available.")
        acting = db.get(User, task.acting_user_id)

        agent = build_agent(db, mate, conversation, task.acting_user_id,
                            acting.username if acting else "user", _roster(db, cid))

        prompt = (f"Group chat so far (oldest first):\n{_recent(db, cid)}\n\n"
                  f"--- YOUR TASK ---\n{task.instruction}\n")
        kwargs = {}
        if task.file_id:
            file = db.get(File, task.file_id)
            if file:
                path = Path(file.file_path)
                prompt += (f"\nA file is attached: name={file.file_name}, file_id={file.id}. "
                           "Use this exact file_id with your tools.\n")
                if path.suffix.lower() == ".pdf":
                    kwargs["files"] = [AgnoFile(filepath=str(path))]
                elif path.suffix.lower() in ALLOWED_IMAGE_TYPES.values():
                    kwargs["images"] = [AgnoImage(filepath=str(path))]

        response = agent.run(prompt, **kwargs)
        text = str(response.content or "").strip() or "(no reply)"

        if _is_cancelled(db, task):      # stopped meanwhile: discard the output
            return

        mentions = message_service.parse_mentions(db, cid, text)
        reply = message_service.create_message(
            db, cid, text, MessageRole.agent,
            sender_agent_mate_id=mate.id, mentions=mentions)
        task.status = TaskStatus.done
        task.result = {"message_id": str(reply.id)}
        task.finished_at = _now()
        db.commit()

        # the reply may @mention other agents: this is how they talk to each other
        handle(db, conversation, reply, task.acting_user_id,
               depth=task.depth + 1, parent_task_id=task.id)

    except Exception as e:
        log.exception("task %s failed", task_id)
        db.rollback()
        task = db.get(AgentTask, task_id)
        if task.status != TaskStatus.cancelled:
            task.status = TaskStatus.failed
            task.error = str(e)[:500]
            task.finished_at = _now()
            db.commit()
            mate = agent_service.get_agent_by_id(db, task.agent_mate_id)
            name = f"@{mate.agent_id}" if mate else "An agent"
            _system(db, cid, f"{name} failed to respond.")


# ---------------------------------------------------------------- control

def stop(db: Session, conversation_id: UUID, user_id: UUID) -> int:
    """Cancel queued and running tasks. A running task's output is discarded when it ends."""
    n = (db.query(AgentTask)
         .filter(AgentTask.conversation_id == conversation_id, AgentTask.status.in_(_ACTIVE_STATES))
         .update({"status": TaskStatus.cancelled, "finished_at": _now()},
                 synchronize_session=False))
    db.commit()
    if n:
        user = db.get(User, user_id)
        _system(db, conversation_id, f"@{user.username} stopped {n} task(s).")
    return n


def list_tasks(db: Session, conversation_id: UUID, limit: int = 50) -> list[AgentTask]:
    return (db.query(AgentTask).options(joinedload(AgentTask.agent))
            .filter(AgentTask.conversation_id == conversation_id)
            .order_by(AgentTask.created_at.desc()).limit(limit).all())


def recover(db: Session):
    """Call once at startup: tasks interrupted by a restart are failed, queued ones resume."""
    db.query(AgentTask).filter(AgentTask.status == TaskStatus.running).update(
        {"status": TaskStatus.failed, "error": "Server restarted", "finished_at": _now()},
        synchronize_session=False)
    db.commit()
    for (cid,) in list(db.query(AgentTask.conversation_id)
                       .filter(AgentTask.status == TaskStatus.queued).distinct()):
        _kick(cid)