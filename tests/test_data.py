import imbDRL.data as data
import numpy as np
import pytest
from imbDRL.environments import ClassifyEnv
from tf_agents.environments.tf_py_environment import TFPyEnvironment
from tf_agents.policies.random_tf_policy import RandomTFPolicy
from tf_agents.replay_buffers.tf_uniform_replay_buffer import \
    TFUniformReplayBuffer
from tf_agents.trajectories import trajectory


def test_load_image():
    """Tests imbDRL.data.load_image."""
    # Empty `data_source`
    with pytest.raises(ValueError) as exc:
        data.load_image("")
    assert "No valid" in str(exc.value)

    # Integer `data_source`
    with pytest.raises(ValueError) as exc:
        data.load_image(1234)
    assert "No valid" in str(exc.value)

    # Non-existing `data_source`
    with pytest.raises(ValueError) as exc:
        data.load_image("credit")
    assert "No valid" in str(exc.value)

    image_data = data.load_image("mnist")
    assert [x.shape for x in image_data] == [(60000, 28, 28, 1), (60000, ), (10000, 28, 28, 1), (10000, )]
    assert [x.dtype for x in image_data] == ["float32", "int32", "float32", "int32"]

    image_data = data.load_image("famnist")
    assert [x.shape for x in image_data] == [(60000, 28, 28, 1), (60000, ), (10000, 28, 28, 1), (10000, )]
    assert [x.dtype for x in image_data] == ["float32", "int32", "float32", "int32"]

    image_data = data.load_image("cifar10")
    assert [x.shape for x in image_data] == [(50000, 32, 32, 3), (50000, ), (10000, 32, 32, 3), (10000, )]
    assert [x.dtype for x in image_data] == ["float32", "int32", "float32", "int32"]


def test_load_imdb():
    """Tests imbDRL.data.load_imdb."""
    # Integer `config`
    with pytest.raises(TypeError) as exc:
        data.load_imdb(config=500)
    assert "is no valid datatype" in str(exc.value)

    # Wrong tuple length `config`
    with pytest.raises(ValueError) as exc:
        data.load_imdb(config=(100, 100, 100))
    assert "must be 2" in str(exc.value)

    # Negative `config`
    with pytest.raises(ValueError) as exc:
        data.load_imdb(config=(-100, 10))
    assert "must be > 0" in str(exc.value)

    # Negative `config`
    with pytest.raises(ValueError) as exc:
        data.load_imdb(config=(100, -10))
    assert "must be > 0" in str(exc.value)

    imdb_data = data.load_imdb()
    assert [x.shape for x in imdb_data] == [(25000, 500), (25000, ), (25000, 500), (25000, )]
    assert [x.dtype for x in imdb_data] == ["int32", "int32", "int32", "int32"]


def test_load_creditcard(tmp_path):
    """Tests imbDRL.data.load_creditcard."""
    cols = "Time,V1,V2,V3,V4,V5,V6,V7,V8,V9,V10,V11,V12,V13,V14,V15,V16,V17,V18,V19,V20,V21,V22,V23,V24,V25,V26,V27,V28,Amount,Class\n"
    row1 = str(list(range(0, 31))).strip("[]") + "\n"
    row2 = str(list(range(31, 62))).strip("[]") + "\n"
    row3 = str(list(range(62, 93))).strip("[]") + "\n"

    with pytest.raises(FileNotFoundError) as exc:
        data.load_creditcard(fp_train=tmp_path / "thisfiledoesnotexist.csv")
    assert "fp_train" in str(exc.value)

    with open(data_file := tmp_path / "data_file.csv", "w") as f:
        f.writelines([cols, row1, row2, row3])

    with pytest.raises(FileNotFoundError) as exc:
        data.load_creditcard(fp_train=data_file, fp_test=tmp_path / "thisfiledoesnotexist.csv")
    assert "fp_test" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        data.load_creditcard(fp_train=data_file, fp_test=data_file, normalization=1234)
    assert "must be of type `bool`" in str(exc.value)

    credit_data = data.load_creditcard(fp_train=data_file, fp_test=data_file)
    assert [x.shape for x in credit_data] == [(3, 29), (3, ), (3, 29), (3, )]
    assert [x.dtype for x in credit_data] == ["float32", "int32", "float32", "int32"]
    assert np.array_equal(credit_data[0][0], np.arange(1, 30, dtype=np.float32))  # No normalization
    assert np.array_equal(credit_data[0][1], np.arange(32, 61, dtype=np.float32))
    assert np.array_equal(credit_data[0][2], np.arange(63, 92, dtype=np.float32))

    credit_data = data.load_creditcard(fp_train=data_file, fp_test=data_file, normalization=True)
    assert [x.shape for x in credit_data] == [(3, 29), (3, ), (3, 29), (3, )]
    assert [x.dtype for x in credit_data] == ["float32", "int32", "float32", "int32"]
    assert np.array_equal(credit_data[0][0], np.zeros(29, dtype=np.float32))  # Min value
    assert np.array_equal(credit_data[0][1], np.full(29, 0.5, dtype=np.float32))  # Halfway
    assert np.array_equal(credit_data[0][2], np.ones(29, dtype=np.float32))  # Max value


