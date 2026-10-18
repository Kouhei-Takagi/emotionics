import concurrent.futures
from typing import Any, Dict
from .core import gyo

def gyo_matrix(
    text: str,
    subject: str,
    circuit: str,
    intent: str,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    [Emotionics Observation Protocol]
    3つの権力勾配（upward, downward, symmetrical）を並列シミュレーションし、
    それぞれのGyo（推定）結果をそのまま返却します。
    
    ※この関数は構造的な差異の「数値化」や「判定」を行いません。
    出力された3つの結果の差異（Delta）から、現在の権力勾配の歪みや
    レッドラインの接近を読み解くのは、観測者（ユーザー）の役割です。
    """
    gradients = ["upward", "downward", "symmetrical"]
    results = {}

    # I/OバウンドなLLMリクエストのため、スレッドプールを使用して並列実行
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_grad = {
            executor.submit(
                gyo,
                text=text,
                subject=subject,
                circuit=circuit,
                power_gradient=grad,
                intent=intent,
                **kwargs
            ): grad for grad in gradients
        }

        # 完了したものから順次結果を取得
        for future in concurrent.futures.as_completed(future_to_grad):
            grad = future_to_grad[future]
            try:
                results[grad] = future.result()
            except Exception as exc:
                results[grad] = {"error": str(exc)}

    return {
        "mode": "gyo_matrix",
        "results": results
    }