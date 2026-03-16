import subprocess
from urllib import response
from openai import OpenAI
from ollama import ChatResponse, chat
import json
from google import genai
from google.genai import types
import mimetypes


class LLM:

    def __init__(self, model_family: str, model: str, params, context):
        self.model_family = model_family
        self.model = model
        self.context = context
        self.api_key = self.get_key(self.model_family)
        self.parameters = self.get_model_params(
            self.model_family, self.model, params)

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
                defined_parameters[p] = params[p]
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
        except Exception as e:
            print("Error generating response... skipping...")
            print(e)
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

    def gemini_prompt(self, message_list, response_struct, context):
        client = genai.Client(api_key=self.api_key)
        system_instruction = None
        contents = []
        for msg in message_list:
            role = msg.get("role")
            content = msg.get("content")
            if role == "system":
                system_instruction = content
            else:
                gemini_role = "model" if role == "assistant" else "user"                
                contents.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })
        if context is not None:
            for o in context:
                upload_config = types.UploadFileConfig(mime_type="text/plain")
                ontology = client.files.upload(file=o, config=upload_config)
                contents.append({
                    "role": "user",
                    "parts": [
                        #This part has to be manually added since i have found a way to guess the mime type.
                        types.Part.from_uri(file_uri=ontology.uri, mime_type=ontology.mime_type),
                        {"text": f"Context file: {ontology.display_name}"}
                    ]
                })
        response = client.models.generate_content(
            model=self.model,
            contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                )
            )
        return response.text if response_struct is None else response_struct(**json.loads(response.text))

    def prompt(self, message_list, response_struct, context):
        if self.model_family == "OpenAI":
            return self.openai_prompt(message_list, response_struct)
        if self.model_family == "Gemini":
            return self.gemini_prompt(message_list, response_struct,context)
        # NOTE: Insert other LLM APIs here. Using Ollama API will be the default behaviour
        else:
            return self.ollama_prompt(message_list, response_struct)
