def main():
    import warnings
    import dreamerv3
    from dreamerv3 import embodied
    import numpy as np
    from time import sleep

    warnings.filterwarnings("ignore", ".*truncated to dtype int32.*")

    # See configs.yaml for all options.
    config = embodied.Config(dreamerv3.configs["defaults"])
    config = config.update(dreamerv3.configs["medium"])
    config = config.update(
        {
<<<<<<< Updated upstream:danijar_CodeBase/basicGymTesting/gymInteractionTest.py
            "logdir": f"basicGymTesting/logdir/LunarLanderGPU",  # this was just changed to generate a new log dir every time for testing
=======
            "logdir": f"logdir/pendulum",  # this was just changed to generate a new log dir every time for testing
>>>>>>> Stashed changes:basicGymTesting/gymInteractionTest.py
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
            embodied.logger.JSONLOutput(logdir, "LunarLander-v2"),
            embodied.logger.TensorBoardOutput(logdir),
            # embodied.logger.WandBOutput(logdir.name, config),
            # embodied.logger.MLFlowOutput(logdir.name),
        ],
    )

    # import crafter
    import gym
    from embodied.envs import from_gym

    # env = crafter.Env()  # Replace this with your Gym env.
<<<<<<< Updated upstream:danijar_CodeBase/basicGymTesting/gymInteractionTest.py
    env = gym.make("LunarLander-v2")  # this needs box2d-py installed also
=======
    env = gym.make("Pendulum-v1")  # this needs box2d-py installed also
>>>>>>> Stashed changes:basicGymTesting/gymInteractionTest.py
    env = from_gym.FromGym(
        env, obs_key="state_vec"
    )  # I found I had to specify a different obs_key than the default of 'image' or 'state_vec'
    env = dreamerv3.wrap_env(env, config)
    env = embodied.BatchEnv([env], parallel=False)
    agent = dreamerv3.Agent(env.obs_space, env.act_space, step, config)
    replay = embodied.replay.Uniform(
        config.batch_length, config.replay_size, logdir / "replay"
    )
    args = embodied.Config(
        **config.run,
        logdir=config.logdir,
        batch_steps=config.batch_size * config.batch_length,
    )
    # embodied.run.train(agent, env, replay, logger, args)
    # embodied.run.eval_only(agent, env, logger, args)

    # Testing part
    checkpoint = embodied.Checkpoint()
    checkpoint.agent = agent
    checkpoint.load(logdir / "checkpoint.ckpt", keys=["agent"])

    # -----------------------display stuff all from either embodied.core.driver or embodied.run.train

    from dreamerv3.embodied import convert

    # Reset env
    acts = {
        k: convert(np.zeros((len(env),) + v.shape, v.dtype))
        for k, v in env.act_space.items()
    }
    acts["reset"] = np.ones(len(env), bool)
    state = None

    # get innitial action
    acts = {k: v for k, v in acts.items() if not k.startswith("log_")}

    done = False
    while not done:
        # get observation
        obs = env.step(acts)
        obs = {k: convert(v) for k, v in obs.items()}
        assert all(len(x) == len(env) for x in obs.values()), obs

        
        policy = lambda *args: agent.policy(*args, mode="eval")
        acts, state = policy(obs, state)

        # clean up actions
        acts = {k: convert(v) for k, v in acts.items()}
        if obs["is_last"].any():
            mask = 1 - obs["is_last"]
<<<<<<< Updated upstream:danijar_CodeBase/basicGymTesting/gymInteractionTest.py
            # acts = {k: v * _expand(mask, len(v.shape)) for k, v in acts.items()}
            acts = {k: v for k, v in acts.items() if not k.startswith("log_")}

        acts["reset"] = obs["is_last"].copy()

        print(acts)

        env.render()
        # sleep(0.1)
=======
            #acts = {k: v * _expand(mask, len(v.shape)) for k, v in acts.items()}
            acts = {k: v for k, v in acts.items() if not k.startswith("log_")}
        acts["reset"] = obs["is_last"].copy()

        # print(acts)
        env.render()
>>>>>>> Stashed changes:basicGymTesting/gymInteractionTest.py
        # done = env.done


def _expand(self, value, dims):
    # From embodied.core.driver
    while len(value.shape) < dims:
        value = value[..., None]
    return value


## -------------------------- end display stuff

if __name__ == "__main__":
    main()
