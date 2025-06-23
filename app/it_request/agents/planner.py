class Planner:
    def __init__(self):
        pass

    def __call__(self, state: dict) -> dict:
        # 模拟执行任务
        return {
            **state,
            "output": "我们已为您提交了重置密码的请求。"
        }

