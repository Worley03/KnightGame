import pygame
import sys
import os


# Initialize Pygame
pygame.init()

icon = pygame.image.load('knight.png')  # Replace with your image file path
pygame.display.set_icon(icon)

# Constants for the game window and grid
SCREEN_WIDTH = 800 - 376
SCREEN_HEIGHT = 500
BOTTOM_MARGIN = 75  # Space at the bottom for the 'Time Waited' display
GRID_HEIGHT = SCREEN_HEIGHT - BOTTOM_MARGIN
GRID_SIZE = 8
CELL_SIZE = GRID_HEIGHT // GRID_SIZE
FONT_SIZE = CELL_SIZE // 2
BORDER_COLOR = (0, 0, 0)
move_log = []

# Define the height values for each cell in the grid (you would fill these with your desired values)
heights = [[9.0, 8.0, 10.0, 12.0, 11.0, 8.0, 10.0, 17.0],
           [7.0, 9.0, 11.0, 9.0, 10.0, 12.0, 14.0, 12.0],
           [4.0, 7.0, 5.0, 8.0, 6.0, 13.0, 10.0, 15.0],
           [4.0, 10.0, 7.0, 9.0, 6.0, 8.0, 7.0, 9.0],
           [2.0, 6.0, 4.0, 5.0, 9.0, 8.0, 11.0, 13.0],
           [0.0, 3.0, 1.0, 4.0, 2.0, 7.0, 10.0, 7.0],
           [1.0, 2.0, 0.0, 1.0, 2.0, 5.0, 7.0, 6.0],
           [0.0, 2.0, 4.0, 3.0, 5.0, 6.0, 2.0, 4.0]
           ]

# Initialize visits grid with zeros
visits = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("A Knight's Maze")

# Load the font
font = pygame.font.SysFont('Arial', FONT_SIZE)


def draw_checkered_flag(screen, top_right_position, cell_size, flag_size=4, color1=(100, 100, 100), color2=(255, 255, 255)):
    start_x, start_y = top_right_position
    flag_width, flag_height = cell_size // flag_size, cell_size // flag_size

    for y in range(flag_size):
        for x in range(flag_size):
            rect_x = start_x + x * flag_width
            rect_y = start_y + y * flag_height
            color = color1 if (x + y) % 2 == 0 else color2
            pygame.draw.rect(screen, color, (rect_x, rect_y, flag_width, flag_height))

def draw_grid(legal_moves, potential_moves, tile_potential_moves, opposite_position):
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            # Outline of the cell
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if no_legal_moves:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 200))  # Black overlay
                screen.blit(overlay, (0, 0))

                # Display the finish text
                moves_text_part1 = "YOU'RE STUCK! Press UNDO,"
                moves_surf_part1 = font.render(moves_text_part1, True, (255, 0, 0))
                moves_rect_part1 = moves_surf_part1.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - FONT_SIZE // 2 - 10))
                screen.blit(moves_surf_part1, moves_rect_part1)

                # The second part of the message (file name) on a new line
                moves_text_part2 = "Or Right Click To Try Again!"
                moves_surf_part2 = font.render(moves_text_part2, True, (255, 0, 0))
                moves_rect_part2 = moves_surf_part2.get_rect(
                    center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + FONT_SIZE // 2 - 5))
                screen.blit(moves_surf_part2, moves_rect_part2)

            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)  # Default border color

            if (x, y) in potential_moves:
                # Determine the shade of grey based on depth
                depth = potential_moves[(x, y)]
                shade = 255 - (depth * 40)  # Decrease shade by 40 for each depth level, adjust as necessary
                pygame.draw.rect(screen, (shade, shade, shade), rect)

            if (x, y) in tile_potential_moves and (x, y) != (GRID_SIZE - 1, 0):
                # Determine the shade of grey based on depth
                depth = tile_potential_moves[(x, y)]
                shade = 255 - (depth * 40)  # Decrease shade by 40 for each depth level, adjust as necessary
                pygame.draw.rect(screen, (shade, shade, shade), rect)

            if (x, y) in potential_moves and (x, y) in tile_potential_moves:
                # Define a specific blue color for overlapping cells
                overlap_color = (0, 100, 100)  # This is a bright blue color
                pygame.draw.rect(screen, overlap_color, rect)

            # Check if this is the opposite cell and highlight it
            if (x, y) == opposite_position:
                pygame.draw.rect(screen, (230, 0, 250), rect, 4)  # Draw purple box with width 3

            # Choose the color based on the number of visits
            if visits[y][x] == 1:
                fill_color = (255, 255, 0)  # Yellow
            elif visits[y][x] == 2:
                fill_color = (255, 165, 0)  # Orange
            elif visits[y][x] >= 3:
                fill_color = (255, 0, 0)  # Red
            else:
                fill_color = (255, 255, 255)  # White (or any background color)

            # Fill the cell proportionally to the number of visits
            fill_height = CELL_SIZE * (visits[y][x] / 3)
            fill_rect = pygame.Rect(x * CELL_SIZE, (y + 1) * CELL_SIZE - fill_height, CELL_SIZE, fill_height)
            pygame.draw.rect(screen, fill_color, fill_rect)  # Fill with the chosen color

            # Draw the green box for legal moves, unless the cell is red
            if visits[y][x] < 3 and (x, y) in legal_moves:
                pygame.draw.rect(screen, (0, 255, 0), rect, 3)  # Green color for legal moves

            height_text = str(int(heights[y][x])) if heights[y][x].is_integer() else str(round((heights[y][x]), 2))

            # Render the altitude text
            alt_surf = font.render(height_text, True, (0, 0, 0))
            alt_rect = alt_surf.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
            screen.blit(alt_surf, alt_rect)


