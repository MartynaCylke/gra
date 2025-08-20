from typing import Dict, Any, List

def make_event(i: int, board: List[str], win: Dict[str, Any], payout: int, wallet_balance: int, state_snapshot: dict) -> Dict[str, Any]:
    return {
        "spin": i,
        "board": board,
        "win": win or None,
        "payout": payout,
        "balance": wallet_balance,
        "state": state_snapshot
    }
