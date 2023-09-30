class Square:
    def __init__(self, length) -> None:
        if type(length) not in [int,float]:
            raise TypeError('Length must be an integer and float')
        if length <= 0:
            raise ValueError('Length must not be negative')
        
        self.length = length
        

    def area(self):
        return self.length * self.length

