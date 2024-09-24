class User:
    """用户数据类
    Attribute:
        - userid 用户标识
        - sign_chance 剩余签名次数
    """

    def __init__(self, userid, sign_chance) -> None:
        self.userid = userid
        self.sign_chance = sign_chance

    @property
    def userid(self):
        return self.userid

    @property
    def sign_chance(self):
        return self.sign_chance
