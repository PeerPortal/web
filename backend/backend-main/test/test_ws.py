import asyncio
import websockets
import json

async def test_ws_connection():
    """测试基本 WebSocket 连接"""
    try:
        uri = "ws://localhost:8000/ws/chat"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket 连接成功")
            
            # 发送测试消息
            test_message = "你好，WebSocket！"
            await websocket.send(test_message)
            print(f"📤 发送消息: {test_message}")
            
            # 接收回复
            response = await websocket.recv()
            print(f"📥 收到回复: {response}")
            
    except Exception as e:
        print(f"❌ WebSocket 连接失败: {e}")

async def test_multiple_messages():
    """测试发送多条消息"""
    try:
        uri = "ws://localhost:8000/ws/chat"
        async with websockets.connect(uri) as websocket:
            print("✅ 开始多消息测试")
            
            messages = [
                "第一条测试消息",
                "第二条测试消息", 
                "第三条测试消息",
                "JSON格式消息: " + json.dumps({"type": "test", "data": "测试数据"})
            ]
            
            for i, msg in enumerate(messages, 1):
                await websocket.send(msg)
                response = await websocket.recv()
                print(f"  {i}. 发送: {msg[:20]}... | 回复: {response[:30]}...")
                
    except Exception as e:
        print(f"❌ 多消息测试失败: {e}")

async def run_all_ws_tests():
    """运行所有 WebSocket 测试"""
    print("🚀 开始 WebSocket 测试...")
    print("=" * 50)
    
    print("\n🔌 测试基本连接:")
    await test_ws_connection()
    
    print("\n📬 测试多条消息:")
    await test_multiple_messages()
    
    print("\n✨ WebSocket 测试完成!")

if __name__ == "__main__":
    asyncio.run(run_all_ws_tests()) 