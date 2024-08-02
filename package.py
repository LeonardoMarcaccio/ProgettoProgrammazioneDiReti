import json

class Package:
    def __init__(self, code, content=None):
        self.code = code
        self.content = content
    
    def toJSON(obj):
        return json.dumps(obj, default=lambda obj: obj.__dict__)

    def fromJSON(obj):
        tmp = json.loads(obj)
        return Package(tmp['code'], tmp['content'])