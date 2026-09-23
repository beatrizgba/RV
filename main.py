import math
from PIL import Image, ImageDraw

# -------------------------------
# CONFIGURACOES DA TELA E CORES
# -------------------------------
LARGURA = 600
ALTURA = 600

BRANCO = (255, 255, 255)
AZUL = (125, 190, 245)
PRETO = (0, 0, 0)
CINZA_GRADE = (220, 220, 220)
CINZA_EIXO = (150, 150, 150)
VERMELHO = (220, 40, 40)


# -------------------------------
# DESENHO BASICO DE PIXEL
# -------------------------------
def pixel(pixels, x, y, cor):
    # Pinta o pixel apenas se estiver dentro da tela.
    if 0 <= x < LARGURA and 0 <= y < ALTURA:
        pixels[x, y] = cor


# -------------------------------
# ALGORITMO DE BRESENHAM
# -------------------------------
def bresenham(pixels, ponto_a, ponto_b, cor=PRETO):
    # Rasterizacao de reta para qualquer direcao.
    x0, y0 = round(ponto_a[0]), round(ponto_a[1])
    x1, y1 = round(ponto_b[0]), round(ponto_b[1])

    dx = abs(x1 - x0)
    dy = abs(y1 - y0)

    passo_x = 1 if x0 < x1 else -1
    passo_y = 1 if y0 < y1 else -1

    erro = dx - dy

    while True:
        pixel(pixels, x0, y0, cor)

        if x0 == x1 and y0 == y1:
            break

        dobro_erro = 2 * erro

        if dobro_erro > -dy:
            erro -= dy
            x0 += passo_x

        if dobro_erro < dx:
            erro += dx
            y0 += passo_y


# -------------------------------
# PREENCHIMENTO SCAN-LINE
# -------------------------------
def scanline(pixels, pontos):
    # Preenche a regiao interna do quadrilatero.
    menor_y = max(0, math.floor(min(y for x, y in pontos)))
    maior_y = min(ALTURA - 1, math.ceil(max(y for x, y in pontos)))

    for y in range(menor_y, maior_y + 1):
        linha = y + 0.5  # usa centro do pixel
        intersecoes = []

        for i in range(4):
            x1, y1 = pontos[i]
            x2, y2 = pontos[(i + 1) % 4]

            # Ignora arestas horizontais
            if y1 == y2:
                continue

            # Verifica se a linha cruza a aresta
            if min(y1, y2) <= linha < max(y1, y2):
                x = x1 + (linha - y1) * (x2 - x1) / (y2 - y1)
                intersecoes.append(x)

        intersecoes.sort()

        # Preenche entre pares de intersecoes
        for i in range(0, len(intersecoes) - 1, 2):
            inicio = max(0, math.ceil(intersecoes[i] - 0.5))
            fim = min(LARGURA - 1, math.floor(intersecoes[i + 1] - 0.5))

            for x in range(inicio, fim + 1):
                pixel(pixels, x, y, AZUL)


# -------------------------------
# GRADE E EIXOS
# -------------------------------
def desenhar_grade_eixos(pixels, draw, passo=50):
    # Desenha linhas verticais da grade
    for x in range(0, LARGURA, passo):
        bresenham(pixels, (x, 0), (x, ALTURA - 1), CINZA_GRADE)
        draw.text((x + 2, 2), str(x), fill=CINZA_EIXO)

    # Desenha linhas horizontais da grade
    for y in range(0, ALTURA, passo):
        bresenham(pixels, (0, y), (LARGURA - 1, y), CINZA_GRADE)
        draw.text((2, y + 2), str(y), fill=CINZA_EIXO)

    # Eixos principais
    bresenham(pixels, (0, 0), (LARGURA - 1, 0), CINZA_EIXO)
    bresenham(pixels, (0, 0), (0, ALTURA - 1), CINZA_EIXO)

    draw.text((5, 5), "(0,0)", fill=CINZA_EIXO)
    draw.text((LARGURA - 20, 5), "X", fill=CINZA_EIXO)
    draw.text((5, ALTURA - 20), "Y", fill=CINZA_EIXO)


# -------------------------------
# MARCACAO DOS VERTICES
# -------------------------------
def desenhar_marcador(pixels, x, y, cor=VERMELHO):
    # Desenha uma pequena cruz no ponto.
    for dx in range(-3, 4):
        pixel(pixels, x + dx, y, cor)

    for dy in range(-3, 4):
        pixel(pixels, x, y + dy, cor)


def rotular_pontos(pixels, draw, pontos):
    # Marca P1, P2, P3 e P4.
    for i, (x, y) in enumerate(pontos, start=1):
        xi = round(x)
        yi = round(y)

        desenhar_marcador(pixels, xi, yi, VERMELHO)

        texto = f"P{i} ({xi},{yi})"

        tx = xi + 6
        ty = yi - 14

        # Ajuste para nao sair da tela
        if tx > LARGURA - 90:
            tx = xi - 90
        if ty < 0:
            ty = yi + 6

        draw.text((tx, ty), texto, fill=VERMELHO)


