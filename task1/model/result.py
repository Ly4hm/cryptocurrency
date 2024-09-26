from __future__ import annotations

class Result:
    """存储操作状态"""

    def __init__(self, status: bool, message: str = None) -> None:
        self.status = status
        self.message = message
        
    @staticmethod
    def err(message: str) -> Result:
        "产生 False 类型的工厂方法"
        return Result(False, message)

    @staticmethod
    def ok(message: str = None) -> Result:
        "产生 True 类型的工厂方法"
        return Result(True, message)
    
    @staticmethod
    def check(result: Result) -> bool:
        "检查 Result 是否为 OK"
        return result.status == True