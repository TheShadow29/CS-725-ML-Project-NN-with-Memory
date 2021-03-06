import numpy as np

import gym
from gym import error, spaces, utils
from gym.utils import seeding
from gym_maze.envs.maze_view_2d import MazeView2D


class MazeEnv(gym.Env):
    metadata = {
        "render.modes": ["human", "rgb_array"],
    }

    ACTION = ["N", "W", "S", "E"]

    def __init__(self, maze_file=None, maze_size=None, mode=None, complex_maze=False):

        self.viewer = None

        if maze_file:
            self.maze_view = MazeView2D(maze_name="OpenAI Gym - Maze (%s)" % maze_file,
                                        maze_file_path=maze_file,
                                        screen_size=(640, 640), complex_maze=complex_maze)
        elif maze_size:
            if mode == "plus":
                has_loops = True
                num_portals = int(round(min(maze_size)/3))
            else:
                has_loops = False
                num_portals = 0

            self.maze_view = MazeView2D(maze_name="OpenAI Gym - Maze (%d x %d)" % maze_size,
                                        maze_size=maze_size, screen_size=(640, 640),
                                        has_loops=has_loops, num_portals=num_portals, complex_maze=complex_maze)
        else:
            raise AttributeError("One must supply either a maze_file path (str) or the maze_size (tuple of length 2)")

        self.maze_size = self.maze_view.maze_size

        # forward or backward in each dimension
        self.action_space = spaces.Discrete(2*len(self.maze_size))

        # observation is the x, y coordinate of the grid
        # low = np.zeros(len(self.maze_size), dtype=int)
        # high = np.array(self.maze_size, dtype=int) - np.ones(len(self.maze_size), dtype=int)
        low = np.zeros(33)
        high = np.ones(33)
        high[-1] = self.maze_size[1]
        high[-2] = self.maze_size[0]

        self.observation_space = spaces.Box(low, high)

        # initial condition
        self.state = None
        self.steps_beyond_done = None

        # Simulation related variables.
        self._seed()
        self.reset()

        # Just need to initialize the relevant attributes
        self._configure()

    def __del__(self):
        self.maze_view.quit_game()

    def _configure(self, display=None):
        self.display = display

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, action):
        if isinstance(action, int):
            self.maze_view.move_robot(self.ACTION[action])
        else:
            self.maze_view.move_robot(action)

        # if np.array_equal(self.maze_view.robot, self.maze_view.goal):
        #     reward = 1
        #     done = True
        # else:
        #     reward = -0.1/(self.maze_size[0]*self.maze_size[1])
        #     done = False

        # self.state = self.maze_view.robot
        self.obs_space = self.maze_view.obs_space()
        # See if red or yellow
        done = False
        reward = -0.1/(self.maze_size[0]*self.maze_size[1])
        if not self.key_seen:
            if self.obs_space[0] == 0:
                self.key_seen = True
                # if red then go to blue
                self.door = 1
                # reward = 0.5
            if self.obs_space[0] == 5:
                # if yellow go to green
                self.key_seen = True
                self.door = 2
                # reward = 0.5
        else:
            if self.obs_space[0] == self.door:
                reward = 2
                done = True
            if self.obs_space[0] == (3 - self.door):
                reward = 1
                done = True
        info = {}
        self.obs_space = np.eye(6)[self.obs_space]
        self.obs_space = self.obs_space.flatten()
        self.obs_space = np.append(self.obs_space, self.key_seen)
        self.obs_space = np.append(self.obs_space, self.maze_view.robot)
        # print(self.obs_space[0])
        # pdb.set_trace()
        return self.obs_space, reward, done, info

    def _reset(self):
        self.maze_view.reset_robot()
        self.state = np.zeros(2)
        self.steps_beyond_done = None
        self.done = False
        # self.door = 0
        self.key_seen = False
        self.obs_space = self.maze_view.obs_space()
        self.obs_space = np.eye(6)[self.obs_space]
        self.obs_space = self.obs_space.flatten()
        self.obs_space = np.append(self.obs_space, self.key_seen)
        self.obs_space = np.append(self.obs_space, self.maze_view.robot)
        # pdb.set_trace()
        return self.obs_space

    def is_game_over(self):
        return self.maze_view.game_over

    def _render(self, mode="human", close=False):
        if close:
            self.maze_view.quit_game()

        return self.maze_view.update(mode)


class MazeEnvTest(MazeEnv):
    def __init__(self):
        # super(MazeEnvTest, self).__init__(maze_file="maze2d_006.npy")
        # super(MazeEnvTest, self).__init__(maze_size=(5, 5))
        super(MazeEnvTest, self).__init__(maze_size=(5, 5))


class MazeEnv7x7Simple(MazeEnv):
    def __init__(self):
        super(MazeEnv7x7Simple, self).__init__(maze_size=(7, 7))


class MazeEnv7x7Complex(MazeEnv):
    def __init__(self):
        super(MazeEnv7x7Complex, self).__init__(maze_size=(7, 7), complex_maze=True)


class MazeEnvSample5x5(MazeEnv):

    def __init__(self):
        super(MazeEnvSample5x5, self).__init__(maze_file="maze2d_5x5.npy")


class MazeEnvRandom5x5(MazeEnv):

    def __init__(self):
        super(MazeEnvRandom5x5, self).__init__(maze_size=(5, 5))


class MazeEnvSample10x10(MazeEnv):

    def __init__(self):
        super(MazeEnvSample10x10, self).__init__(maze_file="maze2d_10x10.npy")


class MazeEnvRandom10x10(MazeEnv):

    def __init__(self):
        super(MazeEnvRandom10x10, self).__init__(maze_size=(10, 10))


class MazeEnvSample3x3(MazeEnv):

    def __init__(self):
        super(MazeEnvSample3x3, self).__init__(maze_file="maze2d_3x3.npy")


class MazeEnvRandom3x3(MazeEnv):

    def __init__(self):
        super(MazeEnvRandom3x3, self).__init__(maze_size=(3, 3))


class MazeEnvSample100x100(MazeEnv):

    def __init__(self):
        super(MazeEnvSample100x100, self).__init__(maze_file="maze2d_100x100.npy")


class MazeEnvRandom100x100(MazeEnv):

    def __init__(self):
        super(MazeEnvRandom100x100, self).__init__(maze_size=(100, 100))


class MazeEnvRandom10x10Plus(MazeEnv):

    def __init__(self):
        super(MazeEnvRandom10x10Plus, self).__init__(maze_size=(10, 10), mode="plus")


class MazeEnvRandom20x20Plus(MazeEnv):

    def __init__(self):
        super(MazeEnvRandom20x20Plus, self).__init__(maze_size=(20, 20), mode="plus")


class MazeEnvRandom30x30Plus(MazeEnv):
    def __init__(self):
        super(MazeEnvRandom30x30Plus, self).__init__(maze_size=(30, 30), mode="plus")
