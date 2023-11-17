from ray import tune
from ray.rllib.algorithms.dreamerv3.dreamerv3 import DreamerV3Config

import flappy_bird_gymnasium
import gymnasium
env = gymnasium.make("FlappyBird-v0", render_mode="human")



def _env_creator(ctx):
    import flappy_bird_gymnasium  # doctest: +SKIP
    import gymnasium as gym
    from supersuit.generic_wrappers import resize_v1
    from ray.rllib.algorithms.dreamerv3.utils.env_runner import NormalizedImageEnv

    return NormalizedImageEnv(
        resize_v1(  # resize to 64x64 and normalize images
            gym.make("FlappyBird-rgb", audio_on=False), x_size=64, y_size=64
        )
    )


# Register the FlappyBird-rgb-v0 env including necessary wrappers via the
# `tune.register_env()` API.
tune.register_env("env1", _env_creator)

# Define the `config` variable to use for training.
config = (
    DreamerV3Config()
    # set the env to the pre-registered string
    .environment("env1")
    # play around with the insanely high number of hyperparameters for DreamerV3 ;) 
    .training(
        model_size="S",
        training_ratio=1024,
    )
)


print("--------------------------------------------------------------------- Training!")
config.build()