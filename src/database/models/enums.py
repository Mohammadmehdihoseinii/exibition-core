import enum

class RoleEnum(str, enum.Enum):
    visitor = "visitor"
    exhibitor = "exhibitor"
    organizer = "organizer"
    admin = "admin"

class ApprovalStatusEnum(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class ExpoStatusEnum(str, enum.Enum):
    draft = "draft"
    live = "live"
    ended = "ended"

class VipLevelEnum(str, enum.Enum):
    normal = "normal"
    silver = "silver"
    gold = "gold"
    platinum = "platinum"

class FavoriteTypeEnum(str, enum.Enum):
    exhibition = "exhibition"
    company = "company"
    product = "product"
    message = "message"

class ViewTargetEnum(str, enum.Enum):
    exhibition = "exhibition"
    company = "company"
    product = "product"
    intro = "intro"
