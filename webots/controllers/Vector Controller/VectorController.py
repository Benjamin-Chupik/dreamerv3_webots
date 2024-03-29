from controller import Robot, DistanceSensor, Motor, Supervisor
from controller import Camera

import matplotlib.pyplot as plt
import numpy as np

# time in [ms] of a simulation step

# setting camera up
# feedback loop: step simulation until receiving an exit event

import gym
from gym import spaces
from gym.utils import seeding
import numpy as np

# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------

class PendulumEnv(gym.Env):
    metadata = {"render.modes": ["human", "rgb_array"], "video.frames_per_second": 30}

    def __init__(self):
        # INITIALIZING ROBOT
        self.timestep = 500
        self.maxspeed = 6.28

        # create the Robot instance.
        self.robot = Robot()
        self.camera = Camera('camera')
        self.camera.enable(self.timestep)

        # Supervisor setup
        self.supervisor = Supervisor()
        self.robot_node = self.supervisor.getFromDef("_BEEPY_")
        self.box_node = self.supervisor.getFromDef("BOXY")

        self.box_pos = self.box_node.getField("translation")
        self.trans_field = self.robot_node.getField("translation")
        self.rot_field = self.robot_node.getField("rotation")


        print(self.robot_node)
        # initialize devices
        self.ps = []
        self.psNames = [
            'ps0', 'ps1', 'ps2', 'ps3',
            'ps4', 'ps5', 'ps6', 'ps7'
        ]

        for i in range(8):
            self.ps.append(self.robot.getDevice(self.psNames[i]))
            self.ps[i].enable(self.timestep)

        self.leftMotor = self.robot.getDevice('left wheel motor')
        self.rightMotor = self.robot.getDevice('right wheel motor')
        self.leftMotor.setPosition(float('inf'))
        self.rightMotor.setPosition(float('inf'))
        self.leftMotor.setVelocity(0.0)
        self.rightMotor.setVelocity(0.0)


        # SPACEY
        self.action_space = spaces.Box(low=-1, high=1,  shape=(2,), dtype=np.float32)
        self.observation_space = spaces.Box(low=0, high=1000,  shape=(8,), dtype=np.float32)
        self.seed()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, u):
        ## SNEAKY WEBOTS STEP

        self.robot.step(self.timestep)
        self.timespent += self.timestep
        print(self.timespent)
        
        # write actuators inputs
        self.leftMotor.setVelocity(u[0] * self.maxspeed)
        self.rightMotor.setVelocity(u[1] * self.maxspeed)

        done = False
        if self.timespent > 1e4: # time in ms
            done = True

        return self._get_obs(), np.sum(self._get_obs())**2/1e7, done, {}

    def reset(self):
        # set sensor values to 0
        self.psValues = np.zeros((8,), dtype=np.float32)
        self.timespent = 0

        randpos = np.zeros(3)
        randpos[:2] = np.random.random(2)-0.5
        randpos[2] = 0.05

        self.box_pos.setSFVec3f(list(randpos))

        # reset robot position and rotation
        self.trans_field.setSFVec3f([0,0,0])
        self.rot_field.setSFRotation([1,0,0,0])
        self.robot_node.resetPhysics()
        
        return self._get_obs()

    def _get_obs(self):
        self.psValues = []
        for i in range(8):
            self.psValues.append(self.ps[i].getValue())
        self.psValues = np.asarray(self.psValues, dtype=np.float32)
        return self.psValues

    def render(self, mode="human"):
        pass

    def close(self):
        if self.viewer:
            self.viewer.close()
            self.viewer = None

################################# DREAMER TIME ################################


import warnings
import dreamerv3
from dreamerv3 import embodied

warnings.filterwarnings("ignore", ".*truncated to dtype int32.*")

# See configs.yaml for all options.
config = embodied.Config(dreamerv3.configs["defaults"])
config = config.update(dreamerv3.configs["medium"])
config = config.update(
    {
        "logdir": f"logdirtest",  # this was just changed to generate a new log dir every time for testing
        "run.train_ratio": 64,
        "run.log_every": 30,
        "batch_size": 16,
        "jax.prealloc": False,
        "encoder.mlp_keys": ".*",
        "decoder.mlp_keys": ".*",
        "encoder.cnn_keys": "$^",
        "decoder.cnn_keys": "$^",
        "jax.platform": "cpu",  # I don't have a gpu locally
    }
)
config = embodied.Flags(config).parse()

logdir = embodied.Path(config.logdir)
step = embodied.Counter()
logger = embodied.Logger(
    step,
    [
        embodied.logger.TerminalOutput(),
        embodied.logger.JSONLOutput(logdir, "metrics.jsonl"),
        embodied.logger.TensorBoardOutput(logdir),
        # embodied.logger.WandBOutput(logdir.name, config),
        # embodied.logger.MLFlowOutput(logdir.name),
    ],
)


import gym
from embodied.envs import from_gym

env = PendulumEnv() # 
env = from_gym.FromGym(
    env, obs_key="state_vec"
)  # I found I had to specify a different obs_key than the default of 'image'
env = dreamerv3.wrap_env(env, config)
env = embodied.BatchEnv([env], parallel=False)

print("here---------------------------------------------")
agent = dreamerv3.Agent(env.obs_space, env.act_space, step, config)
print("---------------------------------------------")
replay = embodied.replay.Uniform(
    config.batch_length, config.replay_size, logdir / "replay"
)
args = embodied.Config(
    **config.run,
    logdir=config.logdir,
    batch_steps=config.batch_size * config.batch_length,
)
embodied.run.train(agent, env, replay, logger, args)