# Define the undo button rectangle and position
undo_button_rect = pygame.Rect(SCREEN_WIDTH - 100, SCREEN_HEIGHT - BOTTOM_MARGIN + 38, 90, 30)

# Knight's starting position
knight_pos = [0, 7, 0]  # x, y, height (z)
# Increment visit count for starting position
visits[knight_pos[1]][knight_pos[0]] += 1

# All possible 3D 'L' moves for the knight
knight_moves = [
    # Moves with 2 steps in the x direction
    (2, 1, 0), (2, -1, 0), (2, 0, 1), (2, 0, -1),
    (-2, 1, 0), (-2, -1, 0), (-2, 0, 1), (-2, 0, -1),

    # Moves with 2 steps in the y direction
    (1, 2, 0), (-1, 2, 0), (0, 2, 1), (0, 2, -1),
    (1, -2, 0), (-1, -2, 0), (0, -2, 1), (0, -2, -1),

    # Moves with 2 steps in the z (height) direction
    (1, 0, 2), (-1, 0, 2), (0, 1, 2), (0, -1, 2),
    (1, 0, -2), (-1, 0, -2), (0, 1, -2), (0, -1, -2),

    # Moves with 1 step in the x direction and 2 in the y
    (1, 2, 0), (1, -2, 0), (-1, 2, 0), (-1, -2, 0),

    # Moves with 1 step in the y direction and 2 in the x
    (2, 1, 0), (2, -1, 0), (-2, 1, 0), (-2, -1, 0),

    # Moves with 1 step in the x direction and 2 in the z
    (1, 0, 2), (1, 0, -2), (-1, 0, 2), (-1, 0, -2),

    # Moves with 1 step in the z direction and 2 in the x
    (2, 0, 1), (2, 0, -1), (-2, 0, 1), (-2, 0, -1),

    # Moves with 1 step in the y direction and 2 in the z
    (0, 1, 2), (0, 1, -2), (0, -1, 2), (0, -1, -2),

    # Moves with 1 step in the z direction and 2 in the y
    (0, 2, 1), (0, 2, -1), (0, -2, 1), (0, -2, -1),
]


def get_legal_moves(pos, moves):
    legal_moves = []
    for move in moves:
        new_x, new_y, new_z = pos[0] + move[0], pos[1] + move[1], pos[2] + move[2]
        # Check if the new position is within bounds, at the correct height, and not visited 3 times
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and visits[new_y][new_x] < 3:  # Exclude cells visited
            # 3 times
            if heights[new_y][new_x] == new_z:
                legal_moves.append((new_x, new_y))
    return legal_moves


# Function to move the knight
def move_knight(pos, move):
    new_pos = [pos[0] + move[0], pos[1] + move[1], pos[2] + move[2]]
    # Ensure the new position is within the grid bounds and the height is valid
    if 0 <= new_pos[0] < GRID_SIZE and 0 <= new_pos[1] < GRID_SIZE and heights[new_pos[1]][new_pos[0]] == new_pos[2]:
        return new_pos
    return pos  # Return the original position if the move is not valid


