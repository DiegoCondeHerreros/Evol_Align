import json
import argparse
import csv
from pathlib import Path

from llm_interface import LLM
from structured_outputs import *
from utils import KeyValue


def run(args):
    sys_prompt = args.sys_prompt
    user_prompt = args.user_prompt
    model_family = args.model_family
    model = args.model
    params = args.params
    structure = eval(args.structure)
    output = f'output/{args.output}_PrEn.csv'
    context = args.context

    try:
        with open(f'sys_prompts/{sys_prompt}', 'r+')as p:
            sys_prompts = json.load(p)
    except ValueError:
        raise ValueError(
            f'The prompt file /sys_prompts/{sys_prompt} does not exist')

    try:
        with open(f'user_prompts/{user_prompt}', 'r+')as p:
            user_prompts = json.load(p)
    except ValueError:
        raise ValueError(
            f'The prompt file /user_prompts/{user_prompt} does not exist')

    llm = LLM(model_family, model, params, context)

    responses = []

    for t in user_prompts:
        print(f'Running prompt {user_prompts.index(
            t) + 1} of {len(user_prompts)}...')
        full_prompt = sys_prompts[0] + t
        try:
            response_row = []
            response = llm.prompt(full_prompt, structure, context)
            response_row = [response]
            responses.append(response_row)
            print('Success!')
        except Exception as e:
            print(e)
            print(f'Prompt {user_prompts.index(t) + 1} failed. Continuing...')

    print('Prompting complete, writing output...')
    with open(output, "w", newline="") as o:
        writer = csv.writer(o)
        writer.writerows(responses)
        print('Experiment complete!')


def main():
    parser = argparse.ArgumentParser(
        prog='LLM Alignment Prompt Engineering',
        description='A python script for automating parts of the prompt engineering process'
    )
    parser.add_argument(
        '-sp',
        type=str,
        help='The system prompt format that will be used, accepts the format "<prompt name>.txt", and searches in the "sys_prompts" directory',
        dest='sys_prompt',
        required=True
    )
    parser.add_argument(
        '-up',
        type=str,
        help='The user prompt that will be used, accepts the format "<prompt name>.txt", and searches in the "user_propmts" directory',
        dest='user_prompt',
        required=True
    )
    parser.add_argument(
        '-mf',
        type=str,
        help='The model family requested',
        dest='model_family',
        required=True
    )
    parser.add_argument(
        '-m',
        type=str,
        help='The model requested',
        dest='model',
        required=True
    )
    parser.add_argument(
        '-hp',
        nargs='*',
        action=KeyValue,
        help='The hyperparameters for the model',
        dest='params',
    )
    parser.add_argument(
        '-s',
        type=str,
        help='The format responses should follow',
        dest='structure',
        required=True
    )
    parser.add_argument(
        '-o',
        type=str,
        help='The name of the generated output file ("_PrEn" will be appended to denote a prompt engineering survey)',
        dest='output',
        required=True
    )
    parser.add_argument(
        '-c',
        nargs='+',
        type=Path,
        help='The file path of the data that is added context for the prompt',
        dest='context',
        required=False
    )
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
