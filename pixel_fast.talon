mode: user.pixel
tag: user.pixel_fast_mode
-
{user.directional}:
    user.move_on_grid(1, directional_1)
<number> {user.directional}:
    user.move_on_grid(number_1, directional_1)
{user.directional} {user.directional}:
    user.move_on_grid_2d(1, directional_1, 1, directional_2)
<number> {user.directional} {user.directional}:
    user.move_on_grid_2d(number, directional_1, number, directional_2)
<number> {user.directional} <number> {user.directional}:
    user.move_on_grid_2d(number_1, directional_1, number_2, directional_2)
testing:"fast mode is indeed on"