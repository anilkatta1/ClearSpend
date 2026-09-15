from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import Membership, get_session
from app.domain import Role


@dataclass(frozen=True)
class Principal:
    user_id: str
    organization_id: str
    email: str
    name: str
    role: Role


def principal_from_header(
    session: Annotated[Session, Depends(get_session)],
    demo_user: Annotated[str | None, Header(alias="X-Demo-User")] = None,
) -> Principal:
    if not demo_user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "X-Demo-User is required")
    memberships = session.scalars(
        select(Membership).join(Membership.user).where(Membership.user.has(email=demo_user.lower()))
    ).all()
    if len(memberships) != 1:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Unknown demo identity")
    membership = memberships[0]
    return Principal(
        user_id=membership.user_id,
        organization_id=membership.organization_id,
        email=membership.user.email,
        name=membership.user.name,
        role=Role(membership.role),
    )


PrincipalDep = Annotated[Principal, Depends(principal_from_header)]


def require_roles(*allowed: Role):
    def dependency(principal: PrincipalDep) -> Principal:
        if principal.role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Role is not permitted")
        return principal

    return dependency
