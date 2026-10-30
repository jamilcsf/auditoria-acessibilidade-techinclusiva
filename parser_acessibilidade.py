
import json
from pathlib import Path
from collections import Counter

PASTA = Path(__file__).parent
ARQUIVO_ORIGINAL = PASTA / "resultados" / "resultado_axe.json"
ARQUIVO_CORRIGIDO = PASTA / "resultados" / "resultado_axe_corrigido.json"

MAPEAMENTO_WCAG = {
    "button-name": ("4.1.2", "A", "Nome, função e valor"),
    "color-contrast": ("1.4.3", "AA", "Contraste mínimo"),
    "html-has-lang": ("3.1.1", "A", "Idioma da página"),
    "image-alt": ("1.1.1", "A", "Conteúdo não textual")
}

GRAVIDADES = {
    "critical": "Crítica",
    "serious": "Séria",
    "moderate": "Moderada",
    "minor": "Menor"
}


def carregar_json(caminho):
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if isinstance(dados, list):
        if not dados:
            raise ValueError(f"Arquivo vazio: {caminho}")
        dados = dados[0]

    return dados


def resumir_auditoria(dados, titulo):
    violacoes = dados.get("violations", [])
    total = sum(len(v.get("nodes", [])) for v in violacoes)
    gravidades = Counter()

    print("\n" + "=" * 65)
    print(titulo)
    print("=" * 65)
    print("URL:", dados.get("url", "Não informada"))
    print("Data:", dados.get("timestamp", "Não informada"))
    print("Tipos de violações:", len(violacoes))
    print("Total de ocorrências:", total)

    for v in violacoes:
        impacto = v.get("impact", "Não classificado")
        gravidade = GRAVIDADES.get(impacto, impacto)
        nodes = v.get("nodes", [])
        gravidades[gravidade] += len(nodes)

        wcag = MAPEAMENTO_WCAG.get(v.get("id"))

        print("\nRegra:", v.get("id"))
        print("Gravidade:", gravidade)
        print("Ocorrências:", len(nodes))

        if wcag:
            print(
                f"WCAG 2.1: {wcag[0]} - Nível {wcag[1]} "
                f"- {wcag[2]}"
            )

        print("Elementos afetados:")
        for node in nodes:
            for seletor in node.get("target", []):
                print(" -", seletor)

    print("\nResumo por gravidade:")
    for gravidade in ["Crítica", "Séria", "Moderada", "Menor"]:
        print(f"{gravidade}: {gravidades.get(gravidade, 0)}")

    return {
        "tipos": len(violacoes),
        "ocorrencias": total,
        "gravidades": gravidades
    }


def comparar(resultados_antes, resultados_depois):
    antes = resultados_antes["ocorrencias"]
    depois = resultados_depois["ocorrencias"]

    if antes > 0:
        reducao = ((antes - depois) / antes) * 100
    else:
        reducao = 0

    print("\n" + "=" * 65)
    print("             COMPARAÇÃO DAS AUDITORIAS")
    print("=" * 65)
    print(f"Ocorrências antes das correções: {antes}")
    print(f"Ocorrências depois das correções: {depois}")
    print(f"Redução das ocorrências: {reducao:.1f}%")
    print("=" * 65)


def main():
    try:
        original = carregar_json(ARQUIVO_ORIGINAL)
        corrigido = carregar_json(ARQUIVO_CORRIGIDO)

        resultado_antes = resumir_auditoria(
            original, "PRIMEIRA AUDITORIA - HTML ORIGINAL"
        )

        resultado_depois = resumir_auditoria(
            corrigido, "SEGUNDA AUDITORIA - HTML CORRIGIDO"
        )

        comparar(resultado_antes, resultado_depois)

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as erro:
        print("\nERRO:", erro)


if __name__ == "__main__":
    main()
