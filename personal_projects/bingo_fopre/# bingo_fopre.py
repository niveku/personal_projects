# bingo_fopre.py

# Cartones extraídos de tus 6 PDFs
CARDS = {
    "3106": [
        [3, 16, 31, 59, 68],
        [12, 21, 33, 50, 70],
        [14, 25, None, 49, 69],   # centro = comodín
        [2, 18, 43, 48, 64],
        [10, 19, 38, 54, 71],
    ],
    "3107": [
        [10, 17, 39, 51, 64],
        [13, 30, 41, 50, 67],
        [12, 25, None, 47, 74],
        [14, 26, 37, 53, 61],
        [7, 28, 45, 56, 66],
    ],
    "3108": [
        [11, 26, 34, 59, 72],
        [3, 21, 32, 54, 66],
        [5, 27, None, 53, 68],
        [1, 19, 37, 51, 62],
        [8, 28, 35, 47, 73],
    ],
    "3109": [
        [6, 23, 35, 57, 61],
        [4, 17, 43, 52, 70],
        [14, 24, None, 60, 71],
        [15, 16, 42, 46, 63],
        [13, 27, 38, 58, 73],
    ],
    "3110": [
        [14, 29, 43, 58, 61],
        [3, 18, 37, 49, 74],
        [15, 26, None, 48, 72],
        [12, 24, 34, 59, 66],
        [7, 23, 41, 55, 71],
    ],
    "3111": [
        [2, 20, 38, 46, 67],
        [3, 26, 44, 48, 71],
        [9, 21, None, 50, 68],
        [7, 25, 35, 55, 75],
        [5, 19, 45, 54, 62],
    ],
}

# Colores ANSI sencillos
RESET = "\033[0m"
BOLD = "\033[1m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
FG_BLACK = "\033[30m"

def render_card(serie, grid, marked):
    print(f"{BOLD}Serie {serie}{RESET}")
    headers = ["F", "O", "P", "R", "E"]
    print(" ".join(f"{h:^5}" for h in headers))
    for r in grid:
        row_str = []
        for val in r:
            if val is None:
                # comodín
                cell = f"{BG_BLUE}{FG_BLACK}{'FREE':^5}{RESET}"
            else:
                if val in marked:
                    cell = f"{BG_YELLOW}{FG_BLACK}{str(val):^5}{RESET}"
                else:
                    cell = f"{str(val):^5}"
            row_str.append(cell)
        print(" ".join(row_str))
    print()

def render_all(marked):
    # limpiar pantalla opcional:
    # print("\033c", end="")
    for serie in sorted(CARDS.keys()):
        render_card(serie, CARDS[serie], marked)

def main():
    marked = set()
    print("Bingo FOPRE cargado. Cartones: ", ", ".join(sorted(CARDS.keys())))
    render_all(marked)
    while True:
        cmd = input("Ingresa número, 'reset' o 'salir': ").strip().lower()
        if cmd == "salir":
            break
        elif cmd == "reset":
            marked.clear()
            print("Se limpiaron las marcas.\n")
            render_all(marked)
        else:
            # intentar convertir a número
            try:
                num = int(cmd)
            except ValueError:
                print("Entrada no válida.")
                continue
            marked.add(num)
            print(f"Marcado {num}.\n")
            render_all(marked)

if __name__ == "__main__":
    main()