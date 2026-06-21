"""GUI-independent tests for the SDK interactive session."""

from cops_and_robbers_rl.main import build_parser
from cops_and_robbers_rl.sdk.sdk import CopsAndRobbersSDK


def test_gui_demo_flag_is_exposed_by_cli() -> None:
    args = build_parser().parse_args(["gui", "--demo"])

    assert args.command == "gui"
    assert args.demo is True


def test_interactive_session_starts_with_renderable_default_board() -> None:
    snapshot = CopsAndRobbersSDK.from_config().create_interactive_session().snapshot

    assert snapshot.grid_size == (5, 5)
    assert snapshot.sub_game_id == 1
    assert snapshot.moves_completed == 0
    assert snapshot.cop_position != snapshot.thief_position
    assert not snapshot.terminal


def test_interactive_step_and_sub_game_use_sdk_state() -> None:
    session = CopsAndRobbersSDK.from_config().create_interactive_session()

    stepped = session.step()
    finished = session.run_sub_game()

    assert stepped.moves_completed == 1
    assert finished.terminal
    assert finished.winner is not None
    assert finished.sub_game_score.cop > 0
    assert finished.sub_game_score.thief > 0
    assert finished.match_score == finished.sub_game_score


def test_interactive_full_match_runs_six_games_and_reset_clears_scores() -> None:
    session = CopsAndRobbersSDK.from_config().create_interactive_session()

    finished = session.run_full_match()
    reset = session.reset()

    assert finished.sub_game_id == 6
    assert finished.terminal
    assert finished.full_match_complete
    assert finished.match_score.cop >= 6 * 5
    assert finished.match_score.thief >= 6 * 5
    assert reset.sub_game_id == 1
    assert reset.match_score.cop == reset.match_score.thief == 0
    assert not reset.full_match_complete


def test_interactive_match_can_advance_one_animation_frame_at_a_time() -> None:
    session = CopsAndRobbersSDK.from_config().create_interactive_session()

    frames = [session.snapshot]
    while not frames[-1].full_match_complete:
        frames.append(session.advance_match())

    assert len(frames) > 6
    assert {frame.sub_game_id for frame in frames} == set(range(1, 7))
    assert frames[-1].match_score.cop >= 30
    assert frames[-1].match_score.thief >= 30
