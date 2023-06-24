class Solution {
public:

    int solve(int x, int y, vector<vector<int>>& grid) {
        
        if (x == 0 || y == 0)
            return 1;
        
        if (grid[x][y] != -1)
            return grid[x][y];

        grid[x][y] = solve(x-1, y, grid) + solve(x, y-1, grid);
        
        return grid[x][y];
    }
    
    int uniquePaths(int m, int n) {

        vector<vector<int>> grid(m, vector<int>(n,-1));
        return solve(m-1, n-1, grid);
    }
};