def log_move(time_waited, pos):
    # Convert grid coordinates to a format like 'a1', 'a2', ...
    col_letter = chr(ord('a') + pos[0])
    row_number = GRID_SIZE - pos[1]  # Assuming the bottom row should be 1
    position_format = f"{col_letter}{row_number}"

    # Log entry format
    log_entry = f"({time_waited},{position_format})\n"
    move_log.append(log_entry)
    # Write the log entry to a file
    with open("move_log.txt", "a") as log_file:
        log_file.write(log_entry)


# Function to draw the knight
def draw_knight(pos, legal_moves):
    if not no_legal_moves:
        # Calculate the screen position based on the grid coordinates
        screen_x = pos[0] * CELL_SIZE
        screen_y = pos[1] * CELL_SIZE

        # Define the color of the knight
        knight_color = (0, 0, 255)  # Blue color

        # Define the thickness of the knight border
        border_thickness = CELL_SIZE // 10

        # Create a pygame.Rect object for the knight's position
        knight_rect = pygame.Rect(screen_x, screen_y, CELL_SIZE, CELL_SIZE)

        # Draw the blue border around the cell
        pygame.draw.rect(screen, knight_color, knight_rect, border_thickness)


def count_tiles_at_knight_height(knight_height, heights, knight_pos):
    # Calculate the coordinates of the opposite tile
    opp_x = GRID_SIZE - 1 - knight_pos[0]
    opp_y = GRID_SIZE - 1 - knight_pos[1]

    # Check if the opposite tile has the same height as the knight's height
    is_opposite_same_height = heights[opp_y][opp_x] == knight_height

    # Count the tiles with the same height as the knight
    count = sum(1 for row in heights for height in row if height == knight_height)

    # Subtract 1 if the opposite tile is at the same height
    if is_opposite_same_height:
        count -= 1

    return count


def update_altitudes(current_pos, wait_time):
    x, y, current_altitude = current_pos

    # Find the opposite point
    opp_x = GRID_SIZE - 1 - x
    opp_y = GRID_SIZE - 1 - y
    opposite_altitude = heights[opp_y][opp_x]

    # Gather points to update, excluding the opposite point if it has the same initial altitude
    points_to_update = [(ix, iy) for iy, row in enumerate(heights) for ix, alt in enumerate(row)
                        if alt == current_altitude and not (ix == opp_x and iy == opp_y)]

    n = len(points_to_update)

    # Sinking the lattice points with the same altitude
    for point in points_to_update:
        heights[point[1]][point[0]] -= wait_time / n

    # Rising the opposite lattice point if it's not at the same altitude
    if current_altitude != opposite_altitude:
        heights[opp_y][opp_x] += wait_time / n

    return heights


def get_potential_moves(pos, moves, heights, visits, depth=5, current_depth=0):
    if current_depth == depth:
        return {}

    potential_moves = {}
    for move in moves:
        new_x, new_y, new_z = pos[0] + move[0], pos[1] + move[1], pos[2] + move[2]
        # Check if the new position is within bounds and not visited 3 times
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and visits[new_y][new_x] < 3:
            if heights[new_y][new_x] == new_z:
                potential_moves[(new_x, new_y)] = current_depth + 1
                # Recursively get moves from the new position
                deeper_moves = get_potential_moves([new_x, new_y, new_z], moves, heights, visits, depth,
                                                   current_depth + 1)
                # Merge the dictionaries, keeping the smallest depth value
                for move, move_depth in deeper_moves.items():
                    if move not in potential_moves or move_depth < potential_moves[move]:
                        potential_moves[move] = move_depth
    return potential_moves

def get_potential_moves_from_tile(start_tile, moves, heights, visits, depth=5, current_depth=0):
    if current_depth == depth:
        return {}

    potential_moves_from_tile = {}
    for move in moves:
        new_x, new_y, new_z = start_tile[0] + move[0], start_tile[1] + move[1], start_tile[2] + move[2]
        # Check if the new position is within bounds and not visited 3 times
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and visits[new_y][new_x] < 3:
            if heights[new_y][new_x] == new_z:
                potential_moves_from_tile[(new_x, new_y)] = current_depth + 1
                # Recursively get moves from the new position
                deeper_moves = get_potential_moves_from_tile([new_x, new_y, new_z], moves, heights, visits, depth,
                                                   current_depth + 1)
                # Merge the dictionaries, keeping the smallest depth value
                for move, move_depth in deeper_moves.items():
                    if move not in potential_moves_from_tile or move_depth < potential_moves_from_tile[move]:
                        potential_moves_from_tile[move] = move_depth
    return potential_moves_from_tile

