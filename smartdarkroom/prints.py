from abc import ABC

class PrintStep():
    def __init__(self, duration, user_prompt="", before_step_duration=0, before_step_light=False):
        self._duration = duration
        self._user_prompt = user_prompt
        self._before_duration = before_step_duration
        self._before_light = before_step_light
        
    def __repr__(self):
        return f"PrintStep(Exposure {self.duration:.1f} sec, " + \
                 f"Preview {self.before_step_duration:.1f} sec w/light {self.before_step_light}, " + \
                 f"{self.user_prompt!r})"
    
    @property
    def duration(self):
        return self._duration
    
    @property
    def user_prompt(self):
        return self._user_prompt
    
    @property
    def before_step_duration(self):
        return self._before_duration
    
    @property
    def before_step_light(self):
        return self._before_light
    

class BasicPrint(ABC):
    def __init__(self, steps=[]):
        self._print_list = steps
        
    def get_print_list(self):
        return self._print_list

    def _set_print_list(self, steps):
        self._print_list = steps
    

class OneExposurePrint(BasicPrint):
    def __init__(self, print_duration, before_step_duration=0, before_step_light=False):
        steps = [ PrintStep(print_duration, user_prompt="Place paper for print.", before_step_duration=before_step_duration, before_step_light=before_step_light) ]
        super().__init__(steps = steps)


class FStopTestStrip(BasicPrint):
    def __init__(self, base=4, steps=5, stops=1/2, middle_out=False):
        if middle_out:
            base = base / 2**(int(steps/2)*stops)
 
        total_steps = [ base * 2**(i*stops) for i in range(0,steps) ]
        total_steps.insert(0, 0)
        incremental_steps = [j-i for i, j in zip(total_steps[:-1], total_steps[1:])]  # take differences between steps
        steps = [ PrintStep(i, 
                            user_prompt="Place paper for print." if i==base else "Move card to block just exposed test strip.")
                   for i in incremental_steps ] 
        super().__init__(steps = steps)


class LocalizedFStopTestStrip(BasicPrint):
    def __init__(self, base=4, steps=5, stops=1/2, middle_out=False):
        if middle_out:
            base = base / 2**(int(steps/2)*stops)

        steps = [ PrintStep(base * 2**(i*stops), 
                            user_prompt="Place paper for print." if i==0 else "Move paper to expose next strip.") 
                   for i in range(0, steps) ] 
        super().__init__(steps = steps)
