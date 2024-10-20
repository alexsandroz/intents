"""Script to update a language."""

import argparse
from functools import partial

import os
from ruamel.yaml import YAML
import shutil

from .const import (
    INTENTS_FILE,
    LANGUAGES_FILE,
    RESPONSE_DIR,
    ROOT,
    SENTENCE_DIR,
    TESTS_DIR,
)
from .util import YamlDumper, get_base_arg_parser

yaml = YAML(typ='rt')


def get_arguments() -> argparse.Namespace:
    """Get parsed passed in arguments."""
    parser = get_base_arg_parser()
    parser.add_argument(
        "language",
        type=str,
        help="ISO 639 code of the language.",
    )
    return parser.parse_args()


def run() -> int:
    args = get_arguments()

    base_dir = SENTENCE_DIR / "en"
    update_dir = SENTENCE_DIR / args.language
    update_language(base_dir, update_dir, args.language)

    base_dir = RESPONSE_DIR / "en"
    update_dir = RESPONSE_DIR / args.language
    update_language(base_dir, update_dir, args.language)

    base_dir = TESTS_DIR / "en"
    update_dir = TESTS_DIR / args.language
    update_language(base_dir, update_dir, args.language)

    return 0


def update_language(base_dir, update_dir, lang):
    for base_file in os.listdir(base_dir):
        if base_file.endswith(".yaml"):
            base_file_path = os.path.join(base_dir, base_file)
            update_file_path = os.path.join(update_dir, base_file)

            with open(base_file_path, 'r') as f_base:
                dados_base = yaml.load(f_base)

            # Checks if the update file already exists
            if os.path.exists(update_file_path):
                with open(update_file_path, 'r') as f_update:
                    dados_update = yaml.load(f_update)

                # Replaces values, maintaining existing values
                def replace_recursively(dados, dict_ref):
                    for key, value in dados.items():
                        if isinstance(value, dict):
                            replace_recursively(value, dict_ref.get(key, {}))

                        elif isinstance(value, list):
                            for i, item in enumerate(value):
                                if isinstance(item, dict):
                                    l = dict_ref.get(key, []) if dict_ref else []
                                    l_ref = l[i] if i < len(l) else {}
                                    replace_recursively(item, l_ref)
                                elif dict_ref and key in dict_ref and i < len(dict_ref[key]):
                                    value[i] = dict_ref[key][i]
                                else:
                                    value[i] = item
                                    value.yaml_add_eol_comment("#TODO translate", key=i)
                        elif dict_ref and key in dict_ref:
                            dados[key] = dict_ref[key]
                        else:
                            dados[key] = value
                            dados.yaml_add_eol_comment("#TODO translate", key=key)

                replace_recursively(dados_base, dados_update)

            # Save changes while preserving the structure
            import sys
            yaml.width = 1024
            dados_base['language'] = lang

            with open(update_file_path, 'w') as f_saida:
                yaml.dump(dados_base, f_saida)
            print(update_file_path)
