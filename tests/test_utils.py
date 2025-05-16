class mockDatetime():
    def __init__(self, time):
        self._time = time
    def now(self,*args,**kwargs):
        return self._time