# -------------------------------
# DESENHO COMPLETO DO QUADRILATERO
# -------------------------------
def desenhar_quadrilatero(pontos, arquivo):
    imagem = Image.new("RGB", (LARGURA, ALTURA), BRANCO)
    pixels = imagem.load()
    draw = ImageDraw.Draw(imagem)

    # Grade e eixos
    desenhar_grade_eixos(pixels, draw)

    # Preenche interior
    scanline(pixels, pontos)

    # Desenha contorno com Bresenham
    for i in range(4):
        bresenham(pixels, pontos[i], pontos[(i + 1) % 4], PRETO)

    # Rotula os vertices
    rotular_pontos(pixels, draw, pontos)

    imagem.save(arquivo)


# -------------------------------
# CENTROIDE DO QUADRILATERO
# -------------------------------
def centroide(pontos):
    # Centroide pela formula do poligono.
    area_dupla = 0.0
    soma_x = 0.0
    soma_y = 0.0

    for i in range(4):
        x1, y1 = pontos[i]
        x2, y2 = pontos[(i + 1) % 4]

        cruzado = x1 * y2 - x2 * y1
        area_dupla += cruzado
        soma_x += (x1 + x2) * cruzado
        soma_y += (y1 + y2) * cruzado

    # Caso degenerado: usa media dos vertices
    if abs(area_dupla) < 1e-9:
        return (
            sum(x for x, y in pontos) / 4,
            sum(y for x, y in pontos) / 4
        )

    cx = soma_x / (3 * area_dupla)
    cy = soma_y / (3 * area_dupla)
    return (cx, cy)


# -------------------------------
# TRANSFORMACAO DE ESCALA
# -------------------------------
def escalar(pontos, sx, sy, pivo):
    cx, cy = pivo
    resultado = []

    for x, y in pontos:
        novo_x = cx + (x - cx) * sx
        novo_y = cy + (y - cy) * sy
        resultado.append((novo_x, novo_y))

    return resultado


# -------------------------------
# TRANSFORMACAO DE ROTACAO
# -------------------------------
def rotacionar(pontos, angulo, pivo):
    # Rotacao 2D usando matriz de rotacao.
    rad = math.radians(angulo)
    c = math.cos(rad)
    s = math.sin(rad)

    cx, cy = pivo
    resultado = []

    for x, y in pontos:
        # translada para o pivô
        xt = x - cx
        yt = y - cy

        # aplica rotacao
        xr = xt * c - yt * s
        yr = xt * s + yt * c

        # volta para a posicao original
        resultado.append((cx + xr, cy + yr))

    return resultado


# -------------------------------
# LEITURA DE DADOS
# -------------------------------
def ler_ponto(numero):
    while True:
        try:
            entrada = input(f"P{numero} - digite x y (0 a 599): ").split()
            x = int(entrada[0])
            y = int(entrada[1])

            if 0 <= x < LARGURA and 0 <= y < ALTURA:
                return (x, y)
            else:
                print("Os valores precisam estar entre 0 e 599.")

        except (ValueError, IndexError):
            print("Digite dois numeros inteiros separados por espaco.")


def ler_numero(mensagem):
    while True:
        try:
            valor = float(input(mensagem).replace(",", "."))
            if math.isfinite(valor):
                return valor
        except ValueError:
            pass

        print("Digite um numero valido.")


# -------------------------------
# PROGRAMA PRINCIPAL
# -------------------------------
def main():
    print("Quadrilatero: informe os vertices na ordem P1 -> P2 -> P3 -> P4")

    pontos = [ler_ponto(i) for i in range(1, 5)]

    angulo = ler_numero("Angulo de rotacao (graus): ")
    sx = ler_numero("Escala sx: ")
    sy = ler_numero("Escala sy: ")

    escolha = ""
    while escolha not in ("1", "2"):
        escolha = input("Pivo: 1 = origem (0,0); 2 = centroide: ").strip()

    if escolha == "1":
        pivo = (0, 0)
    else:
        pivo = centroide(pontos)

    # Transformacoes
    pontos_escalados = escalar(pontos, sx, sy, pivo)
    pontos_rotacionados = rotacionar(pontos, angulo, pivo)
    pontos_combinados = rotacionar(pontos_escalados, angulo, pivo)

    # Gera imagens
    desenhar_quadrilatero(pontos, "original.png")
    desenhar_quadrilatero(pontos_escalados, "escala.png")
    desenhar_quadrilatero(pontos_rotacionados, "rotacao.png")
    desenhar_quadrilatero(pontos_combinados, "escala_e_rotacao.png")

    # Mostra coordenadas finais
    print("\nVertices depois de escala + rotacao:")
    for i, (x, y) in enumerate(pontos_combinados, start=1):
        print(f"P{i} = ({x:.2f}, {y:.2f})")

    print("\nImagens salvas: original.png, escala.png, rotacao.png, escala_e_rotacao.png")
    print("Coordenadas que sairem da tela serao cortadas visualmente na imagem.")


if __name__ == "__main__":
    main()