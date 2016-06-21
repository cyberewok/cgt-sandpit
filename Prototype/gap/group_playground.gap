get_gens := function (W, H, _w, _h)
    local w, h, grid, gens, gen, row, col, index;
    w := _w - 1;
    h := _h - 1;
    grid := [];
    for row in [0..H-1] do
        Add(grid, [row * W + 1..row*W + W]);
    od;
    gens := [];
    for row in [1..H-h] do
        for col in [1..W-w] do
            gen := [];
            #top row
            for index in [col..col + w - 1] do
                Add(gen, grid[row][index]);
            od;
            #right col
            for index in [row..row + h - 1] do
                Add(gen, grid[index][col + w]);
            od;
            #bottom row
            for index in [col + w, col + w - 1..col + 1] do
                Add(gen, grid[row+h][index]);
            od;
            #left col
            for index in [row + h, row + h - 1..row + 1] do
                Add(gen, grid[index][col]);
            od;
            Add(gens, gen);
        od;
    od;
    return gens;
end;

list_to_perm := function (l, size)
    local perm, rot;
    rot:= l{[2..d]}
    for 
end;