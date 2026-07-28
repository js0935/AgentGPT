"""使用者資料模型 — 定義使用者基礎資訊與組織角色的 Pydantic 結構。"""

from typing import Optional

from pydantic import BaseModel, Field


class OrganizationRole(BaseModel):
    id: str
    role: str
    organization_id: str


class UserBase(BaseModel):
    id: str
    name: Optional[str]
    email: Optional[str]
    image: Optional[str] = Field(default=None)
    organization: Optional[OrganizationRole] = Field(default=None)

    @property
    def organization_id(self) -> Optional[str]:
        return self.organization.organization_id if self.organization else None
