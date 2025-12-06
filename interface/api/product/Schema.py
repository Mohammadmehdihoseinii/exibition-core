from pydantic import BaseModel, Field
from typing import List, Optional,Any

class ProductImageSchema(BaseModel):
    url: str
    orginal_name: str
    id: int = 0

class ProductBrochureSchema(BaseModel):
    url: str
    orginal_name: str
    title: str

class ProductCreateSchema(BaseModel):
    title: str
    summary: Optional[str] = None
    long_description: Optional[str] = None
    video_pitch_url: Optional[str] = None
    price_range: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class ProductUpdateSchema(BaseModel):
    title: str = None
    summary: Optional[str] = None
    long_description: Optional[str] = None
    video_pitch_url: Optional[str] = None
    price_range: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class ProductResponse(BaseModel):
    id: int
    company_id: int
    title: str
    summary: Optional[str]
    long_description: Optional[str]
    video_pitch_url: Optional[str]
    price_range: Optional[str]

    tags: List[str] = []
    images: List[ProductImageSchema] = []
    brochures: List[ProductBrochureSchema] = []

class ProductImage:
    url: str
    orginal_name: str
    id: int
