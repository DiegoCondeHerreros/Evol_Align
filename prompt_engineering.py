import json
import argparse
import csv

from llm_interface import LLM
from structured_outputs import *
from utils import KeyValue


def run(args):
    prompt = args.prompt
    model_family = args.model_family
    model = args.model
    params = args.params
    structure = args.structure


def main():
    parser = argparse.ArgumentParser(
        prog='LLM Alignment Prompt Engineering',
        description='A python script for automating parts of the prompt engineering process'
    )
    parser.add_argument(
        '-p',
        type=str,
        help='The prompt format that will be used, accepts the format "<prompt name>.txt", and searches in the "prompts" directory',
        dest='prompt',
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
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