def reset_heights():
    # This will create a deep copy of the initial heights
    return [[9.0, 8.0, 10.0, 12.0, 11.0, 8.0, 10.0, 17.0],
            [7.0, 9.0, 11.0, 9.0, 10.0, 12.0, 14.0, 12.0],
            [4.0, 7.0, 5.0, 8.0, 6.0, 13.0, 10.0, 15.0],
            [4.0, 10.0, 7.0, 9.0, 6.0, 8.0, 7.0, 9.0],
            [2.0, 6.0, 4.0, 5.0, 9.0, 8.0, 11.0, 13.0],
            [0.0, 3.0, 1.0, 4.0, 2.0, 7.0, 10.0, 7.0],
            [1.0, 2.0, 0.0, 1.0, 2.0, 5.0, 7.0, 6.0],
            [0.0, 2.0, 4.0, 3.0, 5.0, 6.0, 2.0, 4.0]
            ]


# Initialize an empty list to store game states
undo_stack = []


# Function to save the current game state
def save_state(knight_pos, visits, heights, total_wait_time, legal_moves, potential_moves, potential_moves_from_tile):
    state = {
        'knight_pos': knight_pos.copy(),
        'visits': [row[:] for row in visits],
        'heights': [row[:] for row in heights],
        'total_wait_time': total_wait_time,
        'legal_moves': legal_moves.copy(),
        'potential_moves': potential_moves.copy(),
        'potential_moves_from_tile': potential_moves_from_tile.copy()
    }
    undo_stack.append(state)

def display_finish_screen(total_wait_time):
    # Cover the screen with a semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))  # Black overlay
    screen.blit(overlay, (0, 0))

    # Display the finish text
    finish_text = "Congratulations! You've won!"
    finish_surf = font.render(finish_text, True, (255, 215, 0))  # Gold color text
    finish_rect = finish_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
    screen.blit(finish_surf, finish_rect)

    # Display the total wait time
    time_text = f"Total Wait Time: {total_wait_time}"
    time_surf = font.render(time_text, True, (255, 255, 255))
    time_rect = time_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(time_surf, time_rect)

    moves_text_part1 = "Winning moves are saved in"
    moves_surf_part1 = font.render(moves_text_part1, True, (255, 255, 255))
    moves_rect_part1 = moves_surf_part1.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - FONT_SIZE // 2 - 5))
    screen.blit(moves_surf_part1, moves_rect_part1)

    # The second part of the message (file name) on a new line
    moves_text_part2 = "'Winning Moves.txt'"
    moves_surf_part2 = font.render(moves_text_part2, True, (255, 255, 255))
    moves_rect_part2 = moves_surf_part2.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + FONT_SIZE // 2 - 5))
    screen.blit(moves_surf_part2, moves_rect_part2)

    # Update the display
    pygame.display.flip()

    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting_for_input = False
                return False  # Return False as soon as the screen is clicked

    return True  # Return True if the screen was not clicked (this line might not be reached due to sys.exit())

def save_win_log():
    with open("Winning Moves.txt", "w") as win_file:
        for entry in move_log:
            win_file.write(entry)

# Function to undo to the last saved state
def undo():
    if len(undo_stack) >= 2:
        undo_stack.pop()

    if undo_stack:
        state = undo_stack.pop()
        if move_log:
            move_log.pop()
        with open("move_log.txt", "w") as log_file:
            log_file.writelines(move_log)

        # Restore the previous state, including potential_moves_from_tile
        return state
    else:
        return None


# Game loop
 # Clear the move log file as well
with open("move_log.txt", "w") as log_file:
    log_file.write("")
show_finish_screen = False
running = True
input_active = True
input_text = ''
wait_time = 0
cursor_visible = True  # Cursor starts as visible
last_toggle_time = 0
toggle_interval = 500  # Time in milliseconds (500ms = 0.5 seconds)
legal_moves = get_legal_moves(knight_pos, knight_moves)
altitude_update_needed = False
total_wait_time = 0
no_legal_moves = False  # Add this before the game loop
# Calculate all potential moves from the knight up to X jumps
potential_moves = get_potential_moves(knight_pos, knight_moves, heights, visits)
start_tile = [7, 0, heights[0][7]]  # Assuming the height at 7,0 is required
potential_moves_from_tile = get_potential_moves_from_tile(start_tile, knight_moves, heights, visits)


