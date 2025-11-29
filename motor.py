def normalizar(valor):
    if valor is None or valor == 0:
        return 0
    return max(0, min(100, valor))

def calc_lucratividade(comissao, cvr, refund):
    if comissao is None or cvr is None or refund is None:
        return 0
    return normalizar(float(comissao) * float(cvr) * (1 - float(refund)))

def calc_estabilidade(vendas_30d, vendas_7d):
    if not vendas_30d or vendas_30d == 0:
        return 0
    variacao = abs(vendas_30d - (vendas_7d or 0))
    estabilidade = vendas_30d / (1 + variacao)
    return normalizar(estabilidade)

def calc_tendencia(vendas_30d, vendas_7d):
    if vendas_7d is None or vendas_30d is None:
        return 0
    tendencia = vendas_7d - (vendas_30d / 4)
    return normalizar(tendencia)

def calc_risco(refund):
    if refund is None:
        return 0
    return normalizar(float(refund) * 100)

def calc_score_global(luc, est, ten, risco):
    return (
        0.40 * luc +
        0.25 * est +
        0.20 * ten -
        0.15 * risco
    )
