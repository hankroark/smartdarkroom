from abc import ABC

class PrintStep():
    def __init__(self, duration, user_prompt="", grade=None, before_step_duration=0, before_step_light=False):
        self._duration = duration
        self._user_prompt = user_prompt
        self._grade = grade
        self._before_duration = before_step_duration
        self._before_light = before_step_light
        
    def __str__(self):
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

    def __str__(self):
        representation = f"{self._print_type()}(\n"
        for i, step in enumerate(self.get_print_list()):
            representation += f"    {i+1}: {step},\n"
        representation += ")"
        return representation
    
    def _print_type(self):
        return self.__class__.__name__
        
    def get_print_list(self):
        return self._print_list

    def _set_print_list(self, steps):
        self._print_list = steps

    def __add__(self, other):
        return BasicPrint(self.get_print_list() + other.get_print_list())
    
    def __getitem__(self, key):
        return self.get_print_list()[key]
    

class OneExposurePrint(BasicPrint):
    def __init__(self, print_duration, grade=2.5, before_step_duration=0, before_step_light=False):
        steps = [ PrintStep(print_duration, grade=grade, user_prompt="Place paper for print.", before_step_duration=before_step_duration, before_step_light=before_step_light) ]
        super().__init__(steps = steps)

    @classmethod
    def from_step(cls, source_print, step_number, before_step_duration=0, before_step_light=False):
        original_step = source_print[step_number-1]
        return cls(print_duration=original_step.duration, grade=original_step.grade, \
                   before_step_duration=before_step_duration, \
                   before_step_light=before_step_light)


