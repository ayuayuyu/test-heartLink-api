from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json

from src.WsManager import WsManager
from src.filter import filter
from src.models import Datas
from src.models import Device


app = FastAPI()
manager = WsManager()
filters = filter()

# CORSの設定を追加
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",  # すべてのオリジンを許可する場合
    allow_credentials=True,
    allow_methods=["*"],  # すべてのHTTPメソッドを許可 (GET, POSTなど)
    allow_headers=["*"],  # すべてのHTTPヘッダーを許可
)
    
@app.get("/")
async def get():
    return HTMLResponse("Hello World!")

# @app.post("/id")
# async def id_endpoint(device:Device):
#     """
#     デバイスのIDを受け取るエンドポイント
#     """
#     print("device", device)
#     #一つ目のデバイスIDを取得する
#     if filters.get_count() == 0 :
#         filters.set_deviceId_1(device.id)
#         print(f"player1: {device.id}")
#         filters.set_count(1)
#         return {"player": "1"}
#     #二つ目のデバイスIDを取得する
#     elif filters.get_count() == 1:
#         filters.set_deviceId_2(device.id)
#         filters.set_count(2)
#         print(f"player2: {device.id}")
#         return {"player": "2"}
    
@app.get("/reset")
async def reset_endpoint():
    """
    フロント側から受け取るstatus
    すべてをリセットするエンドポイント
    """
    filters.allReset()
    return {"status": "reset"}
        
@app.post("/data")
#それぞれの心拍数を取得するエンドポイント
async def data_endpoint(data: Datas):
    print(f"心拍数: {data.heartRate}")
    #それぞれのデバイスIDと心拍をdictで一つにまとめる
    manager.device_data[data.player]= data.heartRate
    #JSON方式
    json_data = {
        "player1": filters.get_deviceId_1(),
        "heartRate1": manager.device_data.get(filters.get_deviceId_1()),
        "player2": filters.get_deviceId_2(),
        "heartRate2": manager.device_data.get(filters.get_deviceId_2()),
    }
    # 全クライアントにメッセージを送信(JSON方式)
    await manager.broadcast(json.dumps(json_data),filters.get_roomId())
    return {"status":"status"}


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    filters.set_roomId(room_id)
    await manager.connect(websocket, room_id)
    try:
        while True:
            # クライアントからのメッセージ受信
            data = await websocket.receive_text()
            #JSON形式
            json_data = {
                "id1": filters.get_deviceId_1(),
                "heartRate1": data,
                "id2": filters.get_deviceId_2(),
                "heartRate2": data,
            }
            # ルーム内の全クライアントにブロードキャスト(JSON形式)
            await manager.broadcast(json.dumps(json_data), room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
