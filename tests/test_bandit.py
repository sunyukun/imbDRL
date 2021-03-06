from datetime import datetime

import pytest
from imbDRL.train.bandit import TrainBandit
from tf_agents.environments import suite_gym
from tf_agents.environments.tf_py_environment import TFPyEnvironment


class TrainBanditChild(TrainBandit):
    """Child class of imbDRL.train.bandit.TrainBandit to overwrite abstract methods."""

    def collect_metrics(self):
        """Dummy implementation of abstract method for testing."""
        pass

    def evaluate(self):
        """Dummy implementation of abstract method for testing."""
        pass

    def save_model(self):
        """Dummy implementation of abstract method for testing."""
        pass

    @staticmethod
    def load_model(fp: str):
        """Dummy implementation of abstract method for testing."""
        pass


def test_TrainBandit(tmp_path):
    """Tests imbDRL.train.bandit.TrainBandit."""
    tmp_models = str(tmp_path / "test_model")  # No support for pathLib https://github.com/tensorflow/tensorflow/issues/37357
    tmp_logs = str(tmp_path / "test_log")

    model = TrainBanditChild(10, 0.001, 0.1, 5, model_dir=tmp_models, log_dir=tmp_logs)
    assert model.global_episode == 0
    assert model.epsilon_decay() == 1.0
    assert model.model_dir == tmp_models
    assert model.log_dir == tmp_logs
    assert not model.compiled

    NOW = datetime.now().strftime("%Y%m%d")  # yyyymmdd
    model = TrainBanditChild(10, 0.001, 0.1, 5)
    assert "./models/" + NOW in model.model_dir  # yyyymmdd in yyyymmdd_hhmmss
    assert "./logs/" + NOW in model.log_dir


def test_compile_model(tmp_path):
    """Tests imbDRL.train.bandit.TrainBandit.compile_model."""
    tmp_models = str(tmp_path / "test_model")  # No support for pathLib https://github.com/tensorflow/tensorflow/issues/37357
    tmp_logs = str(tmp_path / "test_log")

    model = TrainBanditChild(10, 0.001, 0.1, 5, model_dir=tmp_models, log_dir=tmp_logs)
    train_env = TFPyEnvironment(suite_gym.load("CartPole-v0"))

    with pytest.raises(TypeError) as exc:
        model.compile_model(train_env, 128, None, None)
    assert "must be tuple or None" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        model.compile_model(train_env, None, 128, None)
    assert "must be tuple or None" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        model.compile_model(train_env, None, None, 128)
    assert "must be tuple or None" in str(exc.value)

    model = TrainBanditChild(10, 0.001, 0.1, 5, model_dir=tmp_models, log_dir=tmp_logs)
    assert not model.compiled
    model.compile_model(train_env, None, (128,), None)
    assert model.compiled


def test_train(tmp_path):
    """Tests imbDRL.train.bandit.TrainBandit.train."""
    tmp_models = str(tmp_path / "test_model")  # No support for pathLib https://github.com/tensorflow/tensorflow/issues/37357
    tmp_logs = str(tmp_path / "test_log")

    model = TrainBanditChild(10, 0.001, 0.1, 5, model_dir=tmp_models, log_dir=tmp_logs, val_every=2, log_every=2)
    train_env = TFPyEnvironment(suite_gym.load("CartPole-v0"))

    with pytest.raises(Exception) as exc:
        model.train()
    assert "must be compiled" in str(exc.value)

    model.compile_model(train_env, None, (128,), None)
    model.train()
    assert model.global_episode == 10
    assert model.epsilon_decay() == 0.1
