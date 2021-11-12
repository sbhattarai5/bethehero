class ReturnObj:
    """This object records the return data, errorcode, lastfunction (lfunction) called and a meaningful message"""

    def __init__(self, data=None, lfunction=None, errorcode=0, success=None, msg=None):
        self.data = data
        self.lfunction = lfunction
        self.errorcode = errorcode
        self.success = success
        self.msg = msg
