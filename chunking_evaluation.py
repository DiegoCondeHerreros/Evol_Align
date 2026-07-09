from llm_interface import LLM


class AlignmentEvaluation():

    def __init__(self, experiment):
        self.exp = experiment
        self.set_judge_model()

    def set_judge_model(self):
        # NOTE: Whilst LLM-as-a-judge has shown potential, there is
        # always the possibility of a simpler binary classification model
        # is there any way where we could use the a small human evaluation
        # session to fine tune an exisiting classifier? Do these even exist?
        model = LLM(
            model_family="Gemini",
            model="gemini-3.5-flash",
            params={"temperature": 0.0, "seed": 7264},
            context=None
        )
        self.judge = model
