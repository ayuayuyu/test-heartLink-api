from pydantic import BaseModel


class Datas(BaseModel):
    heartRate: int
    player: str
    
class Reset(BaseModel):
    value: str
    
class Device(BaseModel):
    id: str
    
class Status(BaseModel):
    status: str
    
class PlayerName(BaseModel):
    player: str
    name: str
    
class Players(BaseModel):
    player: str