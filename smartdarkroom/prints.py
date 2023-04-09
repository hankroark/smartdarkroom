
class BasicPrint():
    def __init__(self, steps=[]):
        self._print_list = steps
        
    def get_print_list(self):
        return self._print_list

    def _set_print_list(self, steps):
        self._print_list = steps
    

class OneExposurePrint(BasicPrint):
    def __init__(self, print_duration):
        steps = [ {"duration":print_duration, "user_prompt":"Place paper for print."} ]
        super().__init__(steps = steps)


class LocalizedFStopTestStrip(BasicPrint):
    def __init__(self, base=4, steps=5, stops=2):
        steps = [ {"duration":base * 2**(i/stops), 
                   "user_prompt": "Place paper for print." if i==0 else "Move paper to expose next strip."} 
                   for i in range(0, steps) ] 
        super().__init__(steps = steps)
