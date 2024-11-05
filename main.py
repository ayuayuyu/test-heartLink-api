from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import json

from src.WsManager import WsManager
from src.filter import filter
from src.models import Datas
from src.models import Device
from src.models import Players
from src.models import Names
from src.models import Array


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

@app.post("/name")
async def name_endpoint(data: Names):
    """
    名前を受け取るエンドポイント
    """
    if data.player == "1":
        filters.set_name1(data.name)
        print(f"name: {filters.get_name1()}")
        return {"name": {filters.get_name1()}}
    elif data.player == "2":
        filters.set_name2(data.name)
        print(f"name: {filters.get_name2()}")
        return {"name": {filters.get_name2()}}
    else:
        return {"name": "erro"}
    
@app.post("/topicId")
async def topicId_endpoint(data:Players):
    if data.player == "1":
        if filters.get_indexCount1() == 0:
            filters.set_topicId(0,data.id)
            filters.set_indexCount1(1)
            return {"id" : {data.id}}
        elif filters.get_indexCount1() == 1:
            filters.set_topicId(2,data.id)
            filters.set_indexCount1(2)
            return {"id" : {data.id}}
        else:
            return {"id": "erro"}
    elif data.player == "2":
        if filters.get_indexCount2() == 0:
            filters.set_topicId(1,data.id)
            filters.set_indexCount2(1)
            return {"id" : {data.id}}
        elif filters.get_indexCount2() == 1:
            filters.set_topicId(3,data.id)
            filters.set_indexCount2(2)
            return {"id" : {data.id}}
        else:
            return {"id": "erro"}
    else:
        return{"player": "erro"}
    
    
@app.post("/topicArray")
async def topicArray_endpoint(array:Array):
    if filters.get_count() == 0:
        filters.set_topicArray1(0,array.array1)
        filters.set_topicArray2(0,array.array2)
        filters.set_count(1)
        return {"array": {array}}
    elif filters.get_count() == 1:
        filters.set_topicArray1(1,array.array1)
        filters.set_topicArray2(1,array.array2)
        filters.set_count(2)
        return {"array": {array}}
    elif filters.get_count() == 2:
        filters.set_topicArray1(2,array.array1)
        filters.set_topicArray2(2,array.array2)
        filters.set_count(3)
        return {"array": {array}}
    elif filters.get_count() == 3:
        filters.set_topicArray1(3,array.array1)
        filters.set_topicArray2(3,array.array2)
        filters.set_count(3)
        return {"array": {array}}
    else:
        return{"array": "erro"}
    
    
@app.get("/getName")
async def getName_endpoint():
    return {"player1": {filters.get_name1()} ,"player2": {filters.get_name2()}}
    
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
        "topicId": filters.get_topicId(),
    }
    # 全クライアントにメッセージを送信(JSON方式)
    await manager.broadcast(json.dumps(json_data))
    return {"status":"status"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
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
                "topicId": filters.get_topicId(),
            }
            # ルーム内の全クライアントにブロードキャスト(JSON形式)
            await manager.broadcast(json.dumps(json_data))
    except WebSocketDisconnect:
        manager.disconnect(websocket)
