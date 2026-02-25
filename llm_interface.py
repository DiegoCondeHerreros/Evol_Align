import subprocess
from openai import OpenAI
from ollama import ChatResponse, chat
import json

class LLM:

    def __init__(self, model_family: str, model: str, **params):
        self.model_family = model_family
        self.model = model
        self.api_key = self.get_key(self.model_family)
        self.parameters = self.get_model_params(self.model_family, self.model, params)

        if self.api_key is None:
            pull = subprocess.Popen(['ollama', 'pull', self.model])
            pull.wait()

    def get_key(self, model_family):
        src = 'api_key.txt'
        with open(src, 'r+') as f:
            model_families = json.load(f)[0]
        if model_family not in list(model_families.keys()):
            raise NameError(f'{model_family} is not present in api_key.txt')
        model_family_info = model_families[model_family]
        if 'API_KEY' not in list(model_family_info.keys()):
            return None
        else:
            return model_family_info['API_KEY']

    def get_model_params(self, model_family, model, params):
        src = 'api_key.txt'
        with open(src, 'r+') as f:
            model_families = json.load(f)[0]
        if model_family not in list(model_families.keys()):
            raise NameError(f'{model_family} is not present in api_key.txt')
        model_family_info = model_families[model_family]
        if model not in list(model_family_info['Models'].keys()):
            raise NameError(f'{model} is not listed in the {model_family} model family in api_key.txt')
        param_list = model_family_info['Models'][model]
        defined_parameters = {}
        for p in list(params.keys()):
            if p in param_list:
                defined_parameters[p]=params[p]
        return defined_parameters

    def openai_prompt(self, message_list, response_struct):
        client = OpenAI(api_key=self.api_key)
        if response_struct is not None:
            self.parameters['response_format'] = response_struct
        try:
            response = client.beta.chat.completions.parse(
                messages=message_list,
                model=self.model,
                **self.parameters
            )
            if response_struct is not None:
                return response.choices[0].message.parsed
            else:
                return response.choices[0].message.content
        except Exception:
            print("Error generating response... skipping...")
            return "Error"

    def ollama_prompt(self, message_list, response_struct):
        response: ChatResponse = chat(
            model=self.model,
            messages=message_list,
            options=self.parameters,
            format=response_struct.model_json_schema()
        )
        formatted_response = response_struct(
            **json.loads(str(response.message.content)))
        return formatted_response

    def prompt(self, message_list, response_struct):
        if self.model_family == "OpenAI":
            return self.openai_prompt(message_list, response_struct)
        # NOTE: Insert other LLM APIs here. Using Ollama API will be the default behaviour
        else:
            return self.ollama_prompt(message_list, response_struct)
