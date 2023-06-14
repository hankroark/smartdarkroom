# Copyright 2023 Hank Roark
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""
This module holds the notion of a print.  Prints are made up of print steps.
There are all kinds of prints in here, from simple one step prints to more
complex multi-step prints.  Mostly supports f-stop style operations.
"""

from abc import ABC

class PrintStep():
    """"
    Represents an atomic print step.  An atomic print step has a duration for the print,
    a prompt to help the user remember what the step is for, a grade (as in black and white
    multicontrast printing grade), and the option to have a before print step duration.
    The before print step duration is designed so a printer can step for dodge burn steps
    with the enlarger on before the actual exposure (imagine holding a dodging card up so
    no light reaches the print, but lets the printer get aligned before the actual exposure
    step).  A print step is immutable after being created.
    """

    def __init__(self, duration, *, user_prompt="", grade=None, before_step_duration=0):
        """
        Constructions a single print step.
        
        Parameters:
            duration (float): Required.  The exposure for the print in seconds.

        Keyword Parameters:
            user_prompt (string): The prompt to remind the user what the step is for or what do before the step. Default: empty string.
            grade (float): The grade of the multicontrast print to make. Default: None.  Just needs an object that can be compared with equality.
            before_step_duration (float): The amount of time to turn on the enlarger light before the actual exposure. If set to -1 there is
                no pause or user prompt before the step begins (useful for dodges). Default: 0.
        """
        self._duration = duration
        self._user_prompt = user_prompt
        self._grade = grade
        self._before_duration = before_step_duration
        
    def __str__(self):
        """
        Returns a user friend representation of the print step.

        Returns:
            string of a user friendly view of this print step.
        """
        before_step_action = None
        if self.before_step_duration > 0:
            before_step_action = f"Preview {self.before_step_duration:.1f} sec w/light"
        elif self.before_step_duration == 0:
            before_step_action = "No pre-step preview light"
        else:
            before_step_action = "No pre-step user prompt (step is continuation of previous step)"

        return f"PrintStep(Exposure {self.duration:.1f} sec, " + \
                 f"Grade {self.grade}, " + \
                 f"{self.user_prompt}, " + \
                 before_step_action + ")"
    
    @property
    def duration(self):
        """
        The length of the exposure duration in seconds. Read-only.
        """
        return self._duration
    
    @property
    def user_prompt(self):
        """
        The prompt to help the user remember what the step is for, or what to before the step starts. Read-only.
        """
        return self._user_prompt
    
    @property
    def before_step_duration(self):
        """
        The length of the pre-exposure time to have the enlarger on in seconds.  ead-only.
        """
        return self._before_duration
    
    @property
    def grade(self):
        """
        The grade of the filter to use in this step.  For example, 00, 0, 1, 1.5, and so on. Read-only.
        """
        return self._grade
        

class BasicPrint(ABC):
    """
    This is the base class of all prints, represents what is common for all types of prints.  It is an abstract base class,
    meaning normally a user will not make one of these direction.  Prints are made up of an ordered list of PrintSteps.
    """

    def __init__(self, steps=[], notes=""):
        """
        Constructs a print with a set of initial print steps.

        Parameters:
            steps (list of PrintSteps): the steps of the prints.  Defaults to an empty list [].
            notes (String): just some notes to go along with the print.  Put anything useful to you in here.
        """
        self._print_list = steps
        self._notes = notes

    def __str__(self):
        """
        Returns a user friend representation of the print, with details for each step.  Each step is numbered and this
        is number is used in some other methods later.

        Returns:
            string of a user friendly view of this entire print.
        """
        representation = f"{self._print_type()}(\n"
        for i, step in enumerate(self.get_print_list()):
            representation += f"    {i+1}: {step},\n"
        representation += f"Notes: {self._notes}\n"
        representation += ")"
        return representation
    
    def _print_type(self):
        """
        Provides a method to describe the type of print.  Used in the user representation of the print.

        Returns:
            string used to describe the print. Defaults to the class name of the print.
        """
        return self.__class__.__name__
        
    def get_print_list(self):
        """
        Allows access to the all the steps of the print.

        Returns:
            list of print steps.
        """
        return self._print_list

    def _set_print_list(self, steps):
        """
        Allows the list of print steps to be replaced with a new list of print steps.

        Parameters:
            steps (list of PrintSteps): the steps of the prints.
        """
        self._print_list = steps

    def __add__(self, other):
        """
        Creates a new Print with the two print lists combined into one new Print.

        Returns:
            basic_print : `BasicPrint`
                A BasicPrint that is the two Prints append in order.  Because it is now a BasicPrint only very limited operations are available.
        """
        return BasicPrint(self.get_print_list() + other.get_print_list())
    
    def __getitem__(self, key):
        """
        Allows to get a particular PrintStep from this print, based on the index (base 0).  This is just like getting an object from any
        Python list.

        Parameters:
            key (int): The offset from the beginning of the Print to return.

        Returns:
            print_step : `PrintStep` 
                A single PrintStep at the offset given.
        """
        return self.get_print_list()[key]
    
    @property
    def notes(self):
        """
        Some notes to go along with the print, anything needed to remind the printer about the print.
        """
        return self._notes    
    
    @notes.setter
    def notes(self, new_notes):
        self._notes = new_notes


class OneExposurePrint(BasicPrint):
    """
    This is the most basic print that a user would create.  It assume one and only one step in the print sequence.  Once created it is
    immutable (unchangeable).  The user prompt is pre-defined.
    """

    def __init__(self, print_duration, *, grade=2.5, before_step_duration=0):
        """
        Constructs a one exposure print.
        
        Parameters:
            print_duration (float): Required.  The exposure for the print in seconds.

        Keyword Parameters:
            grade (float): The grade of the multicontrast print to make. Default: 2.5.  Just needs an object that can be compared with equality.
            before_step_duration (float): The amount of time to turn on the enlarger light before the actual exposure. Default: 0.
        """
        steps = [ PrintStep(print_duration, grade=grade, user_prompt="Place paper for print.", before_step_duration=before_step_duration) ]
        super().__init__(steps = steps)

    @classmethod
    def from_step(cls, source_print, step_number, *, before_step_duration=0):
        """
        Constructs a new OneExposurePrint from the step in another print.  Used typically to pull a print steps from a test strip into a single print. 
        Grade of the new print is the same as the original print step.

        Parameters:
            source_print (BasicPrint): the source Print to pull from.
            step_number (int): The number step from the source Print (1 is the first step, 2 is the second step, etc)

        Keyword Parameters:
            before_step_duration (float): The amount of time to turn on the enlarger light before the actual exposure. Default: 0.
        """
        original_step = source_print[step_number-1]
        return cls(print_duration=original_step.duration, grade=original_step.grade, \
                   before_step_duration=before_step_duration)


class MultiStepPrint(BasicPrint):
        """
        This is a flexible print object.  It supports multiple steps prints, for things like dodging and burning.
        Everything in this Multistep print is done on a base duration and then stops of dodging and burning.  
        If the base duration is changed, all of the dodging and burning durations are recalculated automatically.
        The class supports one contrast grade of printing, but by appending more than one MultiStepPrint together
        one can get split-grade printing (e.g., fullprint = lowgrade + highgrade).
        """

        def __init__(self, base_duration, *, grade=2.5, user_prompt="Place paper for print.", before_step_duration=0):
            """
            Creates a new MultiStepPrint with a base duration and establishes the grade for all the steps.

            Parameters:
                base_duration (float): The MultiStepPrints base exposure duration in seconds. Required.

            Keyword Parameters:
                grade (float): The contrast grade of the print. Can be any object with equality. Default is 2.5.
                user_prompt (string): A prompt to tell the printer what this step is about or what to do ahead of this step.
                    Default is "Place paper for print."
                before_step_duration (float): The amount of time to turn on the enlarger light before the actual exposure. Default: 0.
            """
            self._base_duration = base_duration
            self._base_grade = grade
            self._base_before_step_duration = before_step_duration
            self._base_user_prompt = user_prompt
            self._burn_steps_in_stops = []
            self._dodge_steps_in_stops = []
            self._total_dodge_stops = 0
            self._total_dodge_duration = 0
            super().__init__()
            self._build_print_list()

        @classmethod
        def from_step(cls, source_print, step_number, *, before_step_duration=0):
            """
            Constructs a new MultiStepPrint from the step in another print.  Used typically to pull a print step from a test strip as
            the base duration and grade for a MultiStepPrint.

            Parameters:
                source_print (BasicPrint): the source Print to pull from.
                step_number (int): The number step from the source Print (1 is the first step, 2 is the second step, etc)

            Keyword Parameters:
                before_step_duration (float): The amount of time to turn on the enlarger light before the actual exposure. Default: 0.
            """
            original_step = source_print[step_number-1]
            return cls(base_duration=original_step.duration, grade=original_step.grade, \
                      before_step_duration=before_step_duration)
        
        @classmethod
        def ilford_split_grade(cls, total_duration, *, low_grade=0, high_grade=5, before_steps_duration=0):
            """
            Creates two MultiPrintStep objects, one at a low contrast grade and one at a hight contrast grade.  
            Used for quickly making the basis of a split grade print.  Splits the total
            duration equally between the two objects.  Based on the Ilford Way of creating split grade prints, see
            https://www.darkroomdave.com/tutorial/split-grade-printing-the-ilford-way-using-ilford-multigrade-under-the-lens-filters/
            Once these are returned dodge and burn steps can optionally be added to both objects, and the objects concatenated to 
            make a final print sequence.

            Parameters:
                total_duration (float): The total duration of both grades of prints.

            Keyword Parameters:
                low_grade (float): The contrast grade of the lower contrast print sequence.  Default is 0.
                high_grade (float): The contrast grade of the higher contrast print sequence.  Default is 5.
                before_step_duration (float): The amount of time to turn on the enlarger light before the actual exposure. Default: 0.

            Returns:
                low_grade_print : 'MultiStepPrint'
                    The low grade print
                high_grade_print : 'MultiStepPrint'
                    The high grade print
            """
            low_grade_print = cls(base_duration = total_duration/2,
                                  grade = low_grade,
                                  before_step_duration = before_steps_duration)
            high_grade_print = cls(base_duration = total_duration/2,
                                   grade = high_grade,
                                   user_prompt = "Leave paper in place for print.",
                                   before_step_duration = before_steps_duration)
            
            return low_grade_print, high_grade_print
        
        @classmethod
        def ilford_split_grade_from_step(cls, source_print, step_number, *, before_step_duration=0):
            """
            Creates two MultiPrintStep objects, one at a low contrast grade and one at a hight contrast grade.  
            Used for quickly making the basis of a split grade print.  Pulls from an existing print step, like from a test strip.
            Splits the total duration equally between the two objects.  Based on the Ilford Way of creating split grade prints, see
            https://www.darkroomdave.com/tutorial/split-grade-printing-the-ilford-way-using-ilford-multigrade-under-the-lens-filters/
            Once these are returned dodge and burn steps can optionally be added to both objects, and the objects concatenated to 
            make a final print sequence.

            Parameters:
                source_print (BasicPrint): the source Print to pull from.
                step_number (int): The number step from the source Print (1 is the first step, 2 is the second step, etc)

            Keyword Parameters:
                before_step_duration (float): The amount of time to turn on the enlarger light before the actual exposure. Default: 0.

            Returns:
                low_grade_print : 'MultiStepPrint'
                    The low grade print.  Will be at grade 0.
                high_grade_print : 'MultiStepPrint'
                    The high grade print.  Will be at grade 5
            """
            original_step = source_print[step_number-1]
            return cls.ilford_split_grade(total_duration=original_step.duration, \
                                          before_steps_duration=before_step_duration)


        @property
        def base_duration(self):
            """
            The length of the exposure duration in seconds (float). Recalculates all other steps based on this new duration when set.
            """
            return self._base_duration
        
        @base_duration.setter
        def base_duration(self, new_duration):
            self._base_duration = new_duration
            self._build_print_list()

        @property
        def grade(self):
            """
            The grade of all the steps in the print. Float.  Examples are 0, 0.5, 1, 1.5, and so on.  Rebuilds the steps of the print based on the new grade.
            """
            return self._base_grade
        
        @grade.setter
        def grade(self, new_grade):
            self._base_grade = new_grade
            self._build_print_list()

        @property
        def base_user_prompt(self):
            """
            A prompt to tell the printer what the base step is about or what to do ahead of the base step.  String type.
            """
            return self._base_user_prompt
        
        @base_user_prompt.setter
        def base_user_prompt(self, new_base_user_prompt):
            self._base_user_prompt = new_base_user_prompt
            self._build_print_list()

        # TODO make base before actions mutable

        def _build_print_list(self):
            """
            Anytime the MultiStepPrint is created or changed, all of the steps are automatically recalculated.
            First the removal (dodge) steps and then the base step and then the additive (burn) steps.
            These are then place back into the print in order of base, then dodges, and then burns.
            """
            dodge_steps = self._calc_dodge_steps()
            base_step = PrintStep(duration=self._base_duration - self._total_dodge_duration, \
                                  grade=self._base_grade, \
                                  user_prompt=self._base_user_prompt, \
                                  before_step_duration=self._base_before_step_duration)
            burn_steps = self._calc_burn_steps()
            self._set_print_list([base_step]+dodge_steps+burn_steps)

        def remove_step(self, step_number):
            """
            Allow the user to remove a step.  Any step except the base step can be removed.  Triggers a recalculation.

            Parameter:
                step_number (int): The step to remove from the print. Needs to be 2 or greater (base step cannot be removed) but less than or
                    equal to the maximum step number.  To get the list of steps just print() this object.
            """
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
            """
            Calculates all of the burn steps durations based on the number of stops and base duration.
            """
            burn_steps = []
            for step in self._burn_steps_in_stops:
                burn_duration = self._base_duration * 2**step.duration - self._base_duration
                burn_step = PrintStep(duration=burn_duration,  
                                      grade = self._base_grade if step.grade is None else step.grade, 
                                      user_prompt = step.user_prompt, 
                                      before_step_duration = step.before_step_duration)
                burn_steps.append(burn_step)
            return burn_steps

        def burn(self, stops, *, grade=None, before_step_duration=0, subject=""):
            """
            Allows the user to add a burn step to the print.  Burn steps can be done at a grade different than the base print.

            Parameters:
                stops (float): The number of stops of burn to do.

            Keyword Parameters:
                grade (float): The grade of the burn step.  If none specified will default to the grade of the base print.
                before_step_duration (float): The amount of time to turn on the enlarger light before the actual exposure. Default: 0.
                subject (string): The subject to be burned, added to user prompt to aid the printer. Default to empty string.
            """
            user_prompt = f"Burn {subject if subject else 'unspecified subject'} for {stops} stops"
            burn_step = PrintStep(stops, grade=grade,   # Grade of step ignored when building
                                  user_prompt=user_prompt, \
                                  before_step_duration=before_step_duration)
            self._burn_steps_in_stops.append(burn_step)
            self._build_print_list()

        def _calc_dodge_steps(self):
            """
            Calculates all of the dodge steps durations basedon the number of stops and base duration.
            """
            dodge_steps = []
            self._total_dodge_stops = 0
            self._total_dodge_duration = 0
            for step in self._dodge_steps_in_stops:
                step_stops = step.duration
                dodge_duration = self._base_duration - self._base_duration / (2**step_stops) # duration is stops here
                self._total_dodge_stops += step_stops
                self._total_dodge_duration += dodge_duration
                dodge_step = PrintStep(duration=dodge_duration,  
                                       grade = self._base_grade, 
                                       user_prompt = step.user_prompt, 
                                       before_step_duration = step.before_step_duration)
                dodge_steps.append(dodge_step)
            return dodge_steps

        def dodge(self, stops, *, before_step_duration=-1, subject=""):
            """
            Allows the user to add a dodge step to the print.  Dodge steps are always done at the grade of the base print.

            Parameters:
                stops (float): The number of stops of dodge to do.

            Keyword Parameters:
                before_step_duration (float): The amount of time to turn on the enlarger light before the actual exposure. Default: -1 (meaning
                    that there will not be a pause or user prompt, just an audible signal that the dodge time is beginning.)
                subject (string): The subject to be burned, added to user prompt to aid the printer. Default to empty string.

            Raises:
                Exception
                    Raised if the proposed dodge step would make the total of all the dodge steps greater than the base duration.
            """

            proposed_dodge_duration = self._base_duration - self._base_duration / (2**stops)
            if (proposed_dodge_duration + self._total_dodge_duration) > self._base_duration:
                raise Exception("Cannot add dodge step that would make total dodge duration greater than base duration.")

            user_prompt = f"Dodge {subject if subject else 'unspecified subject'} for {stops} stops"
            dodge_step = PrintStep(stops, grade=None, # Grade of step ignored when building
                                   user_prompt=user_prompt, \
                                   before_step_duration=before_step_duration)
            self._dodge_steps_in_stops.append(dodge_step)
            self._build_print_list()
           

class FStopTestStrip(BasicPrint):
    """
    This allows the user to create a test strip.  It assumes a standard non localized test strip is being made.
    Further the first exposure is the entire test strip with successive covering of portions of the test strip
    for each step.  The test strip is based on a base duration and then incremental stops from that duration.

    This sort of test strip is covered in 'Test Strip for Exposure' section of https://www.35mmc.com/13/04/2020/knowing-little-aiming-high-darkroom-technique-part-2-by-sroyon-mukherjee/
    """

    def __init__(self, base=4, steps=5, stops=1/2, middle_out=False, grade=2.5):
        """
        Constructs a new test strip based on a base exposure and offsets from the base in f-stops.
        
        Parameters:
            base (float): The base exposure in seconds. Defaults to 4.
            steps (int): The number of steps/strips in this test print. Defaults to 5.
            stops (float): The number of stops between steps/strips in this test print. Defaults to 1/2.
            middle_out (bool): If true then the base exposure will be the middle of the test strip and offsets will be calculated above and below.
                Useful when one want to fine tune for the base exposure by exploring around a middle. Defaults to False.
            grade (float): The grade used to print the test strip.;
        """
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
        """
        Allows to get a particular PrintStep from this TestString, based on the index (base 0).  This is just like getting an object from any
        Python list.  For an FStopPrint step it is smart and determines the total exposure of the print step (not just the incremental
        exposure) and returns that as an object.

        Parameters:
            key (int): The offset from the beginning of the Print to return.

        Returns:
            A single PrintStep at the offset given.
        """
        print_list = self.get_print_list()
        new_duration = sum([print_list[i].duration for i in range(key+1)])
        template_step=print_list[key]
        return PrintStep( new_duration, grade=template_step.grade )
    
    @classmethod
    def from_step(cls, source_print, step_number, steps=5, stops=1/2, middle_out=False, grade=None):
        """
        Constructs a new FStopTestString from the step in another print.  Used typically to pull a print step from a test strip into
        another test strip to fine turn the exposure or the grade of the print.

        Parameters:
            source_print (BasicPrint): the source Print to pull from.
            step_number (int): The number step from the source Print (1 is the first step, 2 is the second step, etc)
            steps (int): The number of steps/strips in this test print. Defaults to 5.
            stops (float): The number of stops between steps/strips in this test print. Defaults to 1/2.
            middle_out (bool): If true then the base exposure will be the middle of the test strip and offsets will be calculated above and below.
                Useful when one want to fine tune for the base exposure by exploring around a middle. Defaults to False.
            grade (float): The grade used to print the test strip.  If no grade is given (the default) the grade of the original print step will be used.
        """
        original_step = source_print[step_number-1]
        if grade is None:
            grade = original_step.grade

        return cls(base=original_step.duration, steps=steps, stops=stops, middle_out=middle_out, grade=grade)


class LocalizedFStopTestStrip(BasicPrint):
    """
    This allows the user to create a test strip.  It assumes a standard localized test strip is being made.
    The test strip is based on a base duration and then incremental stops from that duration.

    This sort of test strip is covered in 'Localised Test Strips' section of https://www.35mmc.com/13/04/2020/knowing-little-aiming-high-darkroom-technique-part-2-by-sroyon-mukherjee/
    """

    def __init__(self, base=4, steps=5, stops=1/2, middle_out=False, grade=2.5):
        """
        Constructs a new test strip based on a base exposure and offsets from the base in f-stops.
        
        Parameters:
            base (float): The base exposure in seconds. Defaults to 4.
            steps (int): The number of steps/strips in this test print. Defaults to 5.
            stops (float): The number of stops between steps/strips in this test print. Defaults to 1/2.
            middle_out (bool): If true then the base exposure will be the middle of the test strip and offsets will be calculated above and below.
                Useful when one want to fine tune for the base exposure by exploring around a middle. Defaults to False.
            grade (float): The grade used to print the test strip.;
        """
        if middle_out:
            base = base / 2**(int(steps/2)*stops)

        steps = [ PrintStep(base * 2**(i*stops), 
                            grade=grade,
                            user_prompt="Place paper for print." if i==0 else "Move paper to expose next strip.") 
                   for i in range(0, steps) ] 
        super().__init__(steps = steps)

    @classmethod
    def from_step(cls, source_print, step_number, steps=5, stops=1/2, middle_out=False, grade=None):
        """
        Constructs a new LocalizedFStopTestStrip from the step in another print.  Used typically to pull a print step from a test strip into
        another test strip to fine turn the exposure or the grade of the print.

        Parameters:
            source_print (BasicPrint): the source Print to pull from.
            step_number (int): The number step from the source Print (1 is the first step, 2 is the second step, etc)
            steps (int): The number of steps/strips in this test print. Defaults to 5.
            stops (float): The number of stops between steps/strips in this test print. Defaults to 1/2.
            middle_out (bool): If true then the base exposure will be the middle of the test strip and offsets will be calculated above and below.
                Useful when one want to fine tune for the base exposure by exploring around a middle. Defaults to False.
            grade (float): The grade used to print the test strip.  If no grade is given (the default) the grade of the original print step will be used.
        """
        original_step = source_print[step_number-1]
        if grade is None:
            grade = original_step.grade

        return cls(base=original_step.duration, steps=steps, stops=stops, middle_out=middle_out, grade=grade)
    

class BarnbaumTestPrint(BasicPrint):
    """
    Bruce Barnbaum recommends creating full test prints (if on needs a test print at all).  The test print
    should be the entire area to be printed, with exposures a n seconds, 2n seconds, and 3n seconds (this
    corresponds, assuming 2n seconds is the target, to a section 1 stop below target, a section at target,
    and a section at about 2/3rd stop above target exposure).  Bruce's argument is a test print creates
    the most information, at the least cost, to start and get to the final print.  The goal is also to decide
    which parts of the print to expose each duration to maximize the information and not just blindly
    cover a third of the print each time.
    
    We set the target (2n) exposure time to default to 15 seconds, because 15 seconds is a good base for any dodging
    that might need to happen during main exposure.  Bruce teaches to learn to look at the light from the
    enlarger reflected on the printing easel and learn to adjust the exposure (f-stops on the enlarger lens plus
    neutral density filters plus and filters to adjust grade) to hit close to that 15 second mark.

    See _The Art of Photography_ by Bruce Barnbaum, 2nd edition, pp 185-189.
    """

    def __init__(self, base=7.5, middle_out=False, grade=2):
        """
        Constructs a new test print based on a base exposure and offsets from the base in seconds.
        
        Parameters:
            base (float): The base exposure in seconds. Defaults to 7.5.
            middle_out (bool): If true then the base exposure will be the middle of the test prints and offsets will be calculated above and below.
                Useful when one want to fine tune for the base exposure by exploring around a middle. Defaults to False.
            grade (float): The grade used to print the test print.
        """
        if middle_out:
            base = base / 2.
        
        if base < 1.:
                raise Exception(f"Calculated exposure of {base} is below 1 second, too short for printing.")

        steps = [ PrintStep(base * i, 
                            grade=grade,
                            user_prompt="Place paper for print." if i==1 else "Move paper to cover portion of print.") 
                   for i in range(1, 4) ] 
        super().__init__(steps = steps)

    @classmethod
    def from_step(cls, source_print, step_number, middle_out=False, grade=None):
        """
        Constructs a new BarnbaumTestPrint from the step in another print.  Used typically to pull a print step from a test strip or print
        into another test strip/print to fine turn the exposure or the grade of the print.

        Parameters:
            source_print (BasicPrint): the source Print to pull from.
            step_number (int): The number step from the source Print (1 is the first step, 2 is the second step, etc)
            middle_out (bool): If true then the base exposure will be the middle of the test strip and offsets will be calculated above and below.
                Useful when one want to fine tune for the base exposure by exploring around a middle. Defaults to False.
            grade (float): The grade used to print the test strip.  If no grade is given (the default) the grade of the original print step will be used.
        """
        original_step = source_print[step_number-1]
        if grade is None:
            grade = original_step.grade

        return cls(base=original_step.duration, middle_out=middle_out, grade=grade)
    