def test_get_train_test_val(capsys):
    """Tests imbDRL.data.get_train_test_val."""
    X = np.array([[1, 2], [3, 4], [5, 6], [7, 8]])
    y = np.array([1, 0, 0, 0])

    with pytest.raises(ValueError) as exc:
        data.get_train_test_val(X, y, X, y, 0.2, [0], [1, 2], val_frac=0.0)
    assert "not in interval" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        data.get_train_test_val(X, y, X, y, 0.2, [0], [1, 2], val_frac=1)
    assert "not in interval" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        data.get_train_test_val(X, y, X, y, 0.2, [0], [1, 2], print_stats=1234)
    assert "must be of type" in str(exc.value)

    X_train, y_train, X_test, y_test, X_val, y_val = data.get_train_test_val(X, y, X, y, 0.25, [1], [0], print_stats=False)
    assert X_train.shape == (2, 2)
    assert X_test.shape == (3, 2)
    assert X_val.shape == (1, 2)
    assert y_train.shape == (2, )
    assert y_test.shape == (3, )
    assert y_val.shape == (1, )

    data.get_train_test_val(X, y, X, y, 0.25, [1], [0], print_stats=True)  # Check if printing
    captured = capsys.readouterr()
    assert captured.out == ("Imbalance ratio `p`:\n"
                            "\ttrain:      n=0, p=0.000000\n"
                            "\ttest:       n=0, p=0.000000\n"
                            "\tvalidation: n=0, p=0.000000\n")

    data.get_train_test_val(X, y, X, y, 0.25, [1], [0], print_stats=False)  # Check if not printing
    captured = capsys.readouterr()
    assert captured.out == ""


def test_imbalance_data():
    """Tests imbDRL.data.imbalance_data."""
    X = [7, 7, 7, 8, 8, 8]
    y = [2, 2, 2, 3, 3, 3]

    with pytest.raises(TypeError) as exc:
        data.imbalance_data(X, np.array(y), 0.5, [2], [3])
    assert "`X` must be of type" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        data.imbalance_data(np.array(X), y, 0.5, [2], [3])
    assert "`y` must be of type" in str(exc.value)

    X = np.array(X)
    y = np.array(y)

    with pytest.raises(ValueError) as exc:
        data.imbalance_data(X, y, 0.0, [2], [3])
    assert "not in interval" in str(exc.value)

    with pytest.raises(ValueError) as exc:
        data.imbalance_data(X, y, 1, [2], [3])
    assert "not in interval" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        data.imbalance_data(X, y, 0.5, 2, [3])
    assert "`min_class` must be of type list or tuple" in str(exc.value)

    with pytest.raises(TypeError) as exc:
        data.imbalance_data(X, y, 0.5, [2], 3)
    assert "`maj_class` must be of type list or tuple" in str(exc.value)

    X = np.arange(10)
    y = np.arange(11)

    with pytest.raises(ValueError) as exc:
        data.imbalance_data(X, y, 0.2, [1], [0])
    assert "must contain the same amount of rows" in str(exc.value)

    X = np.arange(100)
    y = np.concatenate([np.ones(50), np.zeros(50)])
    X, y = data.imbalance_data(X, y, 0.2, [1], [0])
    assert [(60, ), (60, ), 10] == [X.shape, y.shape, y.sum()]  # 50/50 is original imb_rate, 10/50(=0.2) is new imb_rate


def test_collect_step():
    """Tests imbDRL.data.collect_step."""
    X = np.arange(10, dtype=np.float32)
    y = np.ones(10, dtype=np.int32)  # All labels are positive

    env = TFPyEnvironment(ClassifyEnv(X, y, 0.2))
    policy = RandomTFPolicy(env.time_step_spec(), env.action_spec())
    trajectory_spec = trajectory.from_transition(env.time_step_spec(), policy.policy_step_spec, env.time_step_spec())
    buffer = TFUniformReplayBuffer(data_spec=trajectory_spec,
                                   batch_size=1,
                                   max_length=10)

    assert buffer.num_frames() == 0
    data.collect_step(env, policy, buffer)
    assert buffer.num_frames() == 1

    data.collect_step(env, policy, buffer)
    assert buffer.num_frames() == 2

    ds = buffer.as_dataset(single_deterministic_pass=True)
    for i in ds.as_numpy_iterator():
        assert i[0].observation in X
        assert i[0].action in (0, 1)


def test_collect_data():
    """Tests imbDRL.data.collect_data."""
    X = np.arange(10, dtype=np.float32)
    y = np.ones(10, dtype=np.int32)  # All labels are positive

    env = TFPyEnvironment(ClassifyEnv(X, y, 0.2))
    policy = RandomTFPolicy(env.time_step_spec(), env.action_spec())
    trajectory_spec = trajectory.from_transition(env.time_step_spec(), policy.policy_step_spec, env.time_step_spec())
    buffer = TFUniformReplayBuffer(data_spec=trajectory_spec,
                                   batch_size=1,
                                   max_length=10)

    assert buffer.num_frames() == 0
    data.collect_data(env, policy, buffer, 1)
    assert buffer.num_frames() == 1

    data.collect_data(env, policy, buffer, 3, logging=True)
    assert buffer.num_frames() == 4

    data.collect_data(env, policy, buffer, 12)
    assert buffer.num_frames() == 10
