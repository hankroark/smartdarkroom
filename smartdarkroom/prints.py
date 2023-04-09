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
