from abc import ABC
# from enum import Enum

class PrintStep():
    def __init__(self, duration, user_prompt="", grade=None, before_step_duration=0, before_step_light=False):
        self._duration = duration
        self._user_prompt = user_prompt
        self._grade = grade
        self._before_duration = before_step_duration
        self._before_light = before_step_light
        
    def __repr__(self):
        return f"PrintStep(Exposure {self.duration:.1f} sec, " + \
                 f"Grade {self.grade}, " + \
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
    
    @property
    def grade(self):
        return self._grade
        

class BasicPrint(ABC):
    def __init__(self, steps=[]):
        self._print_list = steps

    def __repr__(self):
        representation = f"{self._print_type()}(\n"
        for i, step in enumerate(self.get_print_list()):
            representation += f"    {i}: {step},\n"
        representation += ")"
        return representation
    
    def _print_type(self):
        return self.__class__.__name__
        
    def get_print_list(self):
        return self._print_list

    def _set_print_list(self, steps):
        self._print_list = steps

    def _add_step(self, step):
        self._print_list.append(step)
    

class OneExposurePrint(BasicPrint):
    def __init__(self, print_duration, grade=2.5, before_step_duration=0, before_step_light=False):
        steps = [ PrintStep(print_duration, grade=grade, user_prompt="Place paper for print.", before_step_duration=before_step_duration, before_step_light=before_step_light) ]
        super().__init__(steps = steps)


class MultiStepPrint(BasicPrint):
    def __init__(self, base_duration, base_grade=2.5, user_prompt="Place paper for print.", before_step_duration=0, before_step_light=False):
        self._base_duration = base_duration
        self._base_grade = base_grade
        self._base_before_step_duration = 0
        self._base_before_step_light = before_step_light
        self._base_user_prompt = user_prompt
        self._base_step = PrintStep(base_duration, grade=base_grade, \
                                    user_prompt=user_prompt, \
                                    before_step_duration=before_step_duration, \
                                    before_step_light=before_step_light)
        self._burn_steps = []
        self._dodge_steps = []
        self._total_dodge_steps = 0
        self._total_dodge_duration = 0
        super().__init__()
        self._build_print_list()

    # at some point create from test print

    def burn(self, stops, burn_grade=None, before_step_duration=0, before_step_light=False, subject=""):
        burn_duration = self._base_duration * stops if stops < 1 else self._base_duration * 2**(stops-1)
        if burn_grade is None:
            burn_grade = self._base_grade
        user_prompt = f"Burn {subject} for {stops} stops."

        burn_step = PrintStep(burn_duration, grade=burn_grade, user_prompt=user_prompt, \
                         before_step_duration=before_step_duration, \
                         before_step_light=before_step_light)
        self._burn_steps.append(burn_step)

        self._build_print_list()

    def _build_print_list(self):
        self._set_print_list([self._base_step] + self._dodge_steps + self._burn_steps)

    def dodge(self, stops, dodge_grade=None, before_step_duration=0, before_step_light=False, subject=""):
        if stops > 1:
            raise Exception("Cannot add dodge step that is greater than 1 stop.")
        
        if stops + self._total_dodge_steps > 1:
            raise Exception("Cannot add dodge step that would take stops dodged to greater than 1 stop.")
        
        dodge_duration = self._base_duration * stops 
        self._total_dodge_steps += stops
        self._total_dodge_duration += dodge_duration

        if dodge_grade is None:
            dodge_grade = self._base_grade
        user_prompt = f"Dodge {subject} for {stops} stops."

        dodge_step = PrintStep(dodge_duration, grade=dodge_grade, user_prompt=user_prompt, \
                         before_step_duration=before_step_duration, \
                         before_step_light=before_step_light)
        self._dodge_steps.append(dodge_step)
        
        self._base_step = PrintStep(self._base_duration - self._total_dodge_duration, \
                                    grade=self._base_grade, \
                                    user_prompt=self._base_user_prompt, \
                                    before_step_duration=self._base_before_step_duration, \
                                    before_step_light=self._base_before_step_light)
        
        self._build_print_list()

class FStopTestStrip(BasicPrint):
    def __init__(self, base=4, steps=5, stops=1/2, middle_out=False, grade=2.5):
        if middle_out:
            base = base / 2**(int(steps/2)*stops)
 
        total_steps = [ base * 2**(i*stops) for i in range(0,steps) ]
        total_steps.insert(0, 0)
        incremental_steps = [j-i for i, j in zip(total_steps[:-1], total_steps[1:])]  # take differences between steps
        steps = [ PrintStep(i, 
                            grade=grade,
                            user_prompt="Place paper for print." if i==base else "Move card to block just exposed test strip.")
                   for i in incremental_steps ] 
        super().__init__(steps = steps)


class LocalizedFStopTestStrip(BasicPrint):
    def __init__(self, base=4, steps=5, stops=1/2, middle_out=False, grade=2.5):
        if middle_out:
            base = base / 2**(int(steps/2)*stops)

        steps = [ PrintStep(base * 2**(i*stops), 
                            grade=grade,
                            user_prompt="Place paper for print." if i==0 else "Move paper to expose next strip.") 
                   for i in range(0, steps) ] 
        super().__init__(steps = steps)