while running:
    # Calculate the opposite position of the knight
    opposite_pos_x = GRID_SIZE - 1 - knight_pos[0]
    opposite_pos_y = GRID_SIZE - 1 - knight_pos[1]
    opposite_position = (opposite_pos_x, opposite_pos_y)

    current_time = pygame.time.get_ticks()
    if current_time - last_toggle_time > toggle_interval:
        cursor_visible = not cursor_visible
        last_toggle_time = current_time

    # Draw everything
    screen.fill((255, 255, 255))  # Clear the screen with the background color

    top_right_grid_position = (SCREEN_WIDTH - CELL_SIZE, 0)  # This is the pixel position of the top-right grid tile

    draw_checkered_flag(screen, top_right_grid_position, CELL_SIZE)

    # Pass the potential_moves to draw_grid
    # Example of calling draw_grid in your main loop
    draw_grid(legal_moves, potential_moves, potential_moves_from_tile, opposite_position)

    draw_knight(knight_pos, legal_moves)  # Draw the knight at the new position

    total_wait_time_surf = font.render('Total Wait Time: ' + str(total_wait_time), True, (0, 0, 0))
    total_wait_time_rect = total_wait_time_surf.get_rect(bottomright=(SCREEN_WIDTH - 10, SCREEN_HEIGHT - 42))
    screen.blit(total_wait_time_surf, total_wait_time_rect)


    if input_active:
        # Assuming knight_pos[2] holds the current height of the knight
        knight_current_height = heights[knight_pos[1]][knight_pos[0]]
        similar_tile_height = str(int(heights[knight_pos[1]][knight_pos[0]])) if heights[knight_pos[1]][
            knight_pos[0]].is_integer() else str(float(round(heights[knight_pos[1]][knight_pos[0]], 2)))
        same_height_count = count_tiles_at_knight_height(knight_current_height, heights, knight_pos)
        text_surf = font.render('Time To Wait?: ' + input_text, True, (0, 0, 0))

        base_text = 'Time To Wait?: ' + input_text
        if cursor_visible:
            base_text += "_"
        text_surf = font.render(base_text, True, (0, 0, 0))

        # Draw the undo button
        pygame.draw.rect(screen, (0, 0, 0), undo_button_rect)  # Draw the button as a black rectangle
        undo_text = font.render('UNDO', True, (255, 255, 255))  # Create the text (white)
        undo_text_rect = undo_text.get_rect(center=undo_button_rect.center)
        screen.blit(undo_text, undo_text_rect)  # Blit the text onto the screen at the button's position

        # Render the text for the number of tiles at the knight's height
        same_height_text = f"Tiles = Knight's Height ({similar_tile_height}) : {same_height_count}"
        same_height_surf = font.render(same_height_text, True, (0, 0, 0))
        same_height_rect = same_height_surf.get_rect(
            topleft=(10, GRID_HEIGHT + (BOTTOM_MARGIN - FONT_SIZE) // 2 + 15))
        screen.blit(same_height_surf, same_height_rect)
        screen.blit(text_surf, (10, GRID_HEIGHT + (BOTTOM_MARGIN - FONT_SIZE) // 2 - 20))

    pygame.display.flip()  # Update the full display Surface to the screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 1 is the left mouse button
            if undo_button_rect.collidepoint(event.pos):
                # Undo button has been clicked
                previous_state = undo()
                if previous_state:
                    # Restore the previous state
                    knight_pos = previous_state['knight_pos']
                    visits = previous_state['visits']
                    heights = previous_state['heights']
                    total_wait_time = previous_state['total_wait_time']
                    legal_moves = previous_state['legal_moves']
                    potential_moves = previous_state['potential_moves']
                    potential_moves_from_tile = previous_state['potential_moves_from_tile']
                    no_legal_moves = False

        if not input_active and event.type == pygame.MOUSEBUTTONDOWN:
            # Get the mouse position
            mouse_pos = event.pos

            # Calculate the clicked grid coordinates
            clicked_x = mouse_pos[0] // CELL_SIZE
            clicked_y = mouse_pos[1] // CELL_SIZE

            # Check if the clicked cell is a legal move
            if (clicked_x, clicked_y) in legal_moves:
                save_state(knight_pos, visits, heights, total_wait_time, legal_moves, potential_moves,
                           potential_moves_from_tile)
                # Move the knight to the clicked cell
                knight_pos = move_knight(knight_pos, (
                    clicked_x - knight_pos[0], clicked_y - knight_pos[1],
                    heights[clicked_y][clicked_x] - knight_pos[2]))
                # Increment the visit count
                # Inside your game loop, after the knight
                visits[knight_pos[1]][knight_pos[0]] += 1
                # Activate input mode for wait time after a move
                input_active = True
                altitude_update_needed = True
                log_move(wait_time, knight_pos)
            legal_moves = get_legal_moves(knight_pos, knight_moves)

            if knight_pos[0:2] == [7, 0] and not show_finish_screen:
                # Save the win log
                save_win_log()
                # Reset the game state
                heights = reset_heights()  # You'll need to implement a function to reset the heights
                visits = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
                knight_pos = [0, 7, 0]  # Reset to the starting position or any other default
                no_legal_moves = False  # Reset the flag
                # Recalculate legal moves
                visits[knight_pos[1]][knight_pos[0]] += 1
                input_active = True
                legal_moves = get_legal_moves(knight_pos, knight_moves)
                potential_moves = get_potential_moves(knight_pos, knight_moves, heights, visits)
                potential_moves_from_tile = get_potential_moves_from_tile(start_tile, knight_moves, heights, visits)
                # Set a flag to show the finish screen
                # Clear the undo stack and move log since we're starting over
                undo_stack.clear()
                move_log.clear()

                # Clear the move log file as well
                with open("move_log.txt", "w") as log_file:
                    log_file.write("")

                show_finish_screen = True

        elif input_active:
            # Handle wait time input
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    potential_moves = get_potential_moves(knight_pos, knight_moves, heights, visits)
                    legal_moves = get_legal_moves(knight_pos, knight_moves)
                    save_state(knight_pos, visits, heights, total_wait_time, legal_moves, potential_moves,
                               potential_moves_from_tile)
                    if input_text.isdigit():
                        wait_time = min(max(int(input_text), 0), 100)
                        # Update the altitudes based on the wait time
                        total_wait_time += wait_time
                        update_altitudes(knight_pos, wait_time)
                        # Recalculate legal moves after the altitudes have been updated
                        # After updating altitudes and before recalculating legal moves
                        knight_pos[2] = heights[knight_pos[1]][knight_pos[0]]
                        legal_moves = get_legal_moves(knight_pos, knight_moves)
                        potential_moves = get_potential_moves(knight_pos, knight_moves, heights, visits)
                        potential_moves_from_tile = get_potential_moves_from_tile(start_tile, knight_moves, heights,
                                                                                  visits)
                    else:
                        wait_time = 0


                    # Reset for the next input
                    input_text = ''
                    input_active = False  # Deactivate input mode
                    if legal_moves:
                        no_legal_moves = False
                    if not legal_moves:
                        no_legal_moves = True
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

        if no_legal_moves:
            input_active = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3 and input_active == True and no_legal_moves:
            log_file_path = "move_log.txt"
            if knight_pos[0:2] != [7, 0]:
                    if os.path.exists(log_file_path):
                        os.remove(log_file_path)
            # Reset the game state
            heights = reset_heights()  # You'll need to implement a function to reset the heights
            visits = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            knight_pos = [0, 7, 0]  # Reset to the starting position or any other default
            no_legal_moves = False  # Reset the flag
            # Recalculate legal moves
            total_wait_time = 0
            visits[knight_pos[1]][knight_pos[0]] += 1
            input_active = True
            legal_moves = get_legal_moves(knight_pos, knight_moves)
            potential_moves = get_potential_moves(knight_pos, knight_moves, heights, visits)
            potential_moves_from_tile = get_potential_moves_from_tile(start_tile, knight_moves, heights, visits)
            if legal_moves:
                no_legal_moves = False
            # Clear the undo stack and move log since we're starting over
            undo_stack.clear()
            move_log.clear()

            # Clear the move log file as well
            with open("move_log.txt", "w") as log_file:
                log_file.write("")
            continue  # Skip processing other events

    # When the victory condition is met
        if show_finish_screen:
            show_finish_screen = display_finish_screen(total_wait_time)
            total_wait_time = 0

    # Cap the frame rate
    pygame.time.Clock().tick(60)

# Quit the game
pygame.quit()
sys.exit()
