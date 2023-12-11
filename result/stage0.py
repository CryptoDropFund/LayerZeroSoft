
import os
import sys


root_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..'))
sys.path.append(root_path)
from result.swaps import swaps  # NOQA: E402


def stage0(private_key, START_FROM):
    match START_FROM:
        case 'AVAX':
            swaps(private_key, 'AVAX_USDC')
        case 'MATIC':
            swaps(private_key, 'MATIC_USDC')
        case _:
            print(f'[STAGE 0] Not found start mode')


if __name__ == '__main__':
    print('[STAGE 0] Run global main script!')
