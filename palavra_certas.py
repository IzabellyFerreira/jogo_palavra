import pygame
import random
import sqlite3

# Inicializando o Pygame
pygame.init()

# Definindo o tamanho da janela
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Palavra Certa")

# Definindo cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Definindo o relógio
clock = pygame.time.Clock()

# Fonte do texto
font = pygame.font.SysFont("arial", 30)

# Lista de palavras válidas
word_list = [
    "casa", "bola", "amor", "livro", "floresta", "montanha", "carro", 
    "escola", "futebol", "piano", "viagem", "computador", "teclado", "criatividade"
]

# Função para gerar letras aleatórias (letras da palavra + adicionais)
def generate_letters(word, level):
    letters = list(word)  # Letras da palavra
    if level == 1:
        extra_letters = 0
    elif level == 2:
        extra_letters = 0
    elif level == 3:
        extra_letters = 0
    elif level == 4:
        extra_letters = 0

    max_letters = 4 + 2 * (level - 1)
    total_letters = len(word) + extra_letters

    if total_letters > max_letters:
        extra_letters = max_letters - len(word)

    for _ in range(extra_letters):
        letter = random.choice(word)
        letters.append(letter)

    random.shuffle(letters)
    return letters

# Função para exibir o texto na tela
def display_text(text, x, y, color=BLACK):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Função para exibir o ranking
def display_ranking():
    conn = sqlite3.connect('ranking.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS ranking (id INTEGER PRIMARY KEY, name TEXT, score INTEGER)")
    cursor.execute("SELECT * FROM ranking ORDER BY score DESC LIMIT 5")
    rankings = cursor.fetchall()
    conn.close()

    y_offset = 60
    for ranking in rankings:
        display_text(f"{ranking[1]}: {ranking[2]}", 20, y_offset)
        y_offset += 40

# Função para capturar o nome do jogador
def get_player_name():
    name = ""
    name_entered = False
    while not name_entered:
        screen.fill(WHITE)
        display_text("Digite seu nome:", 300, 200)
        display_text(name, 300, 250)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_RETURN:
                    if name:
                        name_entered = True
                else:
                    name += event.unicode

    return name

# Função para salvar o nome e a pontuação no banco de dados
def save_score(player_name, score):
    conn = sqlite3.connect('ranking.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS ranking (id INTEGER PRIMARY KEY, name TEXT, score INTEGER)")
    cursor.execute("INSERT INTO ranking (name, score) VALUES (?, ?)", (player_name, score))
    conn.commit()
    conn.close()

# Função principal do jogo
def game_loop(player_name):
    game_over = False
    score = 0
    level = 1
    word_input = ""
    used_words = []

    current_word = random.choice(word_list)

    while current_word in used_words:
        current_word = random.choice(word_list)
    used_words.append(current_word)

    letters = generate_letters(current_word, level)
    
    # Definindo o tempo inicial com base no nível
    if level == 1:
        time_limit = 12
    elif level == 2:
        time_limit = 9
    elif level == 3:
        time_limit = 6

    time_remaining = time_limit
    start_ticks = pygame.time.get_ticks()

    while not game_over:
        screen.fill(WHITE)

        seconds_elapsed = (pygame.time.get_ticks() - start_ticks) / 1000
        time_remaining = max(0, time_limit - seconds_elapsed)

        if time_remaining == 0:
            screen.fill(RED)
            display_text(f"A palavra correta era: {current_word}", 20, 60, WHITE)
            pygame.display.update()
            pygame.time.delay(2000)
            word_input = ""
            level = 1
            current_word = random.choice(word_list)
            while current_word in used_words:
                current_word = random.choice(word_list)
            used_words.append(current_word)
            letters = generate_letters(current_word, level)
            
            # Redefinir tempo com base no nível
            if level == 1:
                time_limit = 12
            elif level == 2:
                time_limit = 9
            elif level == 3:
                time_limit = 6
            
            time_remaining = time_limit
            start_ticks = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    word_input = word_input[:-1]
                elif event.key == pygame.K_RETURN:
                    if word_input == current_word:
                        score += 10 * level
                        level += 1

                        if level > 4:
                            level = 4

                        # Redefinir o tempo com base no nível
                        if level == 1:
                            time_limit = 12
                        elif level == 2:
                            time_limit = 9
                        elif level == 3:
                            time_limit = 6
                        else:
                            time_limit = 4

                        current_word = random.choice(word_list)
                        while current_word in used_words:
                            current_word = random.choice(word_list)
                        used_words.append(current_word)
                        letters = generate_letters(current_word, level)
                        word_input = ""
                        start_ticks = pygame.time.get_ticks()
                    else:
                        screen.fill(RED)
                        display_text("Você errou! Saindo do jogo...", 200, 250, WHITE)
                        pygame.display.update()
                        pygame.time.delay(2000)
                        save_score(player_name, score)
                        game_over = True

                else:
                    if len(word_input) < len(current_word):
                        word_input += event.unicode

        if word_input == current_word:
            screen.fill(GREEN)
        elif len(word_input) >= len(current_word) and word_input != current_word:
            screen.fill(RED)

        display_text(f"Letras: {' '.join(letters)}", 20, 20, BLUE)
        display_text(f"Palavra formada: {word_input}", 20, 60)
        display_text(f"Nível: {level}", 20, 140)
        display_text(f"Tempo restante: {int(time_remaining)}s", 20, 180, RED if time_remaining < 3 else BLACK)

        pygame.display.update()
        clock.tick(30)

    show_menu()

# Função para desenhar botões com efeitos
def draw_button(text, x, y, width, height, base_color, hover_color, action=None):
    mouse_x, mouse_y = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)

    # Verificar se o mouse está sobre o botão
    if button_rect.collidepoint(mouse_x, mouse_y):
        pygame.draw.rect(screen, hover_color, button_rect, border_radius=10)
    else:
        pygame.draw.rect(screen, base_color, button_rect, border_radius=10)

    # Desenhar o texto do botão
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

    # Ação ao clicar no botão
    if pygame.mouse.get_pressed()[0] and button_rect.collidepoint(mouse_x, mouse_y):
        if action:
            action()

# Função para mostrar o menu principal com botões clicáveis
def show_menu():
    menu_running = True
    while menu_running:
        screen.fill(WHITE)

        # Desenhar os botões
        draw_button("Jogar", 300, 200, 200, 50, BLUE, YELLOW, lambda: start_game())
        draw_button("Ranking", 300, 260, 200, 50, ORANGE, RED, lambda: show_ranking())
        draw_button("Sair", 300, 320, 200, 50, GREEN, RED, lambda: pygame.quit())

        pygame.display.update()

        # Captura de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu_running = False

# Função para iniciar o jogo
def start_game():
    player_name = get_player_name()
    game_loop(player_name)

# Função para mostrar o ranking
def show_ranking():
    screen.fill(WHITE)
    display_text("Ranking:", 20, 20, BLACK)
    display_ranking()

    # Botão Voltar
    draw_button("Voltar", 300, 500, 200, 50, GREEN, RED, lambda: show_menu())

    pygame.display.update()
    pygame.time.delay(5000)

# Iniciar o jogo
if __name__ == "__main__":
    show_menu()