class MultiStepPrint(BasicPrint):
        def __init__(self, base_duration, grade=2.5, user_prompt="Place paper for print.", before_step_duration=0, before_step_light=False):
            self._base_duration = base_duration
            self._base_grade = grade
            self._base_before_step_duration = before_step_duration
            self._base_before_step_light = before_step_light
            self._base_user_prompt = user_prompt
            self._burn_steps_in_stops = []
            self._dodge_steps_in_stops = []
            self._total_dodge_steps = 0
            self._total_dodge_duration = 0
            super().__init__()
            self._build_print_list()

        @classmethod
        def from_step(cls, source_print, step_number, *, before_step_duration=0, before_step_light=False):
            original_step = source_print[step_number-1]
            return cls(base_duration=original_step.duration, grade=original_step.grade, \
                      before_step_duration=before_step_duration, \
                      before_step_light=before_step_light)
        
        @classmethod
        def ilford_split_grade(cls, total_duration, *, low_grade=0, high_grade=5, before_steps_duration=0, before_steps_light=0):
            low_grade_print = cls(base_duration = total_duration/2,
                                  grade = low_grade,
                                  before_step_duration = before_steps_duration,
                                  before_step_light = before_steps_light)
            high_grade_print = cls(base_duration = total_duration/2,
                                   grade = high_grade,
                                   user_prompt = "Leave paper in place for print.",
                                   before_step_duration = before_steps_duration,
                                   before_step_light = before_steps_light)
            
            return low_grade_print, high_grade_print
        
        @classmethod
        def ilford_split_grade_from_step(cls, source_print, step_number, *, before_step_duration=0, before_step_light=False):
            original_step = source_print[step_number-1]
            return cls.ilford_split_grade(total_duration=original_step.duration, \
                                          before_steps_duration=before_step_duration, \
                                          before_steps_light=before_step_light)


    
    # TODO @classmethod ilford split grade strategy, return tuple

        @property
        def base_duration(self):
            return self._base_duration
        
        @base_duration.setter
        def base_duration(self, new_duration):
            self._base_duration = new_duration
            self._build_print_list()

        @property
        def grade(self):
            return self._base_grade
        
        @grade.setter
        def grade(self, new_grade):
            self._base_grade = new_grade
            self._build_print_list()

        @property
        def base_user_prompt(self):
            return self._base_user_prompt
        
        @base_user_prompt.setter
        def base_user_prompt(self, new_base_user_prompt):
            self._base_user_prompt = new_base_user_prompt
            self._build_print_list()

        # TODO make base before actions mutable

        def _build_print_list(self):
            dodge_steps = self._calc_dodge_steps()
            base_step = PrintStep(duration=self._base_duration - self._total_dodge_duration, \
                                  grade=self._base_grade, \
                                  user_prompt=self._base_user_prompt, \
                                  before_step_duration=self._base_before_step_duration, \
                                  before_step_light=self._base_before_step_light)
            burn_steps = self._calc_burn_steps()
            self._set_print_list([base_step]+dodge_steps+burn_steps)

        def remove_step(self, step_number):
            if step_number == 1:
                print("Cannot remove the base step.  No action taken.")
                return
            if step_number > len(self.get_print_list() ):
                print(f"No step number {step_number} existing in print list.  No action take.")
                return
            
            all_steps = self._dodge_steps_in_stops + self._burn_steps_in_stops
            item_to_remove = all_steps.pop(step_number-2)
            if item_to_remove in self._dodge_steps_in_stops:
                self._dodge_steps_in_stops.remove(item_to_remove)
            else:
                self._burn_steps_in_stops.remove(item_to_remove)

            self._build_print_list()

        def _calc_burn_steps(self):
            burn_steps = []
            for step in self._burn_steps_in_stops:
                burn_duration = self._base_duration * 2**step.duration - self._base_duration
                burn_step = PrintStep(duration=burn_duration,  
                                      grade = self._base_grade, 
                                      user_prompt = step.user_prompt, 
                                      before_step_duration = step.before_step_duration, 
                                      before_step_light=step.before_step_light)
                burn_steps.append(burn_step)
            return burn_steps

        def burn(self, stops, *, before_step_duration=0, before_step_light=False, subject=""):
            user_prompt = f"Burn {subject} for {stops} stops."
            burn_step = PrintStep(stops, grade=None,   # Grade of step ignored when building
                                  user_prompt=user_prompt, \
                                  before_step_duration=before_step_duration, \
                                  before_step_light=before_step_light)
            self._burn_steps_in_stops.append(burn_step)
            self._build_print_list()

        def _calc_dodge_steps(self):
            dodge_steps = []
            self._total_dodge_stops = 0
            self._total_dodge_duration = 0
            for step in self._dodge_steps_in_stops:
                step_stops = step.duration
                dodge_duration = self._base_duration - self._base_duration / (2**step_stops) # duration is stops here
                self._total_dodge_steps += step_stops
                self._total_dodge_duration += dodge_duration
                dodge_step = PrintStep(duration=dodge_duration,  
                                       grade = self._base_grade, 
                                       user_prompt = step.user_prompt, 
                                       before_step_duration = step.before_step_duration, 
                                       before_step_light=step.before_step_light)
                dodge_steps.append(dodge_step)
            return dodge_steps

        def dodge(self, stops, *, before_step_duration=0, before_step_light=False, subject=""):
            proposed_dodge_duration = self._base_duration - self._base_duration / (2**stops)
            if (proposed_dodge_duration + self._total_dodge_duration) > self._base_duration:
                raise Exception("Cannot add dodge step that would make total dodge duration greater than base duration.")

            user_prompt = f"Dodge {subject} for {stops} stops."
            dodge_step = PrintStep(stops, grade=None, # Grade of step ignored when building
                                   user_prompt=user_prompt, \
                                   before_step_duration=before_step_duration, \
                                   before_step_light=before_step_light)
            self._dodge_steps_in_stops.append(dodge_step)
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

    def __getitem__(self, key):
        print_list = self.get_print_list()
        new_duration = sum([print_list[i].duration for i in range(key+1)])
        template_step=print_list[key]
        return PrintStep( new_duration, grade=template_step.grade )
    
    @classmethod
    def from_step(cls, source_print, step_number, steps=5, stops=1/2, middle_out=False, grade=None):
        original_step = source_print[step_number-1]
        if grade is None:
            grade = original_step.grade

        return cls(base=original_step.duration, steps=steps, stops=stops, middle_out=middle_out, grade=grade)


class LocalizedFStopTestStrip(BasicPrint):
    def __init__(self, base=4, steps=5, stops=1/2, middle_out=False, grade=2.5):
        if middle_out:
            base = base / 2**(int(steps/2)*stops)

        steps = [ PrintStep(base * 2**(i*stops), 
                            grade=grade,
                            user_prompt="Place paper for print." if i==0 else "Move paper to expose next strip.") 
                   for i in range(0, steps) ] 
        super().__init__(steps = steps)

    @classmethod
    def from_step(cls, source_print, step_number, steps=5, stops=1/2, middle_out=False, grade=None):
        original_step = source_print[step_number-1]
        if grade is None:
            grade = original_step.grade

        return cls(base=original_step.duration, steps=steps, stops=stops, middle_out=middle_out, grade=grade)
    
    # TODO create split grade test strip